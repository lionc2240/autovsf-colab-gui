"""autovsf_core/pipeline/vsf_task.py — VideoSubFinder Extraction Task."""

import os
from typing import Callable, Optional
from autovsf_core.domain.job import Job
from autovsf_core.domain.status import TaskStatus, JobStatus
from autovsf_core.pipeline.task_base import BaseTask
from autovsf_core.engine.vsf.runner import VSFRunner


class VSFTask(BaseTask):
    """Pipeline task executing VideoSubFinder subtitle image extraction."""

    def __init__(self, vsf_binary: Optional[str] = None):
        super().__init__("VideoSubFinder Extraction")
        self.runner = VSFRunner(vsf_binary)

    def execute(self, job: Job, progress_cb: Optional[Callable[[str, float, str], None]] = None) -> None:
        self.status = TaskStatus.RUNNING
        job.status = JobStatus.RUNNING_VSF

        def internal_cb(pct: float, count: int, eta_str: str):
            job.vsf_progress = pct
            if count > 0:
                job.extracted_images_count = count
            msg = f"VSF Progress: {pct:.1f}% ({count} images extracted) ETA: {eta_str}"
            if progress_cb:
                progress_cb(self.name, pct, msg)

        try:
            rgb_dir = self.runner.run(
                video_path=job.video_path,
                crop=job.crop_profile,
                output_dir=job.output_dir,
                progress_cb=internal_cb,
            )
            self.status = TaskStatus.SUCCESS
        except Exception as e:
            self.status = TaskStatus.FAILED
            job.error_message = f"VSF Task Failed: {str(e)}"
            raise e
