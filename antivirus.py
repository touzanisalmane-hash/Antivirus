import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QProgressBar,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
)

DANGEROUS_EXTENSIONS = [".exe", ".bat", ".cmd", ".vbs", ".js", ".scr", ".ps1"]
MAX_SIZE_BYTES = 100 * 1024 * 1024


class AntivirusApp(QWidget):

    def __init__(self):
        super().__init__()
        self.suspicious_files = []
        self.selected_folder = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Antivirus")
        self.resize(500, 500)

        self.title_label = QLabel("Antivirus")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)

        self.folder_label = QLabel("No folder selected")

        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.scan_folder)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.result_list = QListWidget()
        self.result_list.setSelectionMode(QListWidget.ExtendedSelection)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)

        self.status_label = QLabel("Status: waiting for scan...")

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.select_folder_button)
        layout.addWidget(self.folder_label)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.result_list)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose a folder to scan")

        if folder == "":
            return

        self.selected_folder = folder
        self.folder_label.setText("Folder: " + folder)

    def is_dangerous_extension(self, file_name):
        for extension in DANGEROUS_EXTENSIONS:
            if file_name.lower().endswith(extension):
                return True
        return False

    def scan_folder(self):
        if self.selected_folder == "":
            QMessageBox.information(self, "No folder", "Please select a folder first.")
            return

        self.result_list.clear()
        self.suspicious_files = []
        self.progress_bar.setValue(0)

        all_files = []
        for current_folder, subfolders, files in os.walk(self.selected_folder):
            for file_name in files:
                full_path = os.path.join(current_folder, file_name)
                all_files.append(full_path)

        total_files = len(all_files)

        if total_files == 0:
            self.status_label.setText("Status: no files found in this folder.")
            return

        scanned_count = 0
        suspicious_count = 0

        for full_path in all_files:
            try:
                file_name = os.path.basename(full_path)
                file_size = os.path.getsize(full_path)
                is_suspicious = False

                if self.is_dangerous_extension(file_name):
                    is_suspicious = True

                if file_size == 0:
                    is_suspicious = True

                if file_size > MAX_SIZE_BYTES:
                    is_suspicious = True

                if is_suspicious:
                    self.suspicious_files.append(full_path)
                    self.result_list.addItem(full_path)
                    suspicious_count = suspicious_count + 1

            except Exception as error:
                print("Error checking file:", full_path, "-", error)

            scanned_count = scanned_count + 1
            progress_percent = int((scanned_count / total_files) * 100)
            self.progress_bar.setValue(progress_percent)
            QApplication.processEvents()

        self.status_label.setText(
            "Status: scanned " + str(scanned_count) + " files, found "
            + str(suspicious_count) + " suspicious files."
        )

    def delete_selected(self):
        selected_items = self.result_list.selectedItems()

        if len(selected_items) == 0:
            QMessageBox.information(self, "Nothing selected", "Please select at least one file to delete.")
            return

        question = "Are you sure you want to delete " + str(len(selected_items)) + " file(s)?"
        answer = QMessageBox.question(
            self, "Confirm delete", question, QMessageBox.Yes | QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        deleted_count = 0

        for item in selected_items:
            file_path = item.text()

            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count = deleted_count + 1

                    row = self.result_list.row(item)
                    self.result_list.takeItem(row)

                    if file_path in self.suspicious_files:
                        self.suspicious_files.remove(file_path)

            except Exception as error:
                print("Error deleting file:", file_path, "-", error)

        self.status_label.setText("Status: deleted " + str(deleted_count) + " file(s).")
        QMessageBox.information(self, "Done", "Deleted " + str(deleted_count) + " file(s).")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AntivirusApp()
    window.show()
    sys.exit(app.exec_())