import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from helpers.functions import get_filepath_for_executable
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class MergeFilesIntroductionPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the introduction page frame for merging participant data.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller

        # Initialize header
        self.init_header()

        # Initialize UI components
        self.init_ui_components()

        # Add navigation buttons
        get_navigation_buttons(
            self, "combine_columns_introduction_page",
            skip_button_name="Skip combine", skip_to_page="final_page"
        )

    def init_header(self):
        """Create and pack the header component."""
        header = HeaderComponent(self, filename=__file__, step_name="Combine Columns Introduction")
        header.pack(fill='x')

    def init_ui_components(self):
        """Initialize and pack all UI components on the frame."""
        self.init_title_label()
        self.init_custom_style()
        self.init_explanatory_text_box()
        self.init_example_text_box()

    def init_title_label(self):
        """Initialize and pack the title label."""
        self.title_label = tk.Label(self, text="Combine Columns", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

    def init_custom_style(self):
        """Create a custom font and configure a style using this font."""
        custom_font = tkFont.Font(family="Helvetica", size=14)
        style = ttk.Style(self)
        style.configure("Custom.TButton", font=custom_font)

    def init_explanatory_text_box(self):
        """Create, configure, and pack the explanatory text box."""
        text_box = tk.Text(self, height=5, width=60, wrap="word", font=("Helvetica", 12))
        text_box.pack(pady=(75, 0), padx=10, side="top", fill="x", anchor="w")
        text_box.insert("end", "Because the downloaded file structure might not work optimal for analysis, "
                               "this section allows for the merge of your column files together into 1 or multiple "
                               "CSV files. The current file structure is as follows: each participant has its own "
                               "folder. For each column there is a folder inside each participant folder. That "
                               "column folder contains the CSV or data file of that column. See below for visualization "
                               "of that folder structure. This tool allows for the merge of those CSV files.")
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

    def init_example_text_box(self):
        """Create, configure, and pack the example text box with example file content."""
        example_text_box = tk.Text(self, height=19, width=60, wrap="word", font=("Courier", 12))
        example_text_box.pack(pady=(10, 0), padx=10, side="top", fill="x", anchor="w")
        example_text_content = self.get_folder_structure_example_text_file()
        example_text_box.insert("end", example_text_content)
        example_text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

    def get_folder_structure_example_text_file(self):
        """
        Retrieve the text content from a file that contains the example of folder structure.

        Returns:
            str: Content of the example text file.
        """
        filepath = os.path.join('static', 'folder_structure_example.txt')
        filepath = get_filepath_for_executable(filepath)
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                example_file = file.read()
            return example_file
        except FileExistsError:
            return ""
