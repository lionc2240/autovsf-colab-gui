"""autovsf_core/engine/ocr/ocr_base.py — Abstract OCR Engine Base Interface."""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class BaseOCREngine(ABC):
    """Abstract interface for OCR engines generating SRT subtitle files from subtitle images."""

    @abstractmethod
    def run_ocr(
        self,
        images_dir: str,
        output_srt_path: str,
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
    ) -> str:
        """Process images in images_dir and save result to output_srt_path.

        progress_cb format: (done_count, total_count, status_msg)
        Returns path to final output_srt_path.
        """
        pass
