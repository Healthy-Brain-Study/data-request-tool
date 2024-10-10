import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from helpers.combine_columns import get_all_columns_with_csv_and_their_number_of_lines
from helpers.functions import get_filepath_for_executable
from helpers.header import HeaderComponent
from helpers.loading_dialog import LoadingDialog
from static.columns_to_combine import columns_to_combine


class ColumnSelectionPage(tk.Frame):
    """
    Provides a user interface for selecting columns to be combined into CSV files.

    Args:
        parent (tk.Widget): The parent widget.
        controller (Controller): The main application controller.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_columns = []
        self.check_vars = []

        header = HeaderComponent(self, filename=__file__, step_name="Combine Columns Selection")
        header.pack(fill='x')

        style = ttk.Style()
        style.configure("White.TFrame", background="white")
        style.configure("WhiteCheckbutton.TCheckbutton", background="white", foreground="black")

        label = tk.Label(self, text="Select columns to combine into 1 CSV file per column", font=("Helvetica", 12))
        label.pack()

        self.frame = ttk.Frame(self)
        self.frame.pack(padx=10, fill='both', expand=True)

        instructions_label = tk.Label(self.frame, height=4, text=(
            "The image below illustrates how selected columns will be combined in one CSV file.\n"
            "Each column will get its own CSV file containing all participants who have at least some data present.\n"
            "The 'participant_id' column will be present in every CSV file.\n"),
            font=("Helvetica", 10), justify="left")
        instructions_label.pack(pady=(10, 0))

        image_path = get_filepath_for_executable(os.path.join('static', 'combine_example.png'))
        excel_image = tk.PhotoImage(file=image_path)
        excel_image_label = tk.Label(self.frame, image=excel_image)
        excel_image_label.image = excel_image
        excel_image_label.pack(pady=10)
        excel_image = excel_image.subsample(2, 2)

        self.label_frame = ttk.Frame(self.frame)
        self.label_frame.pack(fill='x', expand=True)

        selection_label = tk.Label(self.label_frame, text="Select columns:")
        selection_label.pack(pady=5, padx=5, side="left", fill="x")

        self.canvas = tk.Canvas(self.frame, background="white")
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="White.TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        ttk.Button(self, text="Select All", command=self.select_all).pack(side='left', padx=5, pady=5)
        ttk.Button(self, text="Deselect All", command=self.deselect_all).pack(side='left', padx=5, pady=5)
        ttk.Button(self, text="Combine", command=self.start_combine, width=10).pack(side='right', padx=5, pady=5)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("combine_columns_folder_selection_page"), width=10).pack(side='right', padx=5, pady=5)

    def start(self):
        """
        Starts the process of loading columns by displaying a loading dialog and creating a new thread.
        """
        root_window = self.controller
        root_window.config(cursor="watch")
        root_window.update_idletasks()

        self.loading_dialog = LoadingDialog(self.controller)
        loading_columns_thread = threading.Thread(target=self.load_columns, daemon=True)
        loading_columns_thread.start()

        self.wait_for_columns_to_load(loading_columns_thread)

    def wait_for_columns_to_load(self, loading_columns_thread):
        """
        Periodically checks if the loading columns thread is still alive and updates the UI accordingly.

        Args:
            loading_columns_thread (threading.Thread): The thread in which column loading is executed.
        """
        if loading_columns_thread.is_alive():
            self.after(100, lambda: self.wait_for_columns_to_load(loading_columns_thread))
        else:
            self.loading_dialog.close()

    def load_columns(self):
        """
        Loads columns from the selected folder and updates the UI components with the retrieved columns.
        """
        root_window = self.controller
        input_folder = self.controller.get_frame("combine_columns_folder_selection_page").folder_path.get()
        if input_folder:
            self.all_columns, self.columns_to_combine = get_all_columns_with_csv_and_their_number_of_lines(input_folder, self.loading_dialog)
            self.columns = sorted(list(self.all_columns["columns"]))
            self.columns_available_for_select = self.all_columns["columns_available_for_select"]
            self.columns_which_cant_be_merged = self.all_columns["columns_which_cant_be_merged"]
            self.populate_checkboxes()
            root_window.config(cursor="")
            root_window.update_idletasks()

    def populate_checkboxes(self):
        """
        Populates the scrollable frame with checkboxes for each column available for selection.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.check_vars.clear()

        for column in self.columns:
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.scrollable_frame, text=column, variable=var, style="WhiteCheckbutton.TCheckbutton")
            enabled = True  # Assume checkbox is enabled by default

            if column in self.columns_which_cant_be_merged:
                chk.state(['disabled'])
                chk.config(text=f"{column} (Not suitable for merge)")
                enabled = False

            chk.pack(anchor='w')
            self.check_vars.append((var, enabled))

    def select_all(self):
        """
        Sets all checkbox variables to True where the checkbox is enabled.
        """
        for var, enabled in self.check_vars:
            if enabled:
                var.set(True)

    def deselect_all(self):
        """
        Sets all checkbox variables to False.
        """
        for var, _ in self.check_vars:
            var.set(False)

    def start_combine(self):
        """
        Gathers selected columns and starts the combining process if more than one column is selected.
        """
        self.selected_columns = [list(self.columns)[i] for i, (var, enabled) in enumerate(self.check_vars) if var.get() and enabled]
        if len(self.selected_columns) > 1:
            input_folder = self.controller.get_frame("combine_columns_folder_selection_page").folder_path.get()
            separator = ','
            self.controller.show_frame("combine_columns_progress_page")
            self.controller.get_frame("combine_columns_progress_page").start_combine(self.selected_columns, self.selected_columns, input_folder, self.columns_to_combine, separator)
        else:
            messagebox.showerror("Error", "No columns selected. Please select at least one column.")
