import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from helpers.functions import get_target_folder, set_target_folder
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class MergeFilesFolderSelectionPage(tk.Frame):
    """
    A Frame to select the folder for merging files.

    This page allows the user to select the input folder where the participant data is located.
    It provides a header, instructions, and a navigation button to browse for the folder.
    """

    def __init__(self, parent, controller):
        """
        Initialize the frame for the folder selection page.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.folder_path = tk.StringVar()

        # Header
        header = HeaderComponent(self, filename=__file__, step_name="Combine Columns Folder Selection")
        header.pack(fill='x')

        label = tk.Label(self, text="Select the input folder:", font=("Helvetica", 12), anchor="w")
        label.pack(pady=(10, 0), padx=10, anchor="w")

        # Explanatory text box
        text_box = tk.Text(self, height=4, width=60, wrap="word", font=("Helvetica", 12))
        text_box.pack(padx=10)
        text_box.insert("end", "Please select the folder where the participant data is located. The folder is called 'pulled-data'."
                        "The folder should contain the participant folders usually named 'HBXXXXX'. \n")
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

        self.entry = tk.Entry(self, textvariable=self.folder_path, state='readonly', width=50)
        self.entry.pack(pady=(0, 10), padx=10)

        if get_target_folder():
            self.folder_path.set(get_target_folder())

        ttk.Button(self, text="Browse", command=self.browse_folder).pack(pady=(0, 10), side="top")

        get_navigation_buttons(self, "combine_columns_folder_selection_page")

    def browse_folder(self):
        """
        Open a dialog to browse for a directory.

        The user selects a directory through a file dialog. The chosen directory path
        is then set as the folder path and stored using set_target_folder.
        """
        folder_selected = filedialog.askdirectory()
        if folder_selected:  # if a folder was selected
            self.folder_path.set(folder_selected)
            set_target_folder(folder_selected)

    def on_next_page(self):
        """
        Handle navigation to the next page upon folder selection.

        Checks if a folder path has been set. If not, it shows a warning.
        Otherwise, it proceeds to the next page and passes the selected folder path.

        Returns:
            bool: True if navigation is successful, False if a warning is shown.
        """
        if self.folder_path.get() == "":
            messagebox.showwarning("Warning", "Please select a folder to proceed.")
            return False
        else:
            # Proceed to the next page (ColumnSelectionPage) and pass the selected folder path
            self.controller.get_frame("column_selection_page").start()
            return True
