# [10000] Beacon intent: Scrolling log output panel

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)


# [100] Subsystem intent: log display widget

class LogPanel(QWidget):

    # [010] Method intent: initialize log panel layout

    def __init__(self):
        super().__init__()

        # [001] create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        # [-----END [001]-----]

        # [002] create header row with label and clear button
        header = QHBoxLayout()
        header.addWidget(QLabel("Log Output:"))
        header.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear)
        header.addWidget(clear_btn)
        layout.addLayout(header)
        # [-----END [002]-----]

        # [003] create scrolling text area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log_area)
        # [-----END [003]-----]

    # [-----END [010]-----]


    # [020] Method intent: append text to log

    def append_log(self, text: str) -> None:

        # [001] append and scroll to bottom
        self.log_area.append(text.rstrip())
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        # [-----END [001]-----]

    # [-----END [020]-----]


    # [030] Method intent: clear log contents

    def _on_clear(self) -> None:

        # [001] clear text area
        self.log_area.clear()
        # [-----END [001]-----]

    # [-----END [030]-----]

# [-----END [100]-----]