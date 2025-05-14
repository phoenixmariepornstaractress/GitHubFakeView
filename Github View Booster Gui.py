import sys
import threading
import gettext
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTextEdit, QMessageBox, QSpinBox, QProgressBar, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from github_view_booster import GitHubViewBooster

# Internationalization setup
gettext.bindtextdomain('messages', 'locale')
gettext.textdomain('messages')
_ = gettext.gettext

class SignalEmitter(QObject):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    progress_signal = pyqtSignal(int)

class BoosterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("GitHub View Booster"))
        self.setGeometry(200, 150, 700, 520)
        self.setStyleSheet(self.style_sheet())

        self.signals = SignalEmitter()
        self.signals.log_signal.connect(self.append_log)
        self.signals.finished_signal.connect(self.on_finished)
        self.signals.progress_signal.connect(self.update_progress)

        self.setup_ui()

    def style_sheet(self):
        return """
            QWidget {
                background-color: #fdfdfd;
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                margin: 4px 0;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004d99;
            }
            QLineEdit, QTextEdit, QSpinBox {
                background-color: #fff;
                border: 1px solid #bbb;
                padding: 5px;
                border-radius: 3px;
            }
            QProgressBar {
                height: 18px;
                border: 1px solid #888;
                border-radius: 4px;
                background-color: #eaeaea;
            }
            QProgressBar::chunk {
                background-color: #3399ff;
                width: 12px;
            }
        """

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addLayout(self.create_input_layout(_("GitHub Repo URL:"), self.url_input := QLineEdit()))
        layout.addLayout(self.create_input_layout(_("Number of Views:"), self.count_input := QSpinBox()))
        self.count_input.setRange(1, 1000)

        layout.addWidget(self.create_advanced_options())
        layout.addLayout(self.create_button_layout())
        layout.addWidget(QLabel(_("Progress:")))
        layout.addWidget(self.progress_bar := QProgressBar())
        self.progress_bar.setValue(0)

        layout.addWidget(QLabel(_("Log Output:")))
        layout.addWidget(self.log_output := QTextEdit(readOnly=True))

        self.setLayout(layout)

    def create_input_layout(self, label_text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        return layout

    def create_advanced_options(self):
        group = QGroupBox(_("Advanced Configuration"))
        layout = QVBoxLayout()
        self.hide_report_checkbox = QCheckBox(_("Hide report file after completion"))
        self.verbose_logs_checkbox = QCheckBox(_("Enable verbose logging"))
        layout.addWidget(self.hide_report_checkbox)
        layout.addWidget(self.verbose_logs_checkbox)
        group.setLayout(layout)
        return group

    def create_button_layout(self):
        layout = QHBoxLayout()
        self.start_button = QPushButton(_("Start Boosting"))
        self.start_button.clicked.connect(self.start_boosting)
        layout.addStretch()
        layout.addWidget(self.start_button)
        return layout

    def start_boosting(self):
        url = self.url_input.text().strip()
        count = self.count_input.value()

        if not url:
            QMessageBox.warning(self, _("Input Required"), _("Please enter a valid GitHub repository URL."))
            return

        self.start_button.setEnabled(False)
        self.progress_bar.setMaximum(count)
        self.progress_bar.setValue(0)
        self.log_output.clear()
        self.append_log(_("Launching view boosting..."))

        threading.Thread(target=self.execute_boosting, args=(url, count), daemon=True).start()

    def execute_boosting(self, url, count):
        booster = GitHubViewBooster(url, count)

        if not booster.validate_url() or not booster.is_valid_github_repo():
            self.signals.log_signal.emit(_("Error: Invalid or unreachable GitHub repository URL."))
            self.signals.finished_signal.emit()
            return

        for i in range(count):
            booster.send_fake_views(delay_range=(0.1, 0.3))
            self.signals.progress_signal.emit(i + 1)
            if self.verbose_logs_checkbox.isChecked():
                self.signals.log_signal.emit(_(f"View {i + 1} of {count} completed."))

        booster.save_report()
        if self.hide_report_checkbox.isChecked():
            booster.hide_report_file()

        self.signals.log_signal.emit(_("✅ Boosting completed successfully."))
        for log in booster.get_recent_logs(10):
            self.signals.log_signal.emit(log)
        self.signals.finished_signal.emit()

    def append_log(self, message):
        self.log_output.append(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self):
        self.start_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = BoosterGUI()
    gui.show()
    sys.exit(app.exec_())
