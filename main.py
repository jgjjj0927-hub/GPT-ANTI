import sys
import threading
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from telegram.bot import poll_loop


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ANTI-VURUS")
    stop_bot = threading.Event()
    bot_thread = threading.Thread(target=poll_loop, args=(stop_bot,), daemon=True, name="telegram-admin-bot")
    bot_thread.start()
    window = MainWindow()
    window.show()
    try:
        return app.exec()
    finally:
        stop_bot.set()
        bot_thread.join(timeout=2)


if __name__ == "__main__":
    sys.exit(main())
