# [10000] Beacon intent: RunPod service management (vLLM and cloudflared)

import re
import threading
from typing import Callable, Optional

from modelstack.backend.ssh_manager import SSHManager


# [100] Subsystem intent: vLLM server manager

class VLLMService:

    # [010] Method intent: initialize vLLM service

    def __init__(self, ssh: SSHManager):

        # [001] store dependencies and state
        self.ssh = ssh
        self.is_running = False
        self.model_path: Optional[str] = None
        self._ready_event = threading.Event()
        # [-----END [001]-----]

    # [-----END [010]-----]


    # [020] Method intent: start vLLM server with specified model

    def start(
        self,
        model_dir: str,
        max_model_len: int = 16000,
        gpu_memory_utilization: float = 0.9,
        on_output: Optional[Callable[[str], None]] = None,
        on_ready: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[int], None]] = None,
    ) -> None:

        # [001] build vLLM launch command
        cmd = (
            f"cd /workspace && "
            f"python -m vllm.entrypoints.openai.api_server "
            f"--model /workspace/{model_dir} "
            f"--host 0.0.0.0 "
            f"--port 7860 "
            f"--trust-remote-code "
            f"--max-model-len {max_model_len} "
            f"--gpu-memory-utilization {gpu_memory_utilization}"
        )
        # [-----END [001]-----]

        # [002] set up PYTHONPATH for persistent installs
        cmd = (
            "export PYTHONPATH=/workspace/python-packages:$PYTHONPATH && "
            + cmd
        )
        # [-----END [002]-----]

        # [003] define output handler that detects startup completion
        self._ready_event.clear()
        self.model_path = f"/workspace/{model_dir}"

        def output_handler(data: str) -> None:
            if on_output:
                on_output(data)
            if not self._ready_event.is_set() and "Application startup complete" in data:
                self.is_running = True
                self._ready_event.set()
                if on_ready:
                    on_ready()
        # [-----END [003]-----]

        # [004] define exit handler
        def exit_handler(exit_code: int) -> None:
            self.is_running = False
            self._ready_event.clear()
            if on_exit:
                on_exit(exit_code)
        # [-----END [004]-----]

        # [005] start streaming process
        self.ssh.start_stream(
            name="vllm",
            command=cmd,
            on_output=output_handler,
            on_exit=exit_handler,
        )
        # [-----END [005]-----]

    # [-----END [020]-----]


    # [030] Method intent: stop vLLM server

    def stop(self) -> None:

        # [001] stop stream and update state
        self.ssh.stop_stream("vllm")
        self.is_running = False
        self._ready_event.clear()
        self.model_path = None
        # [-----END [001]-----]

    # [-----END [030]-----]


    # [040] Method intent: wait for vLLM to finish starting

    def wait_until_ready(self, timeout: float = 120) -> bool:

        # [001] block until ready event or timeout
        return self._ready_event.wait(timeout=timeout)
        # [-----END [001]-----]

    # [-----END [040]-----]

# [-----END [100]-----]


# [200] Subsystem intent: cloudflared tunnel manager

class CloudflaredService:

    # [010] Method intent: initialize cloudflared service

    def __init__(self, ssh: SSHManager):

        # [001] store dependencies and state
        self.ssh = ssh
        self.is_running = False
        self.tunnel_url: Optional[str] = None
        self._url_event = threading.Event()
        # [-----END [001]-----]

    # [-----END [010]-----]


    # [020] Method intent: start cloudflared tunnel

    def start(
        self,
        on_output: Optional[Callable[[str], None]] = None,
        on_url: Optional[Callable[[str], None]] = None,
        on_exit: Optional[Callable[[int], None]] = None,
    ) -> None:

        # [001] build cloudflared command
        cmd = "cd /workspace && ./cloudflared-linux-amd64 tunnel --url http://localhost:7860"
        # [-----END [001]-----]

        # [002] define output handler that captures tunnel URL
        self._url_event.clear()

        def output_handler(data: str) -> None:
            if on_output:
                on_output(data)
            if not self._url_event.is_set():
                url_match = re.search(r"https://[\w-]+\.trycloudflare\.com", data)
                if url_match:
                    self.tunnel_url = url_match.group(0)
                    self.is_running = True
                    self._url_event.set()
                    if on_url:
                        on_url(self.tunnel_url)
        # [-----END [002]-----]

        # [003] define exit handler
        def exit_handler(exit_code: int) -> None:
            self.is_running = False
            self._url_event.clear()
            if on_exit:
                on_exit(exit_code)
        # [-----END [003]-----]

        # [004] start streaming process
        self.ssh.start_stream(
            name="cloudflared",
            command=cmd,
            on_output=output_handler,
            on_exit=exit_handler,
        )
        # [-----END [004]-----]

    # [-----END [020]-----]


    # [030] Method intent: stop cloudflared tunnel

    def stop(self) -> None:

        # [001] stop stream and update state
        self.ssh.stop_stream("cloudflared")
        self.is_running = False
        self._url_event.clear()
        self.tunnel_url = None
        # [-----END [001]-----]

    # [-----END [030]-----]


    # [040] Method intent: wait for tunnel URL to be captured

    def wait_until_ready(self, timeout: float = 30) -> bool:

        # [001] block until URL captured or timeout
        return self._url_event.wait(timeout=timeout)
        # [-----END [001]-----]

    # [-----END [040]-----]

# [-----END [200]-----]