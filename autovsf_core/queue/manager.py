"""autovsf_core/queue/manager.py — Central Job Queue Manager."""

import queue
import threading
from typing import List, Dict, Optional, Callable

from autovsf_core.domain.job import Job
from autovsf_core.domain.status import JobStatus
from autovsf_core.queue.worker import JobWorker


class QueueManager:
    """Singleton Job Queue Manager managing job submission, worker pool, and real-time status."""

    def __init__(self, num_workers: int = 1):
        self.job_queue: queue.Queue = queue.Queue()
        self.jobs: Dict[str, Job] = {}
        self.lock = threading.Lock()

        self.subscribers: List[Callable[[Job, str, float, str], None]] = []

        self.workers: List[JobWorker] = []
        for i in range(num_workers):
            w = JobWorker(worker_id=str(i + 1), job_queue=self.job_queue, progress_cb=self._on_job_progress)
            w.start()
            self.workers.append(w)

    def subscribe(self, listener: Callable[[Job, str, float, str], None]):
        """Subscribe to real-time job progress events."""
        with self.lock:
            if listener not in self.subscribers:
                self.subscribers.append(listener)

    def _on_job_progress(self, job: Job, task_name: str, pct: float, msg: str):
        with self.lock:
            listeners = list(self.subscribers)
        for listener in listeners:
            try:
                listener(job, task_name, pct, msg)
            except Exception:
                pass

    def enqueue_job(self, job: Job) -> str:
        """Enqueue a new Job for background processing."""
        with self.lock:
            job.status = JobStatus.QUEUED
            self.jobs[job.job_id] = job

        self.job_queue.put(job)
        self._on_job_progress(job, "Enqueued", 0.0, f"Job {job.job_id} added to queue")
        return job.job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        with self.lock:
            return self.jobs.get(job_id)

    def get_all_jobs(self) -> List[Job]:
        with self.lock:
            return list(self.jobs.values())

    def shutdown(self):
        for w in self.workers:
            w.stop()


queue_manager = QueueManager(num_workers=1)
