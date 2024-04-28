from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
)
from PyQt6.QtGui import QTextCursor

from PyQt6.QtCore import Qt, QThread, pyqtSignal
import time
import sys

from scraper import Scraper


class Worker(QThread):
    """Worker thread demo for long-running tasks."""

    output = pyqtSignal(str)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        # Simulate some long-running process
        for i in range(5):
            time.sleep(1)
            self.output.emit(f"Output {i}\n")
        self.finished.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lecture Scraper")
        self.resize(300, 200)

        self.initUI()

    def initUI(self):
        self.setStyleSheet(
            """
            background-color: #f0f0f0;
            color: #333333;
            font-family: Arial;
            font-size: 14px;
        """
        )

        self.layout = QVBoxLayout()

        # Username layout
        username_label = QLabel("Unique name:")
        self.username_entry = QLineEdit()
        self.username_entry.setFixedWidth(300)
        self.username_entry.setStyleSheet(
            """
            background-color: #FFFFFF;
            border: 1px solid #999999;
            border-radius: 4px;
            """
        )
        self.layout.addWidget(username_label)
        self.layout.addWidget(self.username_entry)

        # Password layout
        password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setFixedWidth(300)
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setStyleSheet(
            """
            background-color: #FFFFFF;
            border: 1px solid #999999;
            border-radius: 4px;
            """
        )
        self.layout.addWidget(password_label)
        self.layout.addWidget(self.password_entry)

        # Start button
        self.button = QPushButton("Start")
        self.button.setFixedWidth(100)
        self.button.setStyleSheet(
            """
            background-color: #f0f0f0;
            color: black;
            border: 1px solid #999999;
            padding: 5px 10px;
            font-size: 16px;
            border-radius: 4px;
            """
        )
        self.button.clicked.connect(self.start)
        self.layout.addWidget(self.button)
        self.layout.setAlignment(self.button, Qt.AlignmentFlag.AlignCenter)

        # add terminal like window to show progress of the scraper
        self.terminal_box = QTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.layout.addWidget(self.terminal_box)
        self.terminal_box.setStyleSheet(
            """
            background-color: #FFFFFF;
            border: 1px solid #999999;
            border-radius: 4px;
            """
        )
        self.layout.addWidget(self.terminal_box)

        # keep at the end
        self.setLayout(self.layout)

    def start(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        # print(f"Username: {username}, Password: {password}")

        self.disabled_form()

        # start the worker

        # self.worker = Worker(username, password)
        self.worker = Scraper(username, password)
        self.worker.output.connect(self.update_terminal)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def update_terminal(self, text):
        self.terminal_box.moveCursor(QTextCursor.MoveOperation.End)
        self.terminal_box.insertPlainText(text)

    def worker_finished(self):
        self.enabled_form()

    def enabled_form(self):
        """Enable the form and button."""
        self.button.setEnabled(True)
        self.button.setText("Start")
        self.button.setStyleSheet(
            """
            background-color: #f0f0f0;
            color: black;
            border: 1px solid #999999;
            padding: 5px 10px;
            font-size: 16px;
            border-radius: 4px;
            """
        )

        self.username_entry.setEnabled(True)
        self.password_entry.setEnabled(True)

    def disabled_form(self):
        """Disable the form and button."""
        self.button.setEnabled(False)
        self.button.setText("Running...")
        # Change the appearance of the button to indicate it's disabled
        self.button.setStyleSheet(
            """
            background-color: #CCCCCC; /* Change background color to gray */
            color: #999999; /* Change text color to lighter gray */
            border: none;
            padding: 5px 10px;
            font-size: 16px;
            border-radius: 4px;
            """
        )
        self.username_entry.setEnabled(False)
        self.username_entry.clear()
        self.password_entry.setEnabled(False)
        self.password_entry.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
