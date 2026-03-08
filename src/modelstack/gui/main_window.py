# [10000] Beacon intent: Main application window

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QWidget,
)
from PyQt6.QtCore import Qt

from modelstack.backend.ssh_manager import SSHManager
from modelstack.backend.preflight import PreflightChecker
from modelstack.backend.services import VLLMService, CloudflaredService
from modelstack.backend.continue_config import ContinueConfig
from modelstack.gui.connection_panel import ConnectionPanel
from modelstack.gui.model_panel import ModelPanel
from modelstack.gui.service_panel import ServicePanel
from modelstack.gui.log_panel import LogPanel


# [100] Subsystem intent: main window layout and backend wiring

class MainWindow(QMainWindow):

    # [010] Method intent: initialize window and backend services

    def __init__(self):
        super().__init__()

        # [001] configure window properties
        self.setWindowTitle("ModelStack")
        self.setMinimumSize(900, 600)
        # [-----END [001]-----]

        # [002] initialize backend services
        self.ssh = SSHManager()
        self.preflight = PreflightChecker(self.ssh)
        self.vllm = VLLMService(self.ssh)
        self.cloudflared = CloudflaredService(self.ssh)
        self.continue_config = ContinueConfig()
        # [-----END [002]-----]

        # [003] build UI layout
        self._build_ui()
        # [-----END [003]-----]

        # [004] connect panel signals to backend logic
        self._connect_signals()
        # [-----END [004]-----]

    # [-----END [010]-----]


    # [020] Method intent: construct UI layout with panels

    def _build_ui(self) -> None:

        # [001] create central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        # [-----END [001]-----]

        # [002] create connection panel at top
        self.connection_panel = ConnectionPanel()
        main_layout.addWidget(self.connection_panel)
        # [-----END [002]-----]

        # [003] create splitter for middle and bottom sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        # [-----END [003]-----]

        # [004] create top row with model and service panels side by side
        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        self.model_panel = ModelPanel()
        self.service_panel = ServicePanel()
        top_layout.addWidget(self.model_panel, stretch=1)
        top_layout.addWidget(self.service_panel, stretch=1)
        splitter.addWidget(top_row)
        # [-----END [004]-----]

        # [005] create log panel at bottom
        self.log_panel = LogPanel()
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)
        # [-----END [005]-----]

    # [-----END [020]-----]


    # [030] Method intent: wire panel signals to backend actions

    def _connect_signals(self) -> None:

        # [001] connection panel signals
        self.connection_panel.connect_requested.connect(self._on_connect)
        self.connection_panel.disconnect_requested.connect(self._on_disconnect)
        # [-----END [001]-----]

        # [002] service panel signals
        self.service_panel.start_vllm_requested.connect(self._on_start_vllm)
        self.service_panel.stop_vllm_requested.connect(self._on_stop_vllm)
        self.service_panel.start_tunnel_requested.connect(self._on_start_tunnel)
        self.service_panel.stop_tunnel_requested.connect(self._on_stop_tunnel)
        # [-----END [002]-----]

        # [003] model panel signals
        self.model_panel.preflight_requested.connect(self._on_run_preflight)
        # [-----END [003]-----]

    # [-----END [030]-----]


    # [040] Method intent: handle SSH connect

    def _on_connect(self, ssh_string: str) -> None:

        # [001] attempt connection and log result
        try:
            self.ssh.connect(ssh_string)
            self.log_panel.append_log("SSH connected.")
            self.connection_panel.set_connected(True)
        except Exception as e:
            self.log_panel.append_log(f"SSH connection failed: {e}")
            self.connection_panel.set_connected(False)
        # [-----END [001]-----]

    # [-----END [040]-----]


    # [050] Method intent: handle SSH disconnect

    def _on_disconnect(self) -> None:

        # [001] stop services and disconnect
        self.vllm.stop()
        self.cloudflared.stop()
        self.ssh.disconnect()
        self.log_panel.append_log("SSH disconnected.")
        self.connection_panel.set_connected(False)
        self.service_panel.reset_status()
        # [-----END [001]-----]

    # [-----END [050]-----]


    # [060] Method intent: handle vLLM start

    def _on_start_vllm(self, model_dir: str, max_model_len: int, gpu_mem: float) -> None:

        # [001] start vLLM with callbacks to log panel
        self.log_panel.append_log(f"Starting vLLM with /workspace/{model_dir}...")
        self.vllm.start(
            model_dir=model_dir,
            max_model_len=max_model_len,
            gpu_memory_utilization=gpu_mem,
            on_output=lambda data: self.log_panel.append_log(data),
            on_ready=lambda: self._on_vllm_ready(),
            on_exit=lambda code: self.log_panel.append_log(f"vLLM exited with code {code}"),
        )
        # [-----END [001]-----]

    # [-----END [060]-----]


    # [070] Method intent: handle vLLM ready

    def _on_vllm_ready(self) -> None:

        # [001] update UI and log
        self.log_panel.append_log("vLLM startup complete.")
        self.service_panel.set_vllm_running(True)
        # [-----END [001]-----]

    # [-----END [070]-----]


    # [080] Method intent: handle vLLM stop

    def _on_stop_vllm(self) -> None:

        # [001] stop service and update UI
        self.vllm.stop()
        self.log_panel.append_log("vLLM stopped.")
        self.service_panel.set_vllm_running(False)
        # [-----END [001]-----]

    # [-----END [080]-----]


    # [090] Method intent: handle cloudflared start

    def _on_start_tunnel(self) -> None:

        # [001] start tunnel with callbacks
        self.log_panel.append_log("Starting cloudflared tunnel...")
        self.cloudflared.start(
            on_output=lambda data: self.log_panel.append_log(data),
            on_url=lambda url: self._on_tunnel_url(url),
            on_exit=lambda code: self.log_panel.append_log(f"cloudflared exited with code {code}"),
        )
        # [-----END [001]-----]

    # [-----END [090]-----]


    # [095] Method intent: handle cloudflared stop

    def _on_stop_tunnel(self) -> None:

        # [001] stop tunnel and update UI
        self.cloudflared.stop()
        self.log_panel.append_log("cloudflared stopped.")
        self.service_panel.set_tunnel_running(False)
        # [-----END [001]-----]

    # [-----END [095]-----]


    # [100] Method intent: handle tunnel URL captured

    def _on_tunnel_url(self, url: str) -> None:

        # [001] update UI and auto-update Continue config
        self.log_panel.append_log(f"Tunnel URL: {url}")
        self.service_panel.set_tunnel_url(url)
        self.service_panel.set_tunnel_running(True)
        # [-----END [001]-----]

        # [002] update Continue config if vLLM model is known
        if self.vllm.model_path:
            updated = self.continue_config.update_runpod_model(url, self.vllm.model_path)
            if updated:
                self.log_panel.append_log("Continue config updated.")
            else:
                self.log_panel.append_log("Warning: Could not find RunPod entry in Continue config.")
        # [-----END [002]-----]

    # [-----END [100]-----]


    # [110] Method intent: handle preflight check

    def _on_run_preflight(self, expected_models: list[str]) -> None:

        # [001] run preflight and log results
        self.log_panel.append_log("Running preflight checks...")
        result = self.preflight.run_all(expected_models)
        self.log_panel.append_log(f"  vLLM installed: {result.vllm_installed}")
        self.log_panel.append_log(f"  cloudflared exists: {result.cloudflared_exists}")
        for model_dir, found in result.models_found.items():
            self.log_panel.append_log(f"  Model {model_dir}: {'found' if found else 'MISSING'}")
        if result.gpu_info:
            self.log_panel.append_log(f"  GPU:\n{result.gpu_info}")
        for err in result.errors:
            self.log_panel.append_log(f"  ERROR: {err}")
        self.model_panel.update_preflight(result)
        # [-----END [001]-----]

    # [-----END [110]-----]


    # [120] Method intent: clean up on window close

    def closeEvent(self, event) -> None:

        # [001] disconnect SSH and stop all services
        self.vllm.stop()
        self.cloudflared.stop()
        self.ssh.disconnect()
        event.accept()
        # [-----END [001]-----]

    # [-----END [120]-----]

# [-----END [100]-----]