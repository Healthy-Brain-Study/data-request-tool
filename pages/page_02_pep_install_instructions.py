import tkinter as tk
import webbrowser
import platform
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class PepInstallInstructionsPage(tk.Frame):
    """
    This class represents a page in a tkinter application that provides
    installation instructions for the PEP client based on the user's operating system.
    It displays a series of instructions and includes clickable links for necessary resources.
    """

    def __init__(self, parent, controller):
        """
        Initialize the frame and populate it with UI components.

        Args:
            parent: The parent widget.
            controller: The controller for managing the application's frames.
        """
        super().__init__(parent)
        self.controller = controller

        # Header
        header = HeaderComponent(self, filename=__file__, step_name="PEP Installation Instructions")
        header.pack(fill='x')

        general_instructions = [
            "To download the research data the PEP Client is used.",
            "This program creates a secure connection with the database and downloads the data to your local machine.",
            "If you want to know more about PEP: (https://pep.cs.ru.nl/)",
            "Let's move on to the actual data download. Please install the PEP Client first."
        ]

        # Set specific instructions based on the operating system
        instructions = self.get_platform_instructions()

        instructions = general_instructions + instructions

        # Instructions text box
        self.text_box = tk.Text(self, height=12, width=80, wrap="word", font=("Helvetica", 12))
        self.text_box.pack(padx=10, pady=10)
        self.insert_instructions(instructions)
        self.text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

        # Navigation buttons
        get_navigation_buttons(self, "pep_install_instructions_page")

    def get_platform_instructions(self):
        """
        Determine the platform of the user's system and set the appropriate instructions.

        Returns:
            list: A list of strings with the instructions based on the operating system.
        """
        if platform.system() == 'Windows':
            return [
                "You can download the PEP Client installer via this link: (https://pep.cs.ru.nl/hb/prod/pep.msi)",
                "Follow the instructions in the PEP installer.",
                "When finished installing click 'Next'"
            ]
        elif platform.system() == 'Darwin':  # macOS
            return [
                "Currently Docker is used to be able to run the PEP Client on Mac",
                "Therefore, please first install Docker Desktop. (https://docs.docker.com/desktop/install/mac-install/)",
                "Follow the instruction in the Docker installer.",
                "Start Docker Desktop",
                "Click 'Next' below to continue."
            ]
        else:  # Assuming Linux or other Unix-like
            return [
                "Currently Singularity is used to be able to run the PEP Client on Linux",
                "Install Singularity. (https://docs.sylabs.io/guides/3.0/user-guide/installation.html#install-on-linux)",
                "When installation is successful run 'singularity -V' to check if version 3.x is installed.",
                "Click 'Next' below to continue"
            ]

    def insert_instructions(self, instructions):
        """
        Insert the given instructions into the text box with clickable links.

        Args:
            instructions (list): A list of instructions that may include URLs.
        """
        for item in instructions:
            link_start = item.find("http")
            if link_start != -1:
                self.text_box.insert("insert", item[:link_start])
                link_end = item.find(")", link_start) if ")" in item[link_start:] else len(item)
                link_text = item[link_start:link_end]
                self.text_box.insert("insert", link_text, "link")
                self.text_box.tag_config("link", foreground="blue", underline=1)
                self.text_box.tag_bind("link", "<Button-1>", self.open_link)
                self.text_box.insert("insert", item[link_end:] + "\n\n")
            else:
                self.text_box.insert("insert", item + "\n\n")

    def open_link(self, event):
        """
        Open a link clicked by the user in the text box.

        Args:
            event: The event object containing coordinates of the mouse click.
        """
        start_index = self.text_box.index(f"@{event.x},{event.y} linestart")
        end_index = self.text_box.index(f"@{event.x},{event.y} lineend")
        text = self.text_box.get(start_index, end_index)
        url_start = text.find("http")
        if url_start != -1:
            url_end = len(text)
            url = text[url_start:url_end - 1]
            webbrowser.open(url)
