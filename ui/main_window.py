from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from ui.scan_tab import ScanTab
from ui.quarantine_tab import QuarantineTab
from ui.setting import SettingsTab
from ui.about_tab import AboutTab
from core.protection import RealTimeProtection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANTI-VURUS")
        self.resize(900, 650)
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #0a0a0a; color: white; font-family: 'Segoe UI', Arial; }
            QLabel { color: white; }
            QPushButton { background-color: #1a1a1a; color: white; border: 1px solid #333; border-radius: 8px; padding: 8px 15px; }
            QPushButton:hover { background-color: #252525; }
            QCheckBox { color: white; font-size: 14px; }
            QTabWidget::pane { border: 1px solid #222; background: #111; border-radius: 10px; margin: 5px; }
            QTabBar::tab { background: #0a0a0a; color: #888; padding: 10px 20px; border: 1px solid #222; border-radius: 8px; margin: 2px; }
            QTabBar::tab:selected { background: #1a1a1a; color: #00ff41; font-weight: bold; border: 1px solid #333; }
        """)
        central = QWidget()
        layout = QVBoxLayout(central)
        header = QLabel("ANTI-VURUS")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(header)
        tabs = QTabWidget()
        self.scan_tab = ScanTab()
        self.settings_tab = SettingsTab()
        tabs.addTab(self.scan_tab, "Ð¡ÐºÐ°Ð½Ð¸ÑÐ¾Ð²Ð°Ð½Ð¸Ðµ")
        tabs.addTab(QuarantineTab(), "ÐÐ°ÑÐ°Ð½ÑÐ¸Ð½")
        tabs.addTab(self.settings_tab, "ÐÐ°ÑÑÑÐ¾Ð¹ÐºÐ¸")
        tabs.addTab(AboutTab(), "Ð Ð¿ÑÐ¾Ð³ÑÐ°Ð¼Ð¼Ðµ")
        layout.addWidget(tabs)
        self.setCentralWidget(central)
        self.rtp = RealTimeProtection()
        self.settings_tab.rt_changed.connect(self._set_realtime)
        self.rtp.start()

    def _set_realtime(self, enabled: bool):
        if enabled:
            self.rtp.start()
        else:
            self.rtp.stop()

    def closeEvent(self, event):
        self.rtp.stop()
        super().closeEvent(event)
