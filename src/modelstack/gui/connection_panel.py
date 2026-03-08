# [10000] Beacon intent: SSH connection panel widget

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal


# [100] Subsystem intent: connection panel UI and signals

class ConnectionPanel(QWidget):

    # [010] Class-level intent: define signals

    connect_requested = pyqtSignal(str)
    disconnect_requested = pyqtSignal()

    # [-----END [010]-----]


    # [020] Method intent: initialize panel layout

    def __init__(self):
        super().__init__()

        # [001] create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        # [-----END [001]-----]

        # [002] create label
        label = QLabel("SSH Connection String:")
        layout.addWidget(label)
        # [-----END [002]-----]

        # [003] create input row with textbox and buttons
        input_row = QHBoxLayout()

        self.ssh_input = QLineEdit()
        self.ssh_input.setPlaceholderText("ssh <pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519")
        input_row.addWidget(self.ssh_input, stretch=1)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        input_row.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        input_row.addWidget(self.disconnect_btn)

        layout.addLayout(input_row)
        # [-----END [003]-----]

        # [004] create status indicator
        self.status_label = QLabel("Status: Disconnected")
        layout.addWidget(self.status_label)
        # [-----END [004]-----]

    # [-----END [020]-----]


    # [030] Method intent: handle connect button click

    def _on_connect_clicked(self) -> None:

        # [001] emit signal with SSH string
        ssh_string = self.ssh_input.text().strip()
        if ssh_string:
            self.connect_requested.emit(ssh_string)
        # [-----END [001]-----]

    # [-----END [030]-----]


    # [040] Method intent: handle disconnect button click

    def _on_disconnect_clicked(self) -> None:

        # [001] emit disconnect signal
        self.disconnect_requested.emit()
        # [-----END [001]-----]

    # [-----END [040]-----]


    # [050] Method intent: update UI to reflect connection state

    def set_connected(self, connected: bool) -> None:

        # [001] toggle buttons and status text
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.ssh_input.setEnabled(not connected)
        if connected:
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("color: red;")
        # [-----END [001]-----]

    # [-----END [050]-----]

# [-----END [100]-----]