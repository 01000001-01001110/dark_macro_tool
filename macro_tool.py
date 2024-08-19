import sys
import os
import requests
import subprocess
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QListWidget, QLineEdit, QPushButton, QMenuBar, QMenu, 
                               QApplication, QDialog, QMessageBox)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QAction
from settings_dialog import SettingsDialog
from macro_recorder import MacroRecorder
from macro_player import MacroPlayer
from macro_edit_dialog import MacroEditDialog
from database_manager import DatabaseManager
from about_dialog import AboutDialog
from styled_widgets import StylizedLineEdit, StylizedButton
from title_bar import TitleBar

class MacroTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_version = "1.0.1"
        self.github_repo = "01000001-01001110/dark_macro_tool"
        self.db_manager = DatabaseManager(app_name='MacroTool', app_author='Automate & Deploy')
        self.initUI()
        self.current_macro = None
        self.recorder = None
        self.player = None
        self.is_recording = False
        self.is_playing = False
        self.selected_app = "Select an app (optional)"
        self.loop_playback = False
        self.vary_speed = False
        self.load_macros_from_db()
        QApplication.instance().installEventFilter(self)

        # Check for updates every hour
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(3600000)  # 1 hour in milliseconds

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self, "Dark Theme Macro Tool")
        main_layout.addWidget(self.title_bar)

        menu_bar = self.create_menu_bar()
        main_layout.addWidget(menu_bar)

        content = QWidget()
        content.setObjectName("contentWidget")
        content.setStyleSheet("""
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
        content_layout = QVBoxLayout(content)

        macro_layout = QHBoxLayout()
        macro_layout.addWidget(QLabel("Macro Name:"))
        self.macro_name_input = StylizedLineEdit("Enter macro name")
        macro_layout.addWidget(self.macro_name_input)
        content_layout.addLayout(macro_layout)

        button_layout = QHBoxLayout()
        self.record_button = StylizedButton("Record")
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)

        self.play_button = StylizedButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        button_layout.addWidget(self.play_button)

        self.edit_button = StylizedButton("Edit")
        self.edit_button.clicked.connect(self.edit_macro)
        button_layout.addWidget(self.edit_button)

        self.delete_button = StylizedButton("Delete")
        self.delete_button.clicked.connect(self.delete_macro)
        button_layout.addWidget(self.delete_button)

        content_layout.addLayout(button_layout)

        self.macro_list = QListWidget()
        self.macro_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #4f545c;
                border-radius: 5px;
                padding: 5px;
                background-color: #40444b;
                color: #dcddde;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #7289da;
                color: white;
            }
        """)
        content_layout.addWidget(self.macro_list)

        main_layout.addWidget(content)

        self.setFixedSize(400, 500)

    def create_menu_bar(self):
        menu_bar = QMenuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #202225;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #7289da;
            }
            QMenu {
                background-color: #36393f;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #7289da;
            }
        """)

        file_menu = menu_bar.addMenu("File")
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings)

        update_action = file_menu.addAction("Check for Updates")
        update_action.triggered.connect(self.check_for_updates)

        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.open_about)

        return menu_bar

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.app_selector.setCurrentText(self.selected_app)
        settings_dialog.loop_checkbox.setChecked(self.loop_playback)
        settings_dialog.vary_speed_checkbox.setChecked(self.vary_speed)
        if settings_dialog.exec() == QDialog.Accepted:
            self.selected_app = settings_dialog.app_selector.currentText()
            self.loop_playback = settings_dialog.loop_checkbox.isChecked()
            self.vary_speed = settings_dialog.vary_speed_checkbox.isChecked()
            print(f"Settings Updated: App: {self.selected_app}, Loop: {self.loop_playback}, Vary Speed: {self.vary_speed}")

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def check_for_updates(self):
        try:
            api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            if self._compare_versions(latest_version, self.current_version):
                reply = QMessageBox.question(self, 'Update Available', 
                                             f"A new version {latest_version} is available. Would you like to update now?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self._start_update_process(latest_release['assets'][0]['browser_download_url'])
            else:
                QMessageBox.information(self, 'No Updates', "You're running the latest version.")
        except requests.RequestException as e:
            QMessageBox.warning(self, 'Update Check Failed', f"Failed to check for updates: {str(e)}")

    def _compare_versions(self, version1, version2):
        v1_parts = [int(part) for part in version1.split('.')]
        v2_parts = [int(part) for part in version2.split('.')]
        return v1_parts > v2_parts

    def _start_update_process(self, download_url):
        updater_path = os.path.join(os.path.dirname(sys.executable), "updater.exe")
        if not os.path.exists(updater_path):
            QMessageBox.warning(self, 'Update Failed', "Updater not found. Please reinstall the application.")
            return

        # Start the updater process
        subprocess.Popen([updater_path, download_url, sys.executable])
        
        # Close the current application
        QMessageBox.information(self, 'Updating', "The application will now close and update. Please restart it after the update is complete.")
        self.close()
        sys.exit(0)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recorder = MacroRecorder()
        self.recorder.finished.connect(self.on_recording_finished)
        self.recorder.start()
        self.is_recording = True
        self.record_button.setText("Stop")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #f04747;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d84040;
            }
            QPushButton:pressed {
                background-color: #c43535;
            }
        """)

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
        self.is_recording = False
        self.record_button.setText("Record")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #7289da;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #677bc4;
            }
            QPushButton:pressed {
                background-color: #5b6eae;
            }
        """)

    def on_recording_finished(self, macro):
        self.current_macro = macro
        name = self.macro_name_input.text()
        if name:
            self.save_macro_to_db(name, self.current_macro)
            self.macro_name_input.clear()
            print(f"Macro '{name}' saved successfully")
        else:
            print("Unable to save macro: No name provided")

    def toggle_playback(self):
        if not self.is_playing:
            self.start_playback()
        else:
            self.stop_playback()

    def start_playback(self):
        item = self.macro_list.currentItem()
        if item:
            name = item.text()
            macro = self.db_manager.get_macro(name)
            if macro:
                self.current_macro = macro
                self.play_button.setText("Stop")
                self.is_playing = True
                self.player = MacroPlayer(self.current_macro, self.selected_app, self.loop_playback, self.vary_speed)
                self.player.finished.connect(self.on_playback_finished)
                self.player.start()
                
                # Set button style for active state
                self.play_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f04747;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #d84040;
                    }
                    QPushButton:pressed {
                        background-color: #c43535;
                    }
                """)

    def stop_playback(self):
        if self.is_playing and self.player:
            self.player.terminate()
            self.on_playback_finished()

    def on_playback_finished(self):
        self.play_button.setText("Play")
        self.is_playing = False
        self.player = None
        
        # Reset button style
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #7289da;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #677bc4;
            }
            QPushButton:pressed {
                background-color: #5b6eae;
            }
        """)

    def edit_macro(self):
        item = self.macro_list.currentItem()
        if item:
            name = item.text()
            macro = self.db_manager.get_macro(name)
            if macro:
                dialog = MacroEditDialog(macro, self)
                if dialog.exec() == QDialog.Accepted:
                    self.save_macro_to_db(name, dialog.macro)

    def delete_macro(self):
        item = self.macro_list.currentItem()
        if item:
            name = item.text()
            self.db_manager.delete_macro(name)
            self.load_macros_from_db()

    def load_macros_from_db(self):
        self.macros = self.db_manager.get_all_macros()
        self.update_macro_list()

    def save_macro_to_db(self, name, macro):
        self.db_manager.save_macro(name, macro)
        self.load_macros_from_db()

    def update_macro_list(self):
        self.macro_list.clear()
        for name in self.macros:
            self.macro_list.addItem(name)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
            return True  # Consume spacebar events
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        QApplication.instance().removeEventFilter(self)
        if self.recorder:
            self.recorder.stop()
        if self.player:
            self.player.terminate()
            self.player.wait()
        self.db_manager.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MacroTool()
    ex.show()
    sys.exit(app.exec())