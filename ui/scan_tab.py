from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from core.scanner import ScanEngine
from core.quarantine import add_to_quarantine


class ScanTab(QWidget):
    found_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int)
    done_signal = pyqtSignal(object, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target = ""
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.path_lbl = QLabel("Цель: не выбрана")
        top.addWidget(self.path_lbl, 1)
        self.btn_folder = QPushButton("Выбрать папку")
        self.btn_folder.clicked.connect(self._choose_folder)
        top.addWidget(self.btn_folder)
        self.btn_file = QPushButton("Выбрать файл")
        self.btn_file.clicked.connect(self._choose_file)
        top.addWidget(self.btn_file)
        layout.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.results = QListWidget()
        layout.addWidget(self.results, 1)
        buttons = QHBoxLayout()
        self.btn_scan = QPushButton("Сканировать")
        self.btn_scan.clicked.connect(self._start_scan)
        buttons.addWidget(self.btn_scan)
        self.btn_stop = QPushButton("Стоп")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_scan)
        buttons.addWidget(self.btn_stop)
        self.btn_quarantine = QPushButton("В карантин")
        self.btn_quarantine.clicked.connect(self._to_quarantine)
        buttons.addWidget(self.btn_quarantine)
        layout.addLayout(buttons)
        self.engine = ScanEngine(
            progress_cb=self.progress_signal.emit,
            found_cb=self.found_signal.emit,
            done_cb=self.done_signal.emit,
        )
        self.found_signal.connect(self._add_result)
        self.progress_signal.connect(self.progress.setValue)
        self.done_signal.connect(self._on_done)

    def _choose_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if path:
            self.target = path
            self.path_lbl.setText(f"Цель: {path}")

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if path:
            self.target = path
            self.path_lbl.setText(f"Цель: {path}")

    def _start_scan(self):
        if not self.target:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку или файл.")
            return
        self.results.clear()
        self.progress.setValue(0)
        try:
            started = self.engine.start(self.target)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return
        if started:
            self.btn_scan.setEnabled(False)
            self.btn_stop.setEnabled(True)

    def _stop_scan(self):
        self.engine.stop()
        self.btn_stop.setEnabled(False)

    def _add_result(self, threat):
        item = QListWidgetItem(f"[{threat['severity']}] {threat['name']} — {threat['reason']}")
        item.setData(Qt.ItemDataRole.UserRole, threat)
        self.results.addItem(item)

    def _on_done(self, found, stopped):
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.results.addItem("— Остановлено —" if stopped else f"— Завершено. Найдено: {len(found)} —")
        if not stopped:
            self.progress.setValue(100)

    def _to_quarantine(self):
        item = self.results.currentItem()
        if item is None:
            return
        threat = item.data(Qt.ItemDataRole.UserRole)
        if threat and add_to_quarantine(threat):
            QMessageBox.information(self, "Карантин", "Файл перемещён в карантин.")
            self.results.takeItem(self.results.row(item))
        else:
            QMessageBox.warning(self, "Карантин", "Не удалось переместить файл. Возможно, он уже изменён или недоступен.")
