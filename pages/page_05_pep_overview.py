import threading
import tkinter as tk

from helpers.navigation_buttons import get_navigation_buttons
from pepclient_package.pep_client import PepClient
from helpers.functions import get_pep_engine, get_token_filepath
from helpers.header import HeaderComponent
from helpers.loading_dialog import LoadingDialog


class PEPOverviewPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the PEP overview page frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller

        header = HeaderComponent(self, filename=__file__, step_name="PEP Overview")
        header.pack(fill='x')

        self.setup_ui()

    def setup_ui(self):
        """
        Set up user interface elements for the PEP overview page.
        """
        title_font = ("Helvetica", 16, "bold")

        enrollment_label = tk.Label(self, text="Enrollment Information", font=title_font, anchor="w")
        enrollment_label.pack(pady=(10, 2), padx=10, fill='x')
        self.enrollment_text_box = self.create_scrollable_text_widget(height=2)

        participant_group_label = tk.Label(self, text="Participant Group Access", font=title_font, anchor="w")
        participant_group_label.pack(pady=(10, 2), padx=10, fill='x')
        self.participant_group_text_box = self.create_scrollable_text_widget(height=2)

        column_access_label = tk.Label(self, text="Column Access Information", font=title_font, anchor="w")
        column_access_label.pack(pady=(10, 2), padx=10, fill='x')
        self.column_access_text_box = self.create_scrollable_text_widget(height=10)

        get_navigation_buttons(self, "pep_overview_page")

    def create_scrollable_text_widget(self, height):
        """
        Create a scrollable text widget with a vertical scrollbar.

        Args:
            height (int): The height of the text widget.

        Returns:
            tk.Text: The created text widget.
        """
        frame = tk.Frame(self)
        text_widget = tk.Text(frame, height=height, wrap="word", font=("Helvetica", 12), bg='white')
        text_widget.pack(side="left", fill="both")
        text_widget.config(state="disabled")

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        frame.pack(pady=(0, 10), padx=10, fill='x')

        return text_widget

    def load_pep_overview(self, tries=5):
        """
        Load PEP overview information with retries for failed attempts.

        Args:
            tries (int): Number of remaining retry attempts.
        """

        pepcli = PepClient(pep_token_filepath=get_token_filepath(), engine=get_pep_engine(self.controller))
        pepcli.set_timeout(10)

        enrollment_access = pepcli.query_enrollment().get("message", "")
        column_access = pepcli.query_column_access().get("message", "")
        participant_group_access = pepcli._command(command="query participant-group-access").get("message", "")

        if not enrollment_access and tries > 0:
            self.load_pep_overview(tries=tries - 1)
            return
        else:
            pepcli.reset_timeout()

        self.enrollment_text_box.after(0, self.update_text_widget, self.enrollment_text_box, enrollment_access)
        self.column_access_text_box.after(0, self.update_text_widget, self.column_access_text_box, column_access)
        self.participant_group_text_box.after(0, self.update_text_widget, self.participant_group_text_box, participant_group_access)

        self.loading_dialog.close()

    def update_text_widget(self, widget, text):
        """
        Update the text of a text widget in a thread-safe manner.

        Args:
            widget (tk.Text): The text widget to update.
            text (str): The text to insert into the widget.
        """
        widget.config(state="normal")
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")

    def on_show_frame(self):
        """
        Actions to perform when this frame is shown.
        """
        self.loading_dialog = LoadingDialog(self.controller, message="Loading PEP info...")
        threading.Thread(target=self.load_pep_overview, daemon=True).start()

    def go_to_next_page(self):
        """
        Navigate to the next page in the application.
        """
        self.controller.show_frame("download_folder_selection_page")
