import requests
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QFont
from PySide6.QtCore import Qt
from styled_widgets import StylizedButton
from title_bar import TitleBar

class CircularImageLabel(QLabel):
    def __init__(self, pixmap):
        super().__init__()
        self.setFixedSize(80, 80)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = TitleBar(self, "About iNet's")
        self.main_layout.addWidget(self.title_bar)

        self.content = QWidget()
        self.content.setObjectName("contentWidget")
        self.content.setStyleSheet("""
            QWidget#contentWidget {
                background-color: #36393f;
                color: #dcddde;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(10)  
        self.content_layout.setContentsMargins(20, 20, 20, 20)  # Add some padding

        self.download_image()

        self.setFixedSize(300, 300)

    def download_image(self):
        url = "https://cdn.discordapp.com/attachments/1201040962135273513/1267203510769025045/inet0_Logo_2dsvg_tiny_cute_blue_and_purple_ticket_robot_eb6ac3a6-b33b-4bc9-8f7a-35257be74751.png?ex=66a7eebc&is=66a69d3c&hm=9a3b90d36476e6438f93bb4cf47aca7f65c7fafd730f7f68e0d46004a09332d1&"
        response = requests.get(url)
        if response.status_code == 200:
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.setup_ui(pixmap)
        else:
            print(f"Failed to download image: {response.status_code}")
            self.setup_ui(QPixmap())

    def setup_ui(self, avatar_pixmap):
        # Avatar and app name
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)  
        avatar_label = CircularImageLabel(avatar_pixmap)
        top_layout.addWidget(avatar_label)
        
        app_name_label = QLabel("Dark Macro Tool")
        app_name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_layout.addWidget(app_name_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_layout.addStretch()

        self.content_layout.addLayout(top_layout)

        # Description
        description_label = QLabel("Just another tool for recording and playing macros written in Python.")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(description_label)

        # WebLink
        link_label = QLabel('<a href="https://github.com/01000001-01001110" style="color: #7289da;">01000001-01001110</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(link_label)

        # Discord Link
        link_label = QLabel('<a href="https://discord.gg/sCfj8c9CcK" style="color: #7289da;">Join my Discord for support.</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(link_label)

        # Copyright
        copyright_label = QLabel("©2023 01000001-01001110. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(copyright_label)

        self.content_layout.addStretch()  # Push everything up

        # Close button
        close_button = StylizedButton("Close")
        close_button.clicked.connect(self.accept)
        self.content_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.content)

    def showEvent(self, event):
        super().showEvent(event)
        screen = self.screen().geometry()
        self.move(screen.center() - self.rect().center())