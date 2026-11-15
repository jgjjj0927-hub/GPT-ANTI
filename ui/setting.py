from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton
from PyQt6.QtCore import pyqtSignal
from core.config import load_config, save_config
from ui.approval_dialog import ApprovalDialog


class SettingsTab(QWidget):
    rt_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cfg = load_config()
        layout = QVBoxLayout(self)
        self.rt_cb = QCheckBox("Защита в реальном времени (RT)")
        self.rt_cb.setChecked(self.cfg.get("rt_enabled", True))
        self.rt_cb.toggled.connect(self._save_rt)
        layout.addWidget(self.rt_cb)
        demo_button = QPushButton("Запросить подтверждение изменения (демо)")
        demo_button.clicked.connect(self._show_approval)
        layout.addWidget(demo_button)
        layout.addStretch()

    def _save_rt(self, enabled):
        self.cfg["rt_enabled"] = bool(enabled)
        save_config(self.cfg)
        self.rt_changed.emit(bool(enabled))

    def _show_approval(self):
        dlg = ApprovalDialog("настройки защиты", self)
        if dlg.exec():
            self.rt_cb.setChecked(True)
