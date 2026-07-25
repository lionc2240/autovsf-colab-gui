"""autovsf_core/engine/vsf/runner.py — VideoSubFinder process execution runner."""

import os
import re
try:
    import cv2
except ImportError:
    cv2 = None
import time
import psutil
import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional

from autovsf_core.domain.crop import CropProfile
from autovsf_core.config.environment import env
from autovsf_core.engine.vsf.progress import VSFProgressMonitor


def get_video_duration(video_path: str) -> float:
    """Retrieve video duration in seconds via OpenCV or ffprobe."""
    if cv2 is not None:
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 1
            frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            if frames > 0 and fps > 0:
                return float(frames / fps)
        except Exception:
            pass

    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(res.stdout.strip())
    except Exception:
        return 0.0


class VSFRunner:
    """Encapsulates executing VideoSubFinder binary and monitoring progress."""

    def __init__(self, vsf_binary_path: Optional[str] = None):
        self.vsf_binary = vsf_binary_path or env.find_vsf_binary()
        self.proc: Optional[subprocess.Popen] = None
        self._stop_requested = False

    def run(
        self,
        video_path: str,
        crop: CropProfile,
        output_dir: Optional[str] = None,
        progress_cb: Optional[Callable[[float, int, str], None]] = None,
    ) -> str:
        """Run VideoSubFinder on video_path with specified crop. Returns path to RGBImages directory."""
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        video_path = os.path.abspath(video_path)
        if not output_dir:
            output_dir = str(Path(video_path).parent / (Path(video_path).stem + "_out"))
        
        rgb_dir = os.path.join(output_dir, "RGBImages")
        os.makedirs(output_dir, exist_ok=True)

        duration = get_video_duration(video_path)

        # Prepare VSF command arguments
        cmd = [
            self.vsf_binary,
            "-c", "-r",
            "-i", video_path,
            "-o", output_dir,
            "-te", f"{crop.top:.4f}",
            "-be", f"{crop.bottom:.4f}",
            "-le", f"{crop.left:.4f}",
            "-re", f"{crop.right:.4f}"
        ]

        vsf_cwd = os.path.dirname(self.vsf_binary) or None

        def on_watcher_update(count: int, pct: float, eta_str: str):
            if progress_cb:
                progress_cb(pct, count, eta_str)

        monitor = VSFProgressMonitor(rgb_dir, duration, on_watcher_update)
        monitor.start()

        self._stop_requested = False
        try:
            # Ensure execution permission
            if os.path.exists(self.vsf_binary):
                os.chmod(self.vsf_binary, 0o755)

            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=vsf_cwd
            )

            progress_re = re.compile(r'(\d+)\s*%')

            for line in self.proc.stdout:
                if self._stop_requested:
                    break
                line_str = line.strip()
                match = progress_re.search(line_str)
                if match and progress_cb:
                    pct = float(match.group(1))
                    progress_cb(pct, 0, "")

            self.proc.wait()
        finally:
            monitor.stop()
            self.proc = None

        if self._stop_requested:
            raise InterruptedError("VideoSubFinder execution was cancelled by user.")

        return rgb_dir

    def stop(self) -> None:
        """Cancel & kill VideoSubFinder process tree."""
        self._stop_requested = True
        if self.proc and self.proc.poll() is None:
            try:
                parent = psutil.Process(self.proc.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, Exception):
                pass
