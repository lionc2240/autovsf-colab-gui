"""autovsf_core/pipeline/pipeline.py — Job Pipeline Execution Coordinator."""

from typing import List, Callable, Optional
from autovsf_core.domain.job import Job
from autovsf_core.domain.status import JobStatus
from autovsf_core.pipeline.task_base import BaseTask
from autovsf_core.pipeline.vsf_task import VSFTask
from autovsf_core.pipeline.ocr_task import OCRTask
from autovsf_core.pipeline.translate_task import TranslateTask


class JobPipeline:
    """Sequential task pipeline executor for a Job."""

    def __init__(self, tasks: Optional[List[BaseTask]] = None):
        self.tasks: List[BaseTask] = tasks or [
            VSFTask(),
            OCRTask(),
            TranslateTask(),
        ]

    def run(self, job: Job, progress_cb: Optional[Callable[[Job, str, float, str], None]] = None) -> None:
        """Executes all pipeline tasks for a given Job sequentially."""
        try:
            total_tasks = len(self.tasks)
            for idx, task in enumerate(self.tasks):
                def task_progress_cb(tname: str, pct: float, msg: str):
                    if progress_cb:
                        progress_cb(job, tname, pct, msg)

                task.execute(job, progress_cb=task_progress_cb)

            job.status = JobStatus.COMPLETED
            if progress_cb:
                progress_cb(job, "Pipeline Completed", 100.0, f"Successfully processed job {job.job_id}")
        except Exception as e:
            job.status = JobStatus.FAILED
            if not job.error_message:
                job.error_message = str(e)
            if progress_cb:
                progress_cb(job, "Pipeline Failed", 0.0, job.error_message)
            raise e
