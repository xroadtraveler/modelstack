# [10000] Beacon intent: Service control panel for vLLM and cloudflared

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
)
from PyQt6.QtCore import pyqtSignal


# [100] Subsystem intent: service control widget

class ServicePanel(QWidget):

    # [010] Class-level intent: define signals

    start_vllm_requested = pyqtSignal(str, int, float)
    stop_vllm_requested = pyqtSignal()
    start_tunnel_requested = pyqtSignal()
    stop_tunnel_requested = pyqtSignal()

    # [-----END [010]-----]


    # [020] Method intent: initialize panel layout

    def __init__(self):
        super().__init__()

        # [001] create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        # [-----END [001]-----]

        # [002] create vLLM control group
        vllm_group = QGroupBox("vLLM Server")
        vllm_layout = QVBoxLayout(vllm_group)

        self.vllm_status = QLabel("Stopped")
        vllm_layout.addWidget(self.vllm_status)

        vllm_buttons = QHBoxLayout()
        self.start_vllm_btn = QPushButton("Start vLLM")
        self.start_vllm_btn.clicked.connect(self._on_start_vllm)
        vllm_buttons.addWidget(self.start_vllm_btn)

        self.stop_vllm_btn = QPushButton("Stop vLLM")
        self.stop_vllm_btn.clicked.connect(self._on_stop_vllm)
        self.stop_vllm_btn.setEnabled(False)
        vllm_buttons.addWidget(self.stop_vllm_btn)

        vllm_layout.addLayout(vllm_buttons)
        layout.addWidget(vllm_group)
        # [-----END [002]-----]

        # [003] create cloudflared control group
        tunnel_group = QGroupBox("Cloudflare Tunnel")
        tunnel_layout = QVBoxLayout(tunnel_group)

        self.tunnel_status = QLabel("Stopped")
        tunnel_layout.addWidget(self.tunnel_status)

        self.tunnel_url_display = QLineEdit()
        self.tunnel_url_display.setReadOnly(True)
        self.tunnel_url_display.setPlaceholderText("Tunnel URL will appear here")
        tunnel_layout.addWidget(self.tunnel_url_display)

        tunnel_buttons = QHBoxLayout()
        self.start_tunnel_btn = QPushButton("Start Tunnel")
        self.start_tunnel_btn.clicked.connect(self._on_start_tunnel)
        tunnel_buttons.addWidget(self.start_tunnel_btn)

        self.stop_tunnel_btn = QPushButton("Stop Tunnel")
        self.stop_tunnel_btn.clicked.connect(self._on_stop_tunnel)
        self.stop_tunnel_btn.setEnabled(False)
        tunnel_buttons.addWidget(self.stop_tunnel_btn)

        tunnel_layout.addLayout(tunnel_buttons)
        layout.addWidget(tunnel_group)
        # [-----END [003]-----]

    # [-----END [020]-----]


    # [030] Method intent: emit vLLM start signal with model panel data

    def _on_start_vllm(self) -> None:

        # [001] emit signal (main window will get model info from model panel)
        self.start_vllm_requested.emit("", 16000, 0.9)
        # [-----END [001]-----]

    # [-----END [030]-----]


    # [040] Method intent: emit vLLM stop signal

    def _on_stop_vllm(self) -> None:

        # [001] emit stop signal
        self.stop_vllm_requested.emit()
        # [-----END [001]-----]

    # [-----END [040]-----]


    # [050] Method intent: emit tunnel start signal

    def _on_start_tunnel(self) -> None:

        # [001] emit start signal
        self.start_tunnel_requested.emit()
        # [-----END [001]-----]

    # [-----END [050]-----]


    # [060] Method intent: emit tunnel stop signal

    def _on_stop_tunnel(self) -> None:

        # [001] emit stop signal
        self.stop_tunnel_requested.emit()
        # [-----END [001]-----]

    # [-----END [060]-----]


    # [070] Method intent: update vLLM running state

    def set_vllm_running(self, running: bool) -> None:

        # [001] toggle buttons and status
        self.start_vllm_btn.setEnabled(not running)
        self.stop_vllm_btn.setEnabled(running)
        self.vllm_status.setText("Running" if running else "Stopped")
        self.vllm_status.setStyleSheet("color: green;" if running else "color: red;")
        # [-----END [001]-----]

    # [-----END [070]-----]


    # [080] Method intent: update tunnel running state

    def set_tunnel_running(self, running: bool) -> None:

        # [001] toggle buttons and status
        self.start_tunnel_btn.setEnabled(not running)
        self.stop_tunnel_btn.setEnabled(running)
        self.tunnel_status.setText("Running" if running else "Stopped")
        self.tunnel_status.setStyleSheet("color: green;" if running else "color: red;")
        # [-----END [001]-----]

    # [-----END [080]-----]


    # [090] Method intent: display tunnel URL

    def set_tunnel_url(self, url: str) -> None:

        # [001] update URL display
        self.tunnel_url_display.setText(url)
        # [-----END [001]-----]

    # [-----END [090]-----]


    # [100] Method intent: reset all status indicators

    def reset_status(self) -> None:

        # [001] reset to disconnected defaults
        self.set_vllm_running(False)
        self.set_tunnel_running(False)
        self.tunnel_url_display.clear()
        # [-----END [001]-----]

    # [-----END [100]-----]

# [-----END [100]-----]