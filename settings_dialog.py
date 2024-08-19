import psutil
import pygetwindow as gw
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QCheckBox, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
from title_bar import TitleBar

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 220)  # Adjusted height

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)  # Set spacing to 0 to remove gaps

        self.title_bar = TitleBar(self, "Settings")
        main_layout.addWidget(self.title_bar)

        content = QWidget()
        content.setObjectName("contentWidget")
        content.setStyleSheet("""
            QWidget#contentWidget {
                background-color: #36393f;
                color: #dcddde;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QLabel, QCheckBox, QComboBox {
                color: #dcddde;
            }
            QComboBox {
                border: 2px solid #4f545c;
                border-radius: 5px;
                padding: 5px;
                background-color: #40444b;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #4f545c;
                selection-background-color: #7289da;
            }
            QPushButton {
                background-color: #7289da;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #677bc4;
            }
            QPushButton:pressed {
                background-color: #5b6eae;
            }
        """)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        content_layout.addWidget(QLabel("Select Target Application:"))
        self.app_selector = QComboBox()
        self.populate_running_apps()
        content_layout.addWidget(self.app_selector)

        self.loop_checkbox = QCheckBox("Enable Loop Playback")
        content_layout.addWidget(self.loop_checkbox)

        self.vary_speed_checkbox = QCheckBox("Vary Input Speed")
        content_layout.addWidget(self.vary_speed_checkbox)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        content_layout.addLayout(button_layout)

        main_layout.addWidget(content)

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def populate_running_apps(self):
        """Populate the QComboBox with the names of running applications with visible windows."""
        self.app_selector.addItem("Select an app (optional)")
        visible_windows = gw.getAllTitles()
        visible_windows = [title for title in visible_windows if title]  # Filter out empty titles
        for title in visible_windows:
            if title not in self.app_selector.currentText():
                self.app_selector.addItem(title)