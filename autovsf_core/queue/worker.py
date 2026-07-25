"""autovsf_core/queue/worker.py — Background Job Worker Process."""

import queue
import threading
import time
from typing import Callable, Optional

from autovsf_core.domain.job import Job
from autovsf_core.pipeline.pipeline import JobPipeline


class JobWorker(threading.Thread):
    """Background worker thread processing jobs from QueueManager."""

    def __init__(
        self,
        worker_id: str,
        job_queue: queue.Queue,
        progress_cb: Optional[Callable[[Job, str, float, str], None]] = None,
    ):
        super().__init__(name=f"JobWorker-{worker_id}", daemon=True)
        self.worker_id = worker_id
        self.job_queue = job_queue
        self.progress_cb = progress_cb
        self.pipeline = JobPipeline()
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                job: Job = self.job_queue.get(timeout=1.0)
                if job is None:
                    break

                try:
                    self.pipeline.run(job, progress_cb=self.progress_cb)
                except Exception as e:
                    print(f"[{self.name}] Job {job.job_id} failed: {e}")
                finally:
                    self.job_queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self._stop_event.set()
