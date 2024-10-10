import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from PIL import Image, ImageTk

from helpers.functions import get_filepath_for_executable
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class MergeParticipantsExplanationPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the frame for explaining participant data merging.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller

        # Header
        header = HeaderComponent(self, filename=__file__, step_name="Merge Participants Explanation")
        header.pack(fill='x')

        # Title Label
        self.title_label = tk.Label(self, text="Merging the participants data", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # Styling for the application
        style = ttk.Style(self)
        custom_font = tkFont.Font(family="Helvetica", size=14)
        style.configure("Custom.TButton", font=custom_font)

        # Explanatory text box
        text_box = self.create_text_box("The merge involves combining each of the columns for all participants.\n"
                                        "This merge will create one file per column. The resulting file structure is shown below.\n"
                                        "On the left you see the file structure after download.\n"
                                        "On the right you see the file structure after the first merge.")
        text_box.pack(pady=(0, 0), padx=10, side="top", fill="x", anchor="w")

        # Example text box container
        example_frame = tk.Frame(self)
        example_frame.pack(pady=(0, 0), padx=10, fill="x", expand=True)
        self.create_and_pack_example_text_box(example_frame, 'folder_structure_example.txt')
        self.create_and_pack_example_text_box(example_frame, 'merge_participants_structure_example.txt')

        # Display Excel Combination Example Image
        excel_image_label = self.display_example_image()
        excel_image_label.pack()

        get_navigation_buttons(self, "merge_participants_explanation_page")

    def create_text_box(self, initial_text):
        """
        Create a read-only text box with specific text.

        Args:
            initial_text (str): The text to be displayed in the text box.
        """
        text_box = tk.Text(self, height=5, width=60, wrap="word", font=("Helvetica", 12))
        text_box.insert("end", initial_text)
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")
        return text_box

    def create_and_pack_example_text_box(self, parent, txt_file):
        """
        Create, configure and pack an example text box in the given parent.

        Args:
            parent (tk.Widget): The parent widget.
            txt_file (str): The text file containing the text to display.
        """
        example_text_box = self.create_example_text_box(parent, txt_file)
        example_text_box.pack(side="left", expand=True, fill="both")

    def create_example_text_box(self, parent, txt_file):
        """
        Create an example text box based on a text file.

        Args:
            parent (tk.Widget): The parent widget.
            txt_file (str): Name of the text file to display content from.
        """
        example_text_box = tk.Text(parent, height=15, width=60, wrap="word", font=("Courier", 12))
        example_text_content = self.get_folder_structure_example_text_file(txt_file=txt_file)
        example_text_box.insert("end", example_text_content)
        example_text_box.config(state="disabled", bg="#f0f0f0", relief="flat")
        return example_text_box

    def get_folder_structure_example_text_file(self, txt_file='folder_structure_example.txt'):
        """
        Fetch and return the content of a specified example text file.

        Args:
            txt_file (str): The text file to read.
        """
        filepath = get_filepath_for_executable(os.path.join('static', txt_file))
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return ""

    def display_example_image(self):
        """
        Create and return a label containing an example image.
        """
        image_path = get_filepath_for_executable(os.path.join('static', 'combine_example.png'))
        excel_image = ImageTk.PhotoImage(Image.open(image_path))
        excel_image_label = tk.Label(self, image=excel_image)
        excel_image_label.image = excel_image  # Keep a reference
        return excel_image_label
