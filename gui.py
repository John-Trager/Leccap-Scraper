from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDialog,
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


class WelcomeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lecture Scraper Info")
        self.setStyleSheet(
            """
            background-color: #f0f0f0;
            color: #333333;
            font-family: Arial;
            font-size: 14px;
        """
        )

        layout = QVBoxLayout()

        label = QLabel("Welcome to the UMich lecture scraper!")
        layout.addWidget(label)

        # Add a QTextEdit for program description
        program_description = QTextEdit()
        program_description.setReadOnly(True)
        program_description.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )
        program_description.setStyleSheet(
            """
            background-color: #f0f0f0;
            color: #333333;
            font-family: Arial;
            font-size: 14px;
            """
        )
        program_description.setText(
            "This program allows you to scrape lecture information from classes you took at UMich. "
            + "Please enter your UMich unique name and password to get started. "
            + "The program will require you to authenticate with Duo 2FA push."
            + "Please make sure you have your phone ready.\n\n"
            + "The program will scrape the lecture video links and save them to a csv file that "
            + "can later be used to download or access. The video links can be accessed directly to play the lectures "
            + "without the need for logging into your UMich account!"
        )
        layout.addWidget(program_description)
        layout.setAlignment(program_description, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lecture Scraper")
        self.resize(400, 300)

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

        # Create welcome label
        welcome_label = QLabel("Welcome to the UMich lecture scraper!")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(welcome_label)
        self.layout.setAlignment(welcome_label, Qt.AlignmentFlag.AlignCenter)

        # Username layout
        username_label = QLabel("Unique name:")
        self.username_entry = QLineEdit()
        self.username_entry.setFixedWidth(150)
        self.username_entry.setStyleSheet(
            """
            background-color: #FFFFFF;
            border: 1px solid #999999;
            border-radius: 4px;
            """
        )
        self.layout.addWidget(username_label)
        self.layout.addWidget(self.username_entry)
        self.layout.setAlignment(
            self.username_entry, Qt.AlignmentFlag.AlignCenter
        )
        self.layout.setAlignment(username_label, Qt.AlignmentFlag.AlignCenter)

        # Password layout
        password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setFixedWidth(150)
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
        self.layout.setAlignment(
            self.password_entry, Qt.AlignmentFlag.AlignCenter
        )
        self.layout.setAlignment(password_label, Qt.AlignmentFlag.AlignCenter)

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

        # add label for the program
        terminal_label = QLabel("Program Status:")
        terminal_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.layout.addWidget(terminal_label)

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

    welcome_dialog = WelcomeDialog()
    welcome_dialog.exec()

    sys.exit(app.exec())
