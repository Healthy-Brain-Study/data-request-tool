import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from helpers.functions import get_filepath_for_executable, set_resume_download
from helpers.header import HeaderComponent


class IntroductionPage(tk.Frame):
    """
    A class used to represent the introduction page of a tkinter application
    for the Healthy Brain Study - Data Request Tool.
    """

    def __init__(self, parent, controller):
        """
        Initialize the introduction page frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        set_resume_download(False)

        # Add header
        header = HeaderComponent(self, filename=__file__, step_name="Start")
        header.pack(fill='x')

        # Title label
        label = tk.Label(
            self, text="Healthy Brain Study - Data Request Tool",
            font=("Helvetica", 18, "bold")
        )
        label.pack(pady=20, padx=10)

        # Load and display the logo image
        image_path = get_filepath_for_executable(os.path.join('static', 'logo.png'))
        image = Image.open(image_path).resize((100, 100))
        photo = ImageTk.PhotoImage(image)
        self.image_label = ttk.Label(self, image=photo)
        self.image_label.image = photo  # Keep a reference to prevent garbage-collection
        self.image_label.pack(side='top')

        # Style configuration
        style = ttk.Style(self)
        style.configure("Custom.TButton", font=14)

        # Buttons frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side="bottom")

        # Buttons for various actions
        button1 = ttk.Button(
            self.button_frame, text="Resume Download",
            command=self.resume_download_action
        )
        button2 = ttk.Button(
            self.button_frame, text="Unzip download",
            command=self.unzip_download_action
        )
        button3 = ttk.Button(
            self.button_frame, text="Combine Columns",
            command=self.combine_columns_action
        )
        button1.pack(pady=5, padx=10, side="left")
        button2.pack(pady=5, padx=10, side="left")
        button3.pack(pady=5, padx=10, side="left")

        # Start download process button
        start_button = ttk.Button(
            self, text="Start Download Process",
            command=lambda: controller.show_frame("pep_install_instructions_page")
        )
        start_button.pack(pady=10, padx=10, side="bottom")

        # Explanatory text box
        text_box = tk.Text(
            self, height=5, width=60, wrap="word",
            font=("Helvetica", 12)
        )
        text_box.pack(pady=(75, 0), padx=10, side="bottom")
        text_box.insert("end",
                        "Welcome to the data request tool for the Healthy Brain Study. "
                        "This tool assists researchers in downloading and merging data from the PEP database. "
                        "Please click 'Start Download Process' to initiate the downloading process."
                        )
        text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

    def resume_download_action(self):
        """
        Enable resuming the download and switch to the token upload page.
        """
        set_resume_download(True)
        self.controller.show_frame("token_upload_page")

    def unzip_download_action(self):
        """
        Switch to the unzip page.
        """
        self.controller.show_frame("unzip_page")

    def combine_columns_action(self):
        """
        Switch to the combine columns introduction page.
        """
        self.controller.show_frame("combine_columns_introduction_page")
