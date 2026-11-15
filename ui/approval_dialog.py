from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class ApprovalDialog(QDialog):
    def __init__(self, action_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ANTI-VURUS")
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QDialog { background-color: #0a0a0a; color: white; }
            QLabel { color: white; font-family: 'Segoe UI', sans-serif; }
            #title { font-size: 22px; font-weight: bold; }
            #subtitle { color: #a0a0a0; font-size: 14px; }
            #status { color: #ff9f1a; font-weight: bold; margin-top: 10px; }
            QPushButton { 
                border-radius: 10px; padding: 15px; font-size: 16px; font-weight: bold; 
            }
            #btn_accept { background-color: #1a1a1a; color: #00ff41; border: 1px solid #333; }
            #btn_accept:hover { background-color: #222; }
            #btn_reject { background-color: #1a1a1a; color: #ff3333; border: 1px solid #333; }
            #btn_reject:hover { background-color: #222; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("â ï¸ ANTI-VURUS")
        title.setObjectName("title")
        layout.addWidget(title)

        msg1 = QLabel("ÐÐ´Ð¼Ð¸Ð½Ð¸ÑÑÑÐ°ÑÐ¾Ñ Ð¿ÑÐµÐ´Ð»Ð¾Ð¶Ð¸Ð»\nÐ¸Ð·Ð¼ÐµÐ½Ð¸ÑÑ Ð½Ð°ÑÑÑÐ¾Ð¹ÐºÐ¸")
        msg1.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(msg1)

        msg2 = QLabel(f"ÐÐ·Ð¼ÐµÐ½ÐµÐ½Ð¸Ðµ: {action_text}.\n\nÐÐ½Ð¸ÑÐ¸Ð°ÑÐ¾Ñ: Ð°Ð´Ð¼Ð¸Ð½Ð¸ÑÑÑÐ°ÑÐ¾Ñ Ð¿ÑÐ¾ÐµÐºÑÐ°.")
        msg2.setTextFormat(Qt.TextFormat.PlainText)
        msg2.setObjectName("subtitle")
        layout.addWidget(msg2)

        status = QLabel("ÐÐ¶Ð¸Ð´Ð°ÐµÑ ÑÐµÑÐµÐ½Ð¸Ñ Ð¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ñ")
        status.setObjectName("status")
        layout.addWidget(status)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        
        btn_accept = QPushButton("â\nÐÑÐ¸Ð½ÑÑÑ")
        btn_accept.setObjectName("btn_accept")
        btn_accept.clicked.connect(self.accept)
        
        btn_reject = QPushButton("â\nÐÑÐºÐ»Ð¾Ð½Ð¸ÑÑ")
        btn_reject.setObjectName("btn_reject")
        btn_reject.clicked.connect(self.reject)

        btn_layout.addWidget(btn_accept)
        btn_layout.addWidget(btn_reject)
        layout.addLayout(btn_layout)

        note = QLabel("ÐÐµÐ¼Ð¾Ð½ÑÑÑÐ°ÑÐ¸Ñ Ð¾ÐºÐ½Ð°. ÐÐ½Ð¾Ð¿ÐºÐ¸ Ð¿Ð¾Ð´ÐºÐ»ÑÑÐµÐ½Ñ Ðº Ð¿ÑÐ¾Ð³ÑÐ°Ð¼Ð¼Ðµ.")
        note.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(note, alignment=Qt.AlignmentFlag.AlignCenter)
