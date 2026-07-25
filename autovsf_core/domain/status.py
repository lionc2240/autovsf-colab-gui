"""autovsf_core/domain/status.py — Job & Task execution status enums."""

from enum import Enum, auto


class JobStatus(Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING_VSF = "RUNNING_VSF"
    RUNNING_OCR = "RUNNING_OCR"
    TRANSLATING = "TRANSLATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskStatus(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
