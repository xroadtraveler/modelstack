# [10000] Beacon intent: VS Code Continue extension config management

from pathlib import Path
from typing import Optional

import yaml


# [100] Subsystem intent: Continue config reader and updater

class ContinueConfig:

    # [010] Method intent: initialize with config file path

    def __init__(self, config_path: Optional[Path] = None):

        # [001] set config path with default
        if config_path is None:
            config_path = Path.home() / ".continue" / "config.yaml"
        self.config_path = config_path
        # [-----END [001]-----]

    # [-----END [010]-----]


    # [020] Method intent: read and parse config file

    def read(self) -> dict:

        # [001] load YAML from disk
        if not self.config_path.exists():
            raise FileNotFoundError(f"Continue config not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
        # [-----END [001]-----]

    # [-----END [020]-----]


    # [030] Method intent: write config back to disk

    def write(self, config: dict) -> None:

        # [001] dump YAML preserving readability
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        # [-----END [001]-----]

    # [-----END [030]-----]


# [040] Method intent: update tunnel URL and model for RunPod entry

    def update_runpod_model(
        self,
        tunnel_url: str,
        model_path: str,
    ) -> bool:

        # [001] read current config
        config = self.read()
        # [-----END [001]-----]

        # [002] find RunPod model entry by trycloudflare URL or localhost
        models = config.get("models", [])
        target = None
        for entry in models:
            api_base = entry.get("apiBase", "")
            if "trycloudflare.com" in api_base or "localhost:7860" in api_base:
                target = entry
                break
        # [-----END [002]-----]

        # [003] generate display name from model path
        model_dir = model_path.strip("/").split("/")[-1]
        display_name = model_dir.replace("-", " ").replace(".", " ").title() + " RunPod"
        # [-----END [003]-----]

        # [004] update or report missing
        if target is None:
            return False
        target["name"] = display_name
        target["model"] = model_path
        target["apiBase"] = f"{tunnel_url}/v1"
        # [-----END [004]-----]

        # [005] write updated config
        self.write(config)
        return True
        # [-----END [005]-----]

    # [-----END [040]-----]


    # [050] Method intent: get current tunnel URL from config

    def get_current_url(self) -> Optional[str]:

        # [001] find RunPod entry by trycloudflare URL and return apiBase
        config = self.read()
        for entry in config.get("models", []):
            api_base = entry.get("apiBase", "")
            if "trycloudflare.com" in api_base or "localhost:7860" in api_base:
                return api_base
        return None
        # [-----END [001]-----]

    # [-----END [050]-----]

# [-----END [100]-----]