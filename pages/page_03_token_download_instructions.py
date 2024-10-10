import tkinter as tk
import webbrowser
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class TokenDownloadInstructionsPage(tk.Frame):
    """
    A Frame to display download instructions for a token with embedded links,
    and navigation buttons to proceed with the instructions.
    """

    def __init__(self, parent, controller):
        """
        Initializes the TokenDownloadInstructionsPage frame.

        Args:
            parent: The parent widget.
            controller: The controlling entity or logic handler.
        """
        super().__init__(parent)
        self.controller = controller

        # Header
        header = HeaderComponent(self, filename=__file__, step_name="Token Download Instructions")
        header.pack(fill='x')

        # Instructions for the use of the Yivi app
        instructions = [
            "If everything went correctly you've received an email from support@pep.cs.ru.nl",
            "The email contains a link to a Postguard download.",
            "To access this download you need to install the Yivi app and activate it using the same email address "
            "that you've received the link from. (https://www.yivi.app/download)",
            "After you have activated the app you can download the token file using the link from the email.",
            "When downloading, you'll be asked to use the Yivi app for two-factor authentication.",
            "Click 'Next' below to continue"
        ]

        # Instructions text box
        self.text_box = tk.Text(self, height=12, width=80, wrap="word", font=("Helvetica", 12))
        self.text_box.pack(padx=10, pady=10)
        self.insert_instructions(instructions)
        self.text_box.config(state="disabled", bg="#f0f0f0", relief="flat")

        get_navigation_buttons(self, "token_download_instructions_page")

    def insert_instructions(self, instructions):
        """
        Inserts a list of instructions into the text box with links configured for interaction.

        Args:
            instructions: A list of instruction strings.
        """
        for item in instructions:
            link_start = item.find("http")
            if link_start != -1:
                # Insert the text before the link
                self.text_box.insert("insert", item[:link_start])

                # Insert the link
                link_end = item.find(")", link_start) if ")" in item[link_start:] else len(item)
                link_text = item[link_start:link_end]
                self.text_box.insert("insert", link_text, "link")

                # Configure the link tag
                self.text_box.tag_config("link", foreground="blue", underline=1)
                self.text_box.tag_bind("link", "<Button-1>", self.open_link)

                # Insert the rest of the text
                self.text_box.insert("insert", item[link_end:] + "\n\n")
            else:
                self.text_box.insert("insert", item + "\n\n")

    def open_link(self, event):
        """
        Opens a link when clicked in the text box.

        Args:
            event: The event object containing event details.
        """
        start_index = self.text_box.index("@%s,%s linestart" % (event.x, event.y))
        end_index = self.text_box.index("@%s,%s lineend" % (event.x, event.y))
        text = self.text_box.get(start_index, end_index)
        url_start = text.find("http")
        if url_start != -1:
            url_end = len(text)
            url = text[url_start:url_end - 1]
            webbrowser.open(url)
