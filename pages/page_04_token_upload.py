import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from helpers.header import HeaderComponent
from helpers.functions import get_token_filepath, set_token_filepath
from helpers.navigation_buttons import get_navigation_buttons


class TokenUploadPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the token upload page frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller

        # Header
        header = HeaderComponent(self, filename=__file__, step_name="Download Setup & Token Upload")
        header.pack(fill='x')

        # Dropdown selector
        label_selector = tk.Label(self, text="Select engine to run PEP", font=("Helvetica", 18, "bold"))
        label_selector.pack(pady=10, padx=10)
        self.os_selector = ttk.Combobox(self, state="readonly")
        self.os_selector['values'] = ('Docker', 'Singularity (HPC)', 'Windows')
        self.os_selector.pack(pady=10)
        self.preselect_os()

        # Title Label
        label = tk.Label(self, text="Upload Your Token File", font=("Helvetica", 18, "bold"))
        label.pack(pady=20, padx=10)

        # Button to Upload Token File
        upload_button = ttk.Button(self, text="Upload Token File", command=self.upload_token_file)
        upload_button.pack(pady=10, padx=10)

        # Instructions Text Box
        text_box = tk.Text(self, height=5, width=60, wrap="word", font=("Helvetica", 12))
        text_box.pack(pady=20, padx=10)
        text_box.insert("end", "Please upload the token file provided to you. This file "
                               "is necessary for authentication and to proceed with the data "
                               "download process.")
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

        # Navigation Buttons
        get_navigation_buttons(self, "token_upload_page", skip_to_page="unzip_page", skip_button_name="Skip download and go to unzip tool")

    def upload_token_file(self):
        """
        Handles the file upload process by opening a file dialog to select a token file,
        setting the token file path, and navigating to the next page.
        """
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            try:
                with open(filepath, 'r') as _:
                    set_token_filepath(filepath)
                    self.controller.show_frame("pep_overview_page")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load the token file: {e}")

    def on_next_page(self):
        """
        Validates if the token file is uploaded by checking the token file path.

        Returns:
            bool: True if token file is uploaded, False otherwise.
        """
        if get_token_filepath():
            return True
        else:
            messagebox.showwarning("Upload token", "Please upload your token file before continuing.")
            return False

    def preselect_os(self):
        os_name = platform.system().lower()
        if os_name == 'linux':
            self.os_selector.set('Singularity (HPC)')
        elif os_name == 'windows':
            self.os_selector.set('Windows')
        else:
            self.os_selector.set('Docker')
