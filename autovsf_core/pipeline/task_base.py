"""autovsf_core/pipeline/task_base.py — Abstract Base Task definition."""

from abc import ABC, abstractmethod
from typing import Callable, Optional
from autovsf_core.domain.job import Job
from autovsf_core.domain.status import TaskStatus


class BaseTask(ABC):
    """Abstract base class for pipeline tasks."""

    def __init__(self, name: str):
        self.name = name
        self.status = TaskStatus.IDLE

    @abstractmethod
    def execute(self, job: Job, progress_cb: Optional[Callable[[str, float, str], None]] = None) -> None:
        """Execute task for the specified job.

        progress_cb format: (task_name, percent, message)
        """
        pass
