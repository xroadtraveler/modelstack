# [10000] Beacon intent: Application settings management

import json
from pathlib import Path
from typing import Any


# [100] Subsystem intent: settings manager with default creation

class SettingsManager:

    # [010] Class-level intent: define default settings template

    DEFAULT_SETTINGS = {
        "ssh_connection_string": "",
        "last_used_model": "",
        "continue_config_path": "",
        "auto_update_continue": True,
        "models": {},
    }

    # [-----END [010]-----]


    # [020] Method intent: initialize with settings path

    def __init__(self, settings_path: Path = None):

        # [001] set path with platform default
        if settings_path is None:
            settings_path = (
                Path.home() / "AppData" / "Roaming" / "ModelStack" / "settings.json"
            )
        self.settings_path = settings_path
        self._data: dict[str, Any] = {}
        # [-----END [001]-----]

    # [-----END [020]-----]


    # [030] Method intent: load settings from disk or create defaults

    def load(self) -> dict[str, Any]:

        # [001] ensure directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        # [-----END [001]-----]

        # [002] create default file if missing
        if not self.settings_path.exists():
            self._data = dict(self.DEFAULT_SETTINGS)
            self._detect_continue_config()
            self.save()
            return self._data
        # [-----END [002]-----]

        # [003] read existing file
        with open(self.settings_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        # [-----END [003]-----]

        # [004] backfill any missing keys from defaults
        changed = False
        for key, value in self.DEFAULT_SETTINGS.items():
            if key not in self._data:
                self._data[key] = value
                changed = True
        if changed:
            self.save()
        # [-----END [004]-----]

        # [005] return loaded settings
        return self._data
        # [-----END [005]-----]

    # [-----END [030]-----]


    # [040] Method intent: save current settings to disk

    def save(self) -> None:

        # [001] write JSON with readable formatting
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        # [-----END [001]-----]

    # [-----END [040]-----]


    # [050] Method intent: get a setting value

    def get(self, key: str, default: Any = None) -> Any:

        # [001] return value or default
        return self._data.get(key, default)
        # [-----END [001]-----]

    # [-----END [050]-----]


    # [060] Method intent: set a setting value and save

    def set(self, key: str, value: Any) -> None:

        # [001] update and persist
        self._data[key] = value
        self.save()
        # [-----END [001]-----]

    # [-----END [060]-----]


    # [070] Method intent: add or update a model entry

    def set_model(
        self,
        model_id: str,
        local_dir: str,
        max_model_len: int = 16000,
        gpu_memory_utilization: float = 0.9,
        favorite: bool = False,
    ) -> None:

        # [001] update model entry and save
        models = self._data.get("models", {})
        models[model_id] = {
            "favorite": favorite,
            "local_dir": local_dir,
            "max_model_len": max_model_len,
            "gpu_memory_utilization": gpu_memory_utilization,
        }
        self._data["models"] = models
        self.save()
        # [-----END [001]-----]

    # [-----END [070]-----]


    # [080] Method intent: remove a model entry

    def remove_model(self, model_id: str) -> None:

        # [001] delete model and save
        models = self._data.get("models", {})
        models.pop(model_id, None)
        self._data["models"] = models
        self.save()
        # [-----END [001]-----]

    # [-----END [080]-----]


    # [090] Method intent: auto-detect Continue config path

    def _detect_continue_config(self) -> None:

        # [001] check common Continue config location
        default_path = Path.home() / ".continue" / "config.yaml"
        if default_path.exists():
            self._data["continue_config_path"] = str(default_path)
        # [-----END [001]-----]

    # [-----END [090]-----]

# [-----END [100]-----]