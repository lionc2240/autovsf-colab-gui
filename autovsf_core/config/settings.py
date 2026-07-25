"""autovsf_core/config/settings.py — Persistent configuration & CropProfile registry."""

import json
import os
from pathlib import Path
from typing import Dict, Any

from autovsf_core.config.environment import env
from autovsf_core.domain.crop import CropProfile

CONFIG_PATH = env.work_dir / "settings.json"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "folder_id": "",
    "credentials_file": str(env.work_dir / "credentials.json"),
    "token_file": str(env.work_dir / "token.json"),
    "vsf_path": env.find_vsf_binary(),
    "threads": 20,
    "delete_raw_texts": False,
    "delete_texts": False,
    "last_profile": "default",
    "crop_profiles": {
        "default": {"top": 0.2102, "bottom": 0.0000, "left": 0.0000, "right": 1.0000},
        "bottom_sub_narrow": {"top": 0.2500, "bottom": 0.0200, "left": 0.1000, "right": 0.9000},
        "full_frame": {"top": 1.0000, "bottom": 0.0000, "left": 0.0000, "right": 1.0000},
    },
}


class SettingsManager:
    """Manages reading, saving, and merging settings.json."""

    def __init__(self, config_file: Path = CONFIG_PATH):
        self.config_file = Path(config_file)
        self.data: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            self.save(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except Exception:
            self.save(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()

        merged = DEFAULT_SETTINGS.copy()
        for k, v in loaded.items():
            if k == "crop_profiles" and isinstance(v, dict):
                merged["crop_profiles"] = {**DEFAULT_SETTINGS["crop_profiles"], **v}
            else:
                merged[k] = v

        return merged

    def save(self, data: Dict[str, Any] = None) -> None:
        if data is not None:
            self.data = data
        os.makedirs(self.config_file.parent, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_crop_profile(self, name: str) -> CropProfile:
        profiles = self.data.get("crop_profiles", {})
        prof_data = profiles.get(name) or profiles.get("default", DEFAULT_SETTINGS["crop_profiles"]["default"])
        return CropProfile.from_dict(prof_data, name=name)

    def save_crop_profile(self, profile: CropProfile) -> None:
        if "crop_profiles" not in self.data:
            self.data["crop_profiles"] = {}
        self.data["crop_profiles"][profile.name] = {
            "top": profile.top,
            "bottom": profile.bottom,
            "left": profile.left,
            "right": profile.right,
        }
        self.save()


settings = SettingsManager()
