import sys
import os
import requests
import time
import subprocess
from PySide6.QtWidgets import QApplication, QProgressDialog
from PySide6.QtCore import Qt, QThread, Signal

class DownloadThread(QThread):
    progress = Signal(int)
    finished = Signal(bool)

    def __init__(self, url, path):
        super().__init__()
        self.url = url
        self.path = path

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            wrote = 0

            with open(self.path, 'wb') as f:
                for data in response.iter_content(block_size):
                    wrote = wrote + len(data)
                    f.write(data)
                    if total_size > 0:
                        self.progress.emit(int(wrote / total_size * 100))

            self.finished.emit(True)
        except Exception:
            self.finished.emit(False)

class Updater(QApplication):
    def __init__(self, args):
        super().__init__(args)
        
        if len(args) < 3:
            print("Usage: updater.exe <download_url> <current_exe_path>")
            sys.exit(1)

        self.download_url = args[1]
        self.current_exe_path = args[2]
        self.new_exe_path = self.current_exe_path + ".new"

        self.progress_dialog = QProgressDialog("Downloading update...", "Cancel", 0, 100)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Updating")
        
        self.download_thread = DownloadThread(self.download_url, self.new_exe_path)
        self.download_thread.progress.connect(self.progress_dialog.setValue)
        self.download_thread.finished.connect(self.on_download_finished)
        
        self.download_thread.start()
        self.progress_dialog.show()

    def on_download_finished(self, success):
        self.progress_dialog.close()
        if success:
            self.replace_and_restart()
        else:
            print("Download failed")
            sys.exit(1)

    def replace_and_restart(self):
        try:
            # Wait for the original process to exit
            time.sleep(2)
            
            # Replace the old executable with the new one
            os.replace(self.new_exe_path, self.current_exe_path)
            
            # Start the new version
            subprocess.Popen([self.current_exe_path])
            
            # Exit the updater
            sys.exit(0)
        except Exception as e:
            print(f"Error during update: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    updater = Updater(sys.argv)
    sys.exit(updater.exec())