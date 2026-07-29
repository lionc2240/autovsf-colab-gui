"""autovsf_core/engine/youtube/downloader.py — YouTube Video Downloader via yt-dlp."""

import os
import subprocess
from pathlib import Path
from typing import Optional, Callable


class YouTubeDownloader:
    """Handles downloading YouTube videos with minimum 720p quality while preserving original video title."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or "/content/drive/MyDrive/AutoVSF/Videos"

    def download_video(
        self,
        youtube_url: str,
        min_height: int = 720,
        progress_cb: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Download YouTube video using yt-dlp preserving original title.

        Returns absolute path to downloaded video file.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        out_template = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        fmt = f"bestvideo[height>={min_height}]+bestaudio/best[height>={min_height}]/best"

        cmd = [
            "yt-dlp",
            "--no-playlist",
            "-f", fmt,
            "--merge-output-format", "mp4",
            "-o", out_template,
            "--get-filename",
            youtube_url.strip(),
        ]

        if progress_cb:
            progress_cb("Fetching video metadata and target filename...")

        try:
            filename_output = subprocess.check_output(cmd, text=True).strip().split("\n")[-1]
            if not filename_output.endswith(".mp4"):
                filename_output = str(Path(filename_output).with_suffix(".mp4"))
        except Exception:
            filename_output = os.path.join(self.output_dir, "downloaded_video.mp4")

        dl_cmd = [
            "yt-dlp",
            "--no-playlist",
            "-f", fmt,
            "--merge-output-format", "mp4",
            "-o", out_template,
            youtube_url.strip(),
        ]

        if progress_cb:
            progress_cb(f"Downloading YouTube video: {youtube_url}")

        subprocess.run(dl_cmd, check=True)

        if os.path.exists(filename_output):
            return filename_output

        # Fallback search for recently modified file in output_dir
        files = [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith(".mp4")]
        if files:
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return files[0]

        raise FileNotFoundError(f"Failed to locate downloaded video for URL: {youtube_url}")
