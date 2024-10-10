import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from helpers.functions import (
    get_filepath_for_executable, get_target_folder, set_target_folder,
    get_resume_download, set_resume_download
)
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class DownloadFolderSelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the download folder selection page frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.can_continue = False

        header = HeaderComponent(self, filename=__file__, step_name="Download Folder Selection")
        header.pack(fill='x')

        label = tk.Label(self, text="Select Download Folder", font=("Helvetica", 18, "bold"))
        label.pack(pady=20, padx=10)

        instructions_text_box = self.create_instructions_text_box(
            "Please select the folder in which the downloaded data will be placed. If you want to resume "
            "a download, please select the parent-folder of the 'pulled-data-pending' folder."
        )
        instructions_text_box.pack(pady=20, padx=10)

        browse_button = ttk.Button(self, text="Browse", command=self.browse_folder)
        browse_button.pack(pady=10, padx=10)

        self.folder_path_display = tk.Label(self, text="", font=("Helvetica", 12), bg='white', anchor="w")
        self.folder_path_display.pack(pady=10, padx=50, fill='x')

        self.resume_download_var = tk.BooleanVar(value=1 if get_resume_download() else 0)
        resume_download_checkbox = ttk.Checkbutton(
            self, text="Resume Download", variable=self.resume_download_var,
            command=self.toggle_resume_download
        )
        resume_download_checkbox.pack(pady=10, padx=10)

        resume_instructions_text_box = self.create_instructions_text_box(
            "Please mark this checkbox if you want to resume an existing download. By selecting the parent folder of "
            "'pulled-data-pending' folder."
        )
        resume_instructions_text_box.pack(pady=20, padx=10)

        get_navigation_buttons(self, "download_folder_selection_page")

    def browse_folder(self):
        """
        Handle the folder browsing and validation. Updates the selected folder path.

        This function prompts the user to select a directory. If the directory already contains 'pulled-data'
        and it is not part of a resume operation, it asks whether to select a different folder or not.
        """
        self.can_continue = False
        while not self.can_continue:
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                pulled_data_path = os.path.join(folder_selected, "pulled-data")
                pulled_data_path = get_filepath_for_executable(pulled_data_path)
                if os.path.exists(pulled_data_path) and not get_resume_download():
                    response = messagebox.askyesno(
                        "Directory Exists",
                        "The directory 'pulled-data' already exists in this location. Do you want to select a different folder?"
                    )
                    if not response:
                        set_target_folder(pulled_data_path)
                        break
                else:
                    if not get_resume_download():
                        os.makedirs(pulled_data_path, exist_ok=True)
                    set_target_folder(pulled_data_path)
                    self.can_continue = True
            else:
                break
        self.folder_path_display.config(text=get_target_folder())

    def toggle_resume_download(self):
        """
        Toggle the state of resume download.
        """
        set_resume_download(not get_resume_download())

    def create_instructions_text_box(self, text):
        """
        Create and return a disabled text box with instructions.

        Args:
            text (str): The instructional text to display.

        Returns:
            tk.Text: A configured text widget.
        """
        text_box = tk.Text(self, height=5, width=60, wrap="word", font=("Helvetica", 12))
        text_box.insert("end", text)
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")
        return text_box

    def on_next_page(self):
        """
        Validates if the user can proceed to the next page.

        Ensures that the selected folder is valid and not already containing a 'pulled-data' folder,
        unless resuming. Displays a warning if the validation fails.

        Returns:
            bool: True if validation is successful, False otherwise.
        """
        if not self.can_continue:
            messagebox.showwarning(
                "Folder invalid", "Please select a folder with no existing 'pulled-data' folder inside."
            )
            return False
        return True
