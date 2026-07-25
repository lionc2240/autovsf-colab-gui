"""autovsf_core/domain/job.py — Job domain model."""

import uuid
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from autovsf_core.domain.crop import CropProfile
from autovsf_core.domain.status import JobStatus


@dataclass
class Job:
    """Represents a single video subtitle extraction & translation job."""

    video_path: str
    crop_profile: CropProfile = field(default_factory=CropProfile)
    target_language: str = "Tiếng Việt"
    enable_translation: bool = True
    output_dir: Optional[str] = None
    srt_output_path: Optional[str] = None

    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)

    # Real-time metrics
    vsf_progress: float = 0.0
    extracted_images_count: int = 0
    ocr_done: int = 0
    ocr_total: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "video_path": self.video_path,
            "crop_profile": self.crop_profile.to_dict(),
            "target_language": self.target_language,
            "enable_translation": self.enable_translation,
            "output_dir": self.output_dir,
            "srt_output_path": self.srt_output_path,
            "status": self.status.value,
            "created_at": self.created_at,
            "vsf_progress": self.vsf_progress,
            "extracted_images_count": self.extracted_images_count,
            "ocr_done": self.ocr_done,
            "ocr_total": self.ocr_total,
            "error_message": self.error_message,
        }
