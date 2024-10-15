import platform
import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox
from helpers.functions import get_pep_engine, get_selected_columns, get_target_folder, get_token_filepath, get_resume_download
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons
from pepclient_package.pep_client import PepClient


class DownloadProgressPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the Download Progress Page frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.pep_client = None
        self.target_folder = ""
        self.os_name = platform.system().lower()
        self.can_continue = False

        self.setup_ui()

    def on_show_frame(self):
        """
        Actions to perform when this frame is displayed.
        Initializes the PEP client and starts the download process.
        """
        self.pepcli = PepClient(pep_token_filepath=get_token_filepath(), engine=get_pep_engine(self.controller))
        self.target_folder = get_target_folder()
        self.download_data()

    def setup_ui(self):
        """
        Set up the user interface for the download progress page.
        This includes a header, progress label, log display, and navigation buttons.
        """
        header = HeaderComponent(self, filename=__file__, step_name="Download Progress")
        header.pack(fill='x')

        self.progress_label = tk.Label(self, text="Download Progress", font=("Helvetica", 16, "bold"))
        self.progress_label.pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.download_log = tk.Text(frame, height=35, state='disabled', wrap='none', bg='white')
        self.download_log.pack(side='left', fill='both', expand=True)

        self.log_scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.download_log.yview)
        self.log_scrollbar.pack(side='right', fill='y')
        self.download_log.config(yscrollcommand=self.log_scrollbar.set)

        get_navigation_buttons(self, "download_progress_page")

    def download_data(self):
        """
        Start the thread for pulling data and updating the UI asynchronously.
        """
        self.download_thread = threading.Thread(target=self.pep_pull_and_update_ui)
        self.download_thread.start()
        self.after(500, self.check_download_complete)

    def check_download_complete(self):
        """
        Periodically check if the download has completed.
        If the download is still ongoing, schedule another check. If complete, handle the completion.
        """
        if self.download_thread.is_alive():
            self.after(500, self.check_download_complete)
        else:
            self.handle_download_complete()

    def pep_pull_and_update_ui(self):
        """
        Execute the PEP pull command and update the UI based on the output.
        """
        resume_command = "--resume --update -P * -c *"
        selected_columns = get_selected_columns()

        if self.os_name == "darwin":
            if selected_columns:
                command = "pull -P * --report-progress"
            else:
                command = "pull --all-accessible --report-progress"
            if get_resume_download():
                command += f" {resume_command}"

            for output_line in self.pepcli.pep_pull(command, self.target_folder):
                self.add_output_line_to_progress_text(output_line)
        else:
            if selected_columns:
                command = f"pull --output-directory \"{self.target_folder}\" -P * --report-progress"
            else:
                command = f"pull --output-directory \"{self.target_folder}\" --all-accessible --report-progress"
            if get_resume_download():
                command += f" {resume_command}"

            for output_line in self.pepcli.pep_pull(command):
                self.add_output_line_to_progress_text(f"{output_line}\n")

    def add_output_line_to_progress_text(self, line):
        """
        Add a line of output to the progress text widget and automatically scroll to the bottom.

        Args:
            line (str): The line of text to add to the progress display.
        """
        self.download_log.config(state='normal')
        self.download_log.insert('end', line)
        self.download_log.config(state='disabled')
        self.download_log.see('end')

    def handle_download_complete(self):
        """
        Handle actions and UI updates when the download has completed.
        """
        self.add_output_line_to_progress_text("Download Complete!\n")
        self.can_continue = True

    def on_next_page(self):
        """
        Determine if the application can navigate to the next page based on download completion.

        Returns:
            bool: True if navigation is allowed, else False.
        """
        if not self.can_continue:
            messagebox.showwarning("Download unfinished", "Download is not finished yet")

        return self.can_continue
