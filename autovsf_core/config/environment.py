"""autovsf_core/config/environment.py — Workstation environment detector & path resolver."""

import os
import shutil
from pathlib import Path


class WorkstationEnvironment:
    """Detects system environment details (Colab Drive mount, X11/Xvfb, VSF paths)."""

    def __init__(self):
        self.is_colab = os.path.exists("/content")
        self.drive_mounted = os.path.exists("/content/drive/MyDrive")

        # Working Directory on Drive
        if self.drive_mounted:
            self.work_dir = Path("/content/drive/MyDrive/AutoVSF")
        else:
            self.work_dir = Path(os.path.expanduser("~")) / "AutoVSF"

        self.subtitles_dir = self.work_dir / "Subtitles"
        self.vsf_dir = self.work_dir / "VideoSubFinder"
        self.legacy_libs_dir = self.vsf_dir / "legacy_libs"

        # Ensure directories exist
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.subtitles_dir, exist_ok=True)

    def find_vsf_binary(self) -> str:
        """Find executable location of VideoSubFinderWXW binary or wrapper script."""
        candidates = [
            self.vsf_dir / "VideoSubFinderWXW.run",
            self.vsf_dir / "VideoSubFinderWXW",
            self.work_dir / "autovsf-colab" / "VideoSubFinder" / "VideoSubFinderWXW.run",
            Path("/mnt/d/DESKTOP/agy-vsf-colab-gui/VideoSubFinder/VideoSubFinderWXW.run"),
        ]

        for path in candidates:
            if path.exists():
                return str(path)

        # Fallback system PATH lookup
        sys_vsf = shutil.which("VideoSubFinderWXW")
        if sys_vsf:
            return sys_vsf

        return str(self.vsf_dir / "VideoSubFinderWXW.run")

    @property
    def has_display(self) -> bool:
        return "DISPLAY" in os.environ and bool(os.environ["DISPLAY"])


env = WorkstationEnvironment()
