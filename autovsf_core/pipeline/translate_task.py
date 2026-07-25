"""autovsf_core/pipeline/translate_task.py — AI Translation Task."""

import os
from pathlib import Path
from typing import Callable, Optional

from autovsf_core.domain.job import Job
from autovsf_core.domain.status import TaskStatus, JobStatus
from autovsf_core.pipeline.task_base import BaseTask
from autovsf_core.engine.translate.translator import SubtitleTranslator


class TranslateTask(BaseTask):
    """Pipeline task executing AI subtitle translation."""

    def __init__(self):
        super().__init__("AI Subtitle Translation")

    def execute(self, job: Job, progress_cb: Optional[Callable[[str, float, str], None]] = None) -> None:
        if not job.enable_translation:
            self.status = TaskStatus.SKIPPED
            return

        self.status = TaskStatus.RUNNING
        job.status = JobStatus.TRANSLATING

        translator = SubtitleTranslator(target_lang=job.target_language)
        input_srt = job.srt_output_path or str(Path(job.video_path).with_suffix(".srt"))
        output_vi_srt = str(Path(input_srt).parent / f"{Path(input_srt).stem}-vi.srt")

        def internal_cb(done: int, total: int, msg: str):
            pct = (done / total * 100.0) if total > 0 else 0.0
            if progress_cb:
                progress_cb(self.name, pct, msg)

        try:
            translator.translate_direct(
                input_srt=input_srt,
                output_srt=output_vi_srt,
                progress_cb=internal_cb,
            )
            job.srt_output_path = output_vi_srt
            self.status = TaskStatus.SUCCESS
        except Exception as e:
            self.status = TaskStatus.FAILED
            job.error_message = f"Translation Task Failed: {str(e)}"
            raise e
