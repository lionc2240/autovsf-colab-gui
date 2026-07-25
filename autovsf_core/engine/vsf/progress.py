"""autovsf_core/engine/vsf/progress.py — Watchdog observer for VideoSubFinder RGBImages progress."""

import os
import re
import time
import datetime
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class VSFImageWatcher(FileSystemEventHandler):
    """Observes RGBImages directory and computes real-time frame progress & ETA."""

    def __init__(self, video_duration_td: datetime.timedelta, callback: Callable[[int, float, str], None]):
        self.video_duration_td = video_duration_td
        self.callback = callback
        self.count = 0
        self.start_time = time.time()

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            return

        self.count += 1
        name = os.path.basename(event.src_path)

        match = re.search(r"(\d{1,2})_(\d{2})_(\d{2})_(\d+)", name)
        pct = 0.0
        eta_str = "--:--"

        if match and self.video_duration_td.total_seconds() > 0:
            try:
                cur_td = datetime.timedelta(
                    hours=int(match[1]),
                    minutes=int(match[2]),
                    seconds=int(match[3]),
                    microseconds=int(match[4][:6]),
                )
                pct = min(100.0, (cur_td.total_seconds() / self.video_duration_td.total_seconds()) * 100.0)

                elapsed_sec = time.time() - self.start_time
                if pct > 0:
                    est_total = elapsed_sec / (pct / 100.0)
                    eta_sec = max(0, est_total - elapsed_sec)
                    m, s = divmod(int(eta_sec), 60)
                    h, m = divmod(m, 60)
                    eta_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
            except Exception:
                pass

        if self.callback:
            self.callback(self.count, pct, eta_str)


class VSFProgressMonitor:
    """Manages Watchdog Observer lifecycle for VideoSubFinder output directory."""

    def __init__(self, rgb_images_dir: str, duration_sec: float, progress_cb: Callable[[int, float, str], None]):
        self.rgb_dir = rgb_images_dir
        self.duration_td = datetime.timedelta(seconds=int(duration_sec))
        self.progress_cb = progress_cb
        self.observer: Optional[Observer] = None

    def start(self) -> None:
        # Wait up to 15s for directory creation
        for _ in range(15):
            if os.path.exists(self.rgb_dir):
                break
            time.sleep(1)

        if not os.path.exists(self.rgb_dir):
            return

        self.observer = Observer()
        handler = VSFImageWatcher(self.duration_td, self.progress_cb)
        self.observer.schedule(handler, self.rgb_dir, recursive=False)
        self.observer.start()

    def stop(self) -> None:
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=2.0)
