# [10000] Beacon intent: Model selection and preflight status panel

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QSpinBox,
    QDoubleSpinBox,
)
from PyQt6.QtCore import pyqtSignal

from modelstack.backend.preflight import PreflightResult


# [100] Subsystem intent: model panel widget

class ModelPanel(QWidget):

    # [010] Class-level intent: define signals

    preflight_requested = pyqtSignal(list)
    model_selected = pyqtSignal(str, int, float)

    # [-----END [010]-----]


    # [020] Method intent: initialize panel layout

    def __init__(self):
        super().__init__()

        # [001] create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        # [-----END [001]-----]

        # [002] create model list group
        model_group = QGroupBox("Models")
        model_layout = QVBoxLayout(model_group)

        self.model_list = QListWidget()
        model_layout.addWidget(self.model_list)

        self.model_list.currentItemChanged.connect(self._on_model_changed)
        layout.addWidget(model_group)
        # [-----END [002]-----]

        # [003] create vLLM parameter controls
        params_group = QGroupBox("vLLM Parameters")
        params_layout = QVBoxLayout(params_group)

        len_row = QHBoxLayout()
        len_row.addWidget(QLabel("Max Model Len:"))
        self.max_len_spin = QSpinBox()
        self.max_len_spin.setRange(1024, 131072)
        self.max_len_spin.setValue(16000)
        self.max_len_spin.setSingleStep(1000)
        len_row.addWidget(self.max_len_spin)
        params_layout.addLayout(len_row)

        gpu_row = QHBoxLayout()
        gpu_row.addWidget(QLabel("GPU Memory Util:"))
        self.gpu_mem_spin = QDoubleSpinBox()
        self.gpu_mem_spin.setRange(0.1, 1.0)
        self.gpu_mem_spin.setValue(0.9)
        self.gpu_mem_spin.setSingleStep(0.05)
        self.gpu_mem_spin.setDecimals(2)
        gpu_row.addWidget(self.gpu_mem_spin)
        params_layout.addLayout(gpu_row)

        layout.addWidget(params_group)
        # [-----END [003]-----]

        # [004] create preflight section
        preflight_group = QGroupBox("Preflight Status")
        preflight_layout = QVBoxLayout(preflight_group)

        self.preflight_label = QLabel("No checks run yet.")
        preflight_layout.addWidget(self.preflight_label)

        self.preflight_btn = QPushButton("Run Preflight Checks")
        self.preflight_btn.clicked.connect(self._on_preflight_clicked)
        preflight_layout.addWidget(self.preflight_btn)

        layout.addWidget(preflight_group)
        # [-----END [004]-----]

    # [-----END [020]-----]


    # [030] Method intent: handle preflight button click

    def _on_preflight_clicked(self) -> None:

        # [001] gather model dirs from list and emit signal
        model_dirs = []
        for i in range(self.model_list.count()):
            item = self.model_list.item(i)
            if item and item.data(256):
                model_dirs.append(item.data(256))
        self.preflight_requested.emit(model_dirs)
        # [-----END [001]-----]

    # [-----END [030]-----]


    # [035] Method intent: handle model selection change

    def _on_model_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:

        # [001] update parameter spinboxes from stored model data
        if current is None:
            return
        model_data = current.data(257)
        if model_data:
            self.max_len_spin.setValue(model_data.get("max_model_len", 16000))
            self.gpu_mem_spin.setValue(model_data.get("gpu_memory_utilization", 0.9))
        # [-----END [001]-----]

    # [-----END [035]-----]


    # [040] Method intent: populate model list from settings

    def load_models(self, models: dict) -> None:

        # [001] clear and rebuild model list
        self.model_list.clear()
        for model_id, model_info in models.items():
            local_dir = model_info.get("local_dir", model_id)
            item = QListWidgetItem(model_id)
            item.setData(256, local_dir)
            item.setData(257, model_info)
            self.model_list.addItem(item)
        # [-----END [001]-----]

    # [-----END [040]-----]


    # [050] Method intent: get currently selected model info

    def get_selected_model(self) -> tuple[str, int, float]:

        # [001] return selected model dir and parameters
        current = self.model_list.currentItem()
        model_dir = ""
        if current:
            model_dir = current.data(256) or ""
        return model_dir, self.max_len_spin.value(), self.gpu_mem_spin.value()
        # [-----END [001]-----]

    # [-----END [050]-----]


    # [060] Method intent: update preflight status display

    def update_preflight(self, result: PreflightResult) -> None:

        # [001] build status summary
        lines = []
        lines.append(f"vLLM: {'OK' if result.vllm_installed else 'MISSING'}")
        lines.append(f"cloudflared: {'OK' if result.cloudflared_exists else 'MISSING'}")
        for model_dir, found in result.models_found.items():
            lines.append(f"{model_dir}: {'OK' if found else 'MISSING'}")
        if result.errors:
            lines.append(f"Errors: {len(result.errors)}")
        self.preflight_label.setText("\n".join(lines))
        # [-----END [001]-----]

    # [-----END [060]-----]

# [-----END [100]-----]