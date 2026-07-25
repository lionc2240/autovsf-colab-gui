"""autovsf_core/domain/crop.py — Crop profile domain model."""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class CropProfile:
    """Normalized crop profile coordinates for VideoSubFinder.

    top, bottom, left, right are floats in [0.0, 1.0].
    - top (te): top boundary (0.0 at top of frame, 1.0 at bottom)
    - bottom (be): bottom boundary (0.0 at bottom of frame, 1.0 at top)
    - left (le): left boundary (0.0 at left edge, 1.0 at right)
    - right (re): right boundary (1.0 at right edge, 0.0 at left)
    """

    top: float = 0.2102
    bottom: float = 0.0000
    left: float = 0.0000
    right: float = 1.0000
    name: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], name: str = "custom") -> "CropProfile":
        return cls(
            top=float(data.get("top", 0.2102)),
            bottom=float(data.get("bottom", 0.0000)),
            left=float(data.get("left", 0.0000)),
            right=float(data.get("right", 1.0000)),
            name=name,
        )

    def to_pixel_box(self, video_width: int, video_height: int) -> Dict[str, int]:
        """Convert normalized crop ratios to video frame pixel coordinates."""
        top_y = int((1.0 - self.top) * video_height) if self.top <= 1.0 else int(self.top)
        bottom_y = int((1.0 - self.bottom) * video_height) if self.bottom <= 1.0 else int(self.bottom)
        left_x = int(self.left * video_width)
        right_x = int(self.right * video_width)

        # Ensure valid order
        y_min = min(top_y, bottom_y)
        y_max = max(top_y, bottom_y)
        x_min = min(left_x, right_x)
        x_max = max(left_x, right_x)

        return {
            "x_min": x_min,
            "y_min": y_min,
            "x_max": x_max,
            "y_max": y_max,
            "width": x_max - x_min,
            "height": y_max - y_min,
        }

    @classmethod
    def from_pixel_box(
        cls, x_min: int, y_min: int, x_max: int, y_max: int, video_width: int, video_height: int, name: str = "custom"
    ) -> "CropProfile":
        """Construct normalized CropProfile from pixel bounding box coordinates."""
        vw = max(1, video_width)
        vh = max(1, video_height)

        top_val = round(max(0.0, min(1.0, 1.0 - (y_min / vh))), 4)
        bottom_val = round(max(0.0, min(1.0, 1.0 - (y_max / vh))), 4)
        left_val = round(max(0.0, min(1.0, x_min / vw)), 4)
        right_val = round(max(0.0, min(1.0, x_max / vw)), 4)

        return cls(top=top_val, bottom=bottom_val, left=left_val, right=right_val, name=name)
