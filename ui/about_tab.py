from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from core.config import APP_NAME, APP_VERSION, get_pc_name


class AboutTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(QLabel(f"<h1>{APP_NAME} {APP_VERSION}</h1>"))
        layout.addWidget(QLabel("Демонстрационный эвристический сканер. Он не заменяет полноценный антивирус."))
        layout.addWidget(QLabel(f"Компьютер: {get_pc_name()}"))
        site = QLabel('Сайт: <a href="https://jgjjj0927-hub.github.io/ANTO/">jgjjj0927-hub.github.io/ANTO</a>')
        site.setOpenExternalLinks(True)
        layout.addWidget(site)
        layout.addWidget(QLabel("Поддержка: @chameleonAnti"))
        layout.addStretch(1)
