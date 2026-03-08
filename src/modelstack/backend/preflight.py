# [10000] Beacon intent: Preflight checks for RunPod pod readiness

from dataclasses import dataclass, field
from typing import Optional

from modelstack.backend.ssh_manager import SSHManager


# [100] Subsystem intent: preflight check results

@dataclass
class PreflightResult:

    # [010] Method intent: define preflight check data structure

    vllm_installed: bool = False
    cloudflared_exists: bool = False
    models_found: dict[str, bool] = field(default_factory=dict)
    gpu_info: str = ""
    disk_usage: str = ""
    disk_free: str = ""
    errors: list[str] = field(default_factory=list)

    # [-----END [010]-----]

# [-----END [100]-----]


# [200] Subsystem intent: preflight check runner

class PreflightChecker:

    # [010] Method intent: initialize with SSH manager reference

    def __init__(self, ssh: SSHManager):

        # [001] store SSH manager
        self.ssh = ssh
        # [-----END [001]-----]

    # [-----END [010]-----]


    # [020] Method intent: run all preflight checks

    def run_all(self, expected_models: list[str]) -> PreflightResult:

        # [001] initialize result
        result = PreflightResult()
        # [-----END [001]-----]

        # [002] check vLLM installation
        result.vllm_installed = self._check_vllm(result)
        # [-----END [002]-----]

        # [003] check cloudflared binary
        result.cloudflared_exists = self._check_cloudflared(result)
        # [-----END [003]-----]

        # [004] check for expected models
        for model_dir in expected_models:
            result.models_found[model_dir] = self._check_model(model_dir, result)
        # [-----END [004]-----]

        # [005] collect GPU info
        result.gpu_info = self._get_gpu_info(result)
        # [-----END [005]-----]

        # [006] collect disk usage and free space
        result.disk_usage = self._get_disk_usage(result)
        result.disk_free = self._get_disk_free(result)
        # [-----END [006]-----]

        # [007] return completed result
        return result
        # [-----END [007]-----]

    # [-----END [020]-----]


    # [030] Method intent: check if vLLM is installed

    def _check_vllm(self, result: PreflightResult) -> bool:

        # [001] test vLLM import
        try:
            out, err, code = self.ssh.run_command("python -c \"import vllm; print(vllm.__version__)\"")
            if code == 0:
                return True
            result.errors.append(f"vLLM not found: {err.strip()}")
            return False
        except Exception as e:
            result.errors.append(f"vLLM check failed: {e}")
            return False
        # [-----END [001]-----]

    # [-----END [030]-----]


    # [040] Method intent: check if cloudflared binary exists

    def _check_cloudflared(self, result: PreflightResult) -> bool:

        # [001] test cloudflared binary
        try:
            out, err, code = self.ssh.run_command("test -x /workspace/cloudflared-linux-amd64 && echo exists")
            if code == 0 and "exists" in out:
                return True
            result.errors.append("cloudflared binary not found at /workspace/cloudflared-linux-amd64")
            return False
        except Exception as e:
            result.errors.append(f"cloudflared check failed: {e}")
            return False
        # [-----END [001]-----]

    # [-----END [040]-----]


    # [050] Method intent: check if a model directory exists

    def _check_model(self, model_dir: str, result: PreflightResult) -> bool:

        # [001] test model directory
        try:
            out, err, code = self.ssh.run_command(f"test -d /workspace/{model_dir} && echo exists")
            if code == 0 and "exists" in out:
                return True
            result.errors.append(f"Model not found: /workspace/{model_dir}")
            return False
        except Exception as e:
            result.errors.append(f"Model check failed for {model_dir}: {e}")
            return False
        # [-----END [001]-----]

    # [-----END [050]-----]


    # [060] Method intent: get GPU status

    def _get_gpu_info(self, result: PreflightResult) -> str:

        # [001] run nvidia-smi
        try:
            out, err, code = self.ssh.run_command("nvidia-smi")
            if code == 0:
                return out.strip()
            result.errors.append(f"nvidia-smi failed: {err.strip()}")
            return ""
        except Exception as e:
            result.errors.append(f"GPU check failed: {e}")
            return ""
        # [-----END [001]-----]

    # [-----END [060]-----]


    # [070] Method intent: get workspace disk usage

    def _get_disk_usage(self, result: PreflightResult) -> str:

        # [001] check workspace contents
        try:
            out, err, code = self.ssh.run_command("du -sh /workspace/*")
            if code == 0:
                return out.strip()
            return ""
        except Exception as e:
            result.errors.append(f"Disk usage check failed: {e}")
            return ""
        # [-----END [001]-----]

    # [-----END [070]-----]


    # [080] Method intent: get workspace free space

    def _get_disk_free(self, result: PreflightResult) -> str:

        # [001] check filesystem free space
        try:
            out, err, code = self.ssh.run_command("df -h /workspace")
            if code == 0:
                return out.strip()
            return ""
        except Exception as e:
            result.errors.append(f"Disk free check failed: {e}")
            return ""
        # [-----END [001]-----]

    # [-----END [080]-----]


    # [090] Method intent: kill stuck Python processes

    def kill_stuck_processes(self) -> tuple[str, str, int]:

        # [001] force kill all Python processes on pod
        return self.ssh.run_command("pkill -9 python")
        # [-----END [001]-----]

    # [-----END [090]-----]


    # [100] Method intent: install vLLM on pod

    def install_vllm(self) -> tuple[str, str, int]:

        # [001] install to persistent workspace path
        return self.ssh.run_command(
            "pip install --target=/workspace/python-packages vllm --break-system-packages",
            timeout=300,
        )
        # [-----END [001]-----]

    # [-----END [100]-----]


    # [110] Method intent: download cloudflared binary

    def install_cloudflared(self) -> tuple[str, str, int]:

        # [001] download and set executable permissions
        cmd = (
            "cd /workspace && "
            "wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && "
            "chmod +x cloudflared-linux-amd64"
        )
        return self.ssh.run_command(cmd, timeout=120)
        # [-----END [001]-----]

    # [-----END [110]-----]


    # [120] Method intent: download a model from HuggingFace

    def download_model(self, repo_id: str, local_dir: str) -> tuple[str, str, int]:

        # [001] download model to workspace
        cmd = f"cd /workspace && hf download {repo_id} --local-dir ./{local_dir}"
        return self.ssh.run_command(cmd, timeout=1800)
        # [-----END [001]-----]

    # [-----END [120]-----]

# [-----END [200]-----]