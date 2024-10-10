import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from helpers.combine_columns import run_combine
from helpers.header import HeaderComponent


class CombineColumnsProgressPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the page for tracking progress of the column combining process.

        Args:
            parent (tk.Widget): The parent widget.
            controller (object): The application's main controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.target_folder = None
        self.start_time = None

        self.header = HeaderComponent(self, filename=__file__, step_name="Combining Progress")
        self.header.pack(fill='x')

        self.label = tk.Label(self, text="Processing...", font=("Helvetica", 12))
        self.label.pack(pady=10, padx=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode='determinate')
        self.progress.pack(pady=20)

        self.status_text = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status_text, font=("Helvetica", 10))
        self.status_label.pack(pady=10)

        self.time_estimate_label = tk.Label(self, text="Estimated time remaining: calculating...", font=("Helvetica", 10))
        self.time_estimate_label.pack(pady=10)

    def select_target_folder(self):
        """
        Open a dialog to select a target folder and store its path.
        Shows a warning message if no folder is selected.
        """
        messagebox.showwarning("Warning", "Please select a target folder first. Your combined data will be placed here.")
        self.target_folder = filedialog.askdirectory(title="Please select a target folder for your data")
        if self.target_folder:
            self.status_text.set(f"Target folder selected: {self.target_folder}")
        else:
            self.status_text.set("No target folder selected.")

    def start_combine(self, selected_columns, selected_columns_for_meta_combine, input_folder, columns_to_combine, separator=","):
        """
        Start the process of combining columns in a separate thread.

        Args:
            selected_columns (list): Columns selected for merging in a single file.
            selected_columns_for_meta_combine (list): Columns selected for metadata combination.
            input_folder (str): Directory where input files are located.
            columns_to_combine (list): Columns to be combined.
            separator (str): Delimiter used to separate columns in output.
        """
        self.progress['maximum'] = 100
        self.progress['value'] = 0
        self.status_text.set("Combining columns...")
        self.start_time = time.time()

        def combine_columns_wrapper():
            run_combine(
                download_directory=input_folder,
                selected_columns_one_file_merge=selected_columns,
                selected_columns_participant_merge=selected_columns_for_meta_combine,
                update_progress=self.update_progress_bar,
                columns_to_combine=columns_to_combine
            )
            self.finish_combine()

        threading.Thread(target=combine_columns_wrapper, daemon=True).start()

    def update_progress_bar(self, value):
        """
        Update the progress bar in the GUI.

        Args:
            value (float): The new progress value.
        """
        self.after(0, self._update_progress_bar, value)

    def _update_progress_bar(self, value):
        self.progress['value'] = value
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if value > 0:
                total_time_estimate = (elapsed_time / value) * 100
                remaining_time = total_time_estimate - elapsed_time
                self.time_estimate_label.config(text=f"Estimated time remaining: {remaining_time:.2f} seconds")

    def finish_combine(self):
        """
        Finalize the combining process, update GUI accordingly.
        """
        self.status_text.set("Combine operation completed successfully.")
        self.time_estimate_label.config(text="Estimated time: completed.")
        messagebox.showinfo("Success", "Columns combined successfully!")
        self.controller.show_frame("final_page")

    def reset_page(self):
        """
        Reset the progress page to its initial state.
        """
        self.progress['value'] = 0
        self.status_text.set("")
        self.time_estimate_label.config(text="Estimated time remaining: calculating...")
