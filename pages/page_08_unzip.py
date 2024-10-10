import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import zipfile
from queue import Queue

from helpers.functions import get_filepath_for_executable, make_path_os_safe, set_target_folder
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons, go_to_next_page


class UnzipPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the UnzipPage frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.log_queue = Queue()  # Queue to hold log messages
        self.setup_ui()
        self.poll_log_queue()  # Start polling the log queue
        self.participant_folders = []
        self.unzip_done = False

    def setup_ui(self):
        """
        Setup the user interface components for the UnzipPage frame.
        """
        # Header
        header = HeaderComponent(self, filename=__file__, step_name="Unzip column files")
        header.pack(fill='x')

        # Title Label
        self.title_label = tk.Label(self, text="Unzip Downloaded Data", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # Instructions text
        self.text_box = tk.Text(self, height=5, width=60, wrap="word", font=("Helvetica", 12))
        self.text_box.insert("end", "Please navigate to and select the 'pulled-data' directory, which contains the files you need to unzip."
                             "Ensure you are in the 'pulled-data' folder, not inside any individual participant folders."
                             "Once you have confirmed that you are in the correct directory, click 'OK' to proceed.")
        self.text_box.config(state="disabled", bg="#f0f0f0", relief="flat")
        self.text_box.pack(pady=10)

        # Button to select the download folder
        self.select_folder_button = tk.Button(self, text="Select Download Folder", command=self.select_download_folder)
        self.select_folder_button.pack(pady=10)

        # Log display
        self.log_display = tk.Text(self, height=15, state='disabled', wrap='word')
        self.log_display.pack(pady=10, padx=10, fill='both', expand=True)

        # Scrollbar for the log display
        self.log_scrollbar = ttk.Scrollbar(self.log_display, orient='vertical', command=self.log_display.yview)
        self.log_scrollbar.pack(side='right', fill='y')
        self.log_display.config(yscrollcommand=self.log_scrollbar.set)

        get_navigation_buttons(self, "unzip_page", next_button_name="Start Unzipping", skip_button_name="Skip Unzipping", skip_to_page="combine_columns_introduction_page")

    def on_next_page(self):
        return self.start_unzipping()

    def select_download_folder(self):
        """
        Open a dialog for user to select a folder, and enable the start unzipping process.
        """
        self.download_folder = filedialog.askdirectory(title='Select Research Data Download Folder To Unzip')
        self.download_folder = make_path_os_safe(self.download_folder)
        if self.download_folder:
            self.log(f"Selected folder: {self.download_folder}")
            set_target_folder(self.download_folder)

    def run_unzipping(self):
        """
        Manage the unzipping process by renaming and unzipping files.
        """
        self.participant_folders = [participant_folder for participant_folder in os.listdir(self.download_folder)
                                    if participant_folder.startswith("HBU")]
        self.rename_to_zip(self.download_folder)
        self.unzip_files(self.download_folder)
        self.log("Unzipping finished!")

        confirm = messagebox.askyesno("Unzipping finished!", "Go to next page?")
        if confirm:
            self.unzip_done = True
            go_to_next_page(self, 'unzip_page')
        else:
            self.unzip_done = True

    def start_unzipping(self):
        """
        Start the unzipping process after user confirmation.
        """
        if self.unzip_done:
            confirm = messagebox.askyesno("Unzipping finished!", "Go to next page?")
            if confirm:
                go_to_next_page(self)

        confirm = messagebox.askyesno("Confirm", "Start the unzipping process?")
        if confirm:
            threading.Thread(target=self.run_unzipping).start()
        else:
            self.log("Unzipping cancelled by user.")

    def log(self, message):
        """
        Log a message to the log queue.

        Args:
            message (str): The message to log.
        """
        self.log_queue.put(message)

    def poll_log_queue(self):
        """
        Periodically poll the log queue and update the log display with new messages.
        """
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_display.config(state='normal')
            self.log_display.insert('end', message + "\n")
            self.log_display.config(state='disabled')
            self.log_display.see('end')
        self.after(100, self.poll_log_queue)

    def rename_to_zip(self, download_folder):
        """
        Rename all eligible files in the specified folder to '.zip' extensions.

        Args:
            download_folder (str): The path of the folder containing files to rename.
        """
        self.log("Started renaming files to .zip")
        total_renamed = 1
        total_participants = 1
        total = len(self.participant_folders)
        for participant_folder in self.participant_folders:
            files_to_rename = []

            participant_folder_path = os.path.join(download_folder, participant_folder)
            participant_folder_path = get_filepath_for_executable(participant_folder_path)

            if os.path.isdir(participant_folder_path):
                self.log(f"({total_participants}/{total}) - Searching .zip files for participant '{participant_folder}'")
                files = [f for f in os.listdir(participant_folder_path) if "." not in f and not os.path.isdir(os.path.join(participant_folder_path, f))]
                files_to_rename.extend(files)

            for file in files_to_rename:
                total_renamed += 1
                original_filepath = os.path.join(participant_folder_path, file)
                original_filepath = get_filepath_for_executable(original_filepath)
                new_filepath = f"{original_filepath}.zip"
                new_filepath = get_filepath_for_executable(new_filepath)
                os.rename(original_filepath, new_filepath)

            total_participants += 1

        self.log(f"({total}/{total}) - Completed renaming files to .zip, total files renamed: {total_renamed}")
        self.log("Hold on, we're almost halfway in the unzipping process!")

    def unzip_files(self, download_folder):
        """
        Unzip all files with '.zip' extensions within the specified folder.

        Args:
            download_folder (str): The path of the folder containing '.zip' files to unzip.
        """
        total = len(self.participant_folders) + 1
        total_unzipped = 1
        for participant_folder in self.participant_folders:
            participant_folder_path = os.path.join(download_folder, participant_folder)
            participant_folder_path = get_filepath_for_executable(participant_folder_path)
            if os.path.isdir(participant_folder_path):
                zip_files = [f for f in os.listdir(participant_folder_path) if f.endswith('.zip')]
                for item in zip_files:
                    item_path = os.path.join(participant_folder_path, item)
                    item_path = get_filepath_for_executable(item_path)
                    new_filename = item.replace(".zip", "")
                    new_filepath = os.path.join(participant_folder_path, new_filename)
                    new_filepath = get_filepath_for_executable(new_filepath)
                    try:
                        with zipfile.ZipFile(item_path, 'r') as zip_ref:
                            zip_ref.extractall(new_filepath)
                    except Exception as e:
                        self.log(f"Error unzipping {item_path}: {e}")

                total_unzipped += 1
                self.log(f"({total_unzipped}/{total}) - Unzipped .zip files from participant '{participant_folder}'")
