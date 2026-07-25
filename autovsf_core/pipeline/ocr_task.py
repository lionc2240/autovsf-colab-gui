"""autovsf_core/pipeline/ocr_task.py — Google Drive OCR Task."""

import os
from pathlib import Path
from typing import Callable, Optional

from autovsf_core.domain.job import Job
from autovsf_core.domain.status import TaskStatus, JobStatus
from autovsf_core.pipeline.task_base import BaseTask
from autovsf_core.engine.ocr.drive_ocr import GoogleDriveOCREngine


class OCRTask(BaseTask):
    """Pipeline task executing Google Drive document OCR."""

    def __init__(self, threads: int = 20):
        super().__init__("Google Drive OCR")
        self.ocr_engine = GoogleDriveOCREngine(threads=threads)

    def execute(self, job: Job, progress_cb: Optional[Callable[[str, float, str], None]] = None) -> None:
        self.status = TaskStatus.RUNNING
        job.status = JobStatus.RUNNING_OCR

        out_dir = job.output_dir or str(Path(job.video_path).parent / (Path(job.video_path).stem + "_out"))
        rgb_dir = os.path.join(out_dir, "RGBImages")

        if not job.srt_output_path:
            job.srt_output_path = str(Path(job.video_path).with_suffix(".srt"))

        def internal_cb(done: int, total: int, msg: str):
            job.ocr_done = done
            job.ocr_total = total
            pct = (done / total * 100.0) if total > 0 else 0.0
            if progress_cb:
                progress_cb(self.name, pct, msg)

        try:
            self.ocr_engine.run_ocr(
                images_dir=rgb_dir,
                output_srt_path=job.srt_output_path,
                progress_cb=internal_cb,
            )
            self.status = TaskStatus.SUCCESS
        except Exception as e:
            self.status = TaskStatus.FAILED
            job.error_message = f"OCR Task Failed: {str(e)}"
            raise e
