from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt
from core.quarantine import list_quarantine, restore_file, delete_permanently


class QuarantineTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list, 1)
        buttons = QHBoxLayout()
        refresh = QPushButton("Обновить")
        refresh.clicked.connect(self.refresh)
        buttons.addWidget(refresh)
        restore = QPushButton("Восстановить")
        restore.clicked.connect(self._restore)
        buttons.addWidget(restore)
        delete = QPushButton("Удалить навсегда")
        delete.clicked.connect(self._delete)
        buttons.addWidget(delete)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self):
        self.list.clear()
        for index, record in enumerate(list_quarantine()):
            name = str(record.get("name", "unknown"))
            date = str(record.get("date_added", ""))[:16]
            path = str(record.get("path", ""))
            item = QListWidgetItem(f"{name} | {date} | {path}")
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.list.addItem(item)

    def _selected_index(self):
        item = self.list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _restore(self):
        index = self._selected_index()
        if index is not None and restore_file(index):
            self.refresh()
            QMessageBox.information(self, "Карантин", "Файл восстановлен.")
        elif index is not None:
            QMessageBox.warning(self, "Карантин", "Не удалось восстановить файл.")

    def _delete(self):
        index = self._selected_index()
        if index is None:
            return
        answer = QMessageBox.question(self, "Подтверждение", "Удалить выбранный файл без возможности восстановления?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        if delete_permanently(index):
            self.refresh()
            QMessageBox.information(self, "Карантин", "Файл удалён.")
        else:
            QMessageBox.warning(self, "Карантин", "Не удалось удалить файл.")
