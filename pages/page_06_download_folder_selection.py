import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from helpers.functions import (
    get_filepath_for_executable, get_target_folder, set_target_folder,
    get_resume_download, set_resume_download, get_available_columns, set_selected_columns
)
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons
from helpers.loading_dialog import LoadingDialog


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
        self.checkbox_vars = {}  # Dictionary to hold checkbox variables

        header = HeaderComponent(self, filename=__file__, step_name="Download Folder and Columns Selection")
        header.pack(fill='x')

        label = tk.Label(self, text="Select Download Folder", font=("Helvetica", 18, "bold"))
        label.pack(pady=10, padx=10)

        instructions_text_box = self.create_instructions_text_box(
            "Please select the folder in which the downloaded data will be placed. If you want to resume "
            "a download, please select the parent folder of the 'pulled-data-pending' folder.", height=2)
        instructions_text_box.pack(pady=10, padx=10)

        browse_button = ttk.Button(self, text="Browse", command=self.browse_folder)
        browse_button.pack(pady=5, padx=10)

        self.folder_path_display = tk.Label(self, text="", font=("Helvetica", 12), bg='white', anchor="w")
        self.folder_path_display.pack(pady=5, padx=50, fill='x')

        self.resume_download_var = tk.BooleanVar(value=1 if get_resume_download() else 0)
        resume_download_checkbox = ttk.Checkbutton(
            self, text="Resume Download", variable=self.resume_download_var,
            command=self.toggle_resume_download
        )
        resume_download_checkbox.pack(pady=10, padx=10)

        resume_instructions_text_box = self.create_instructions_text_box(
            "Please mark this checkbox if you want to resume an existing download by selecting the parent folder of "
            "'pulled-data-pending' folder."
        )
        resume_instructions_text_box.pack(pady=10, padx=10)

        # Column Selection
        label_columns = tk.Label(self, text="Select Columns to Download", font=("Helvetica", 18, "bold"))
        label_columns.pack(pady=10, padx=10)

        columns_instructions_text_box = self.create_instructions_text_box(
            "Please select the columns you wish to download from the list below.", height=1)
        columns_instructions_text_box.pack(pady=0, padx=10)

        # Placeholder for column checkboxes; will be populated after fetching columns
        self.checkbox_frame = None

        get_navigation_buttons(self, "download_folder_selection_page")

    def on_show_frame(self):
        """
        Actions to perform when this frame is shown.
        Fetch available columns and populate the checkboxes.
        """
        # Show a loading dialog while fetching columns
        self.loading_dialog = LoadingDialog(self.controller, message="Loading available columns...")
        threading.Thread(target=self.fetch_available_columns, daemon=True).start()

    def fetch_available_columns(self):
        """
        Fetch available columns from PEP and populate the checkboxes.
        """
        self.available_columns = get_available_columns()

        self.controller.after(0, self.populate_column_checkboxes)
        self.loading_dialog.close()

    def populate_column_checkboxes(self):
        """
        Populate the checkboxes with available columns.
        """
        if hasattr(self, 'checkbox_frame') and self.checkbox_frame:
            self.checkbox_frame.destroy()

        if not self.available_columns:
            messagebox.showwarning(
                "No Columns Available",
                "No columns are available to select. Please ensure you have access to columns or go back to check your PEP setup."
            )
            self.checkbox_frame = None
        else:
            # Create a frame to hold the checkboxes
            container = ttk.Frame(self)
            container.pack(pady=0, padx=10, fill='both', expand=True)

            # Create a canvas and a scrollbar
            canvas = tk.Canvas(container, bg="white")  # Set background of canvas to white
            scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
            self.checkbox_frame = ttk.Frame(canvas, style="White.TFrame")  # Create a ttk frame with a custom style

            # Apply white background to the ttk frame and checkboxes
            style = ttk.Style()
            style.configure("White.TFrame", background="white")  # Custom style for white background
            style.configure("White.TCheckbutton", background="white")  # Custom style for checkboxes

            self.checkbox_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=self.checkbox_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # Bind the mouse scroll event to the canvas
            canvas.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(event, canvas))

            # Create checkboxes for each column
            self.checkbox_vars = {}
            for column in self.available_columns:
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.checkbox_frame, text=column, variable=var, style="White.TCheckbutton")
                chk.pack(anchor='w', padx=5, pady=2)
                self.checkbox_vars[column] = var

            # Add "Select All" and "Unselect All" buttons
            select_all_button = ttk.Button(self, text="Select All", command=self.select_all_checkboxes)
            select_all_button.pack(pady=5)

            unselect_all_button = ttk.Button(self, text="Unselect All", command=self.unselect_all_checkboxes)
            unselect_all_button.pack(pady=5)

    def select_all_checkboxes(self):
        """
        Select all checkboxes.
        """
        for var in self.checkbox_vars.values():
            var.set(True)

    def unselect_all_checkboxes(self):
        """
        Unselect all checkboxes.
        """
        for var in self.checkbox_vars.values():
            var.set(False)

    def _on_mousewheel(self, event, canvas):
        """
        Handle the mouse wheel scroll event to scroll the canvas content.
        """
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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
                    if response:
                        continue  # Prompt again
                    else:
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

    def create_instructions_text_box(self, text, height=5):
        """
        Create and return a disabled text box with instructions.

        Args:
            text (str): The instructional text to display.

        Returns:
            tk.Text: A configured text widget.
        """
        text_box = tk.Text(self, height=height, width=80, wrap="word", font=("Helvetica", 12))
        text_box.insert("end", text)
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")
        return text_box

    def on_next_page(self):
        """
        Validates if the user can proceed to the next page.

        Ensures that the selected folder is valid and not already containing a 'pulled-data' folder,
        unless resuming. Also checks if columns are selected.

        Returns:
            bool: True if validation is successful, False otherwise.
        """
        if not self.can_continue:
            messagebox.showwarning(
                "Folder invalid", "Please select a folder with no existing 'pulled-data' folder inside."
            )
            return False

        if self.checkbox_vars:
            selected_columns = [column for column, var in self.checkbox_vars.items() if var.get()]
            if not selected_columns:
                messagebox.showwarning(
                    "No Columns Selected", "Please select at least one column to download."
                )
                return False
            else:
                set_selected_columns(selected_columns)
        else:
            messagebox.showwarning(
                "No Columns Available",
                "No columns are available to select. Please ensure you have access to columns or go back to check your PEP setup."
            )
            return False

        return True
