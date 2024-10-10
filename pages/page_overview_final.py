import os
import sys
import tkinter as tk

from helpers.functions import get_target_folder
from helpers.header import HeaderComponent
from helpers.navigation_buttons import get_navigation_buttons


class FinalPage(tk.Frame):
    """
    Represents the final page of the application.

    Attributes:
        controller (Controller): The main application controller.
    """

    def __init__(self, parent, controller):
        """
        Initialize the final page frame.

        Args:
            parent (tk.Widget): The parent widget.
            controller (Controller): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller

        # Header component
        header = HeaderComponent(self, filename=__file__, step_name="Overview")
        header.pack(fill='x')

        # Title Label
        label = tk.Label(self, text="Overview", font=("Helvetica", 18, "bold"))
        label.pack(pady=20, padx=10)

        # Instructions Text Box
        text_box = tk.Text(
            self, height=5, width=60, wrap="word", font=("Helvetica", 12),
            state="disabled", bg="#f0f0f0", relief="flat"
        )
        text_box.pack(pady=20, padx=10)
        text_box.insert("end", "All steps have finished. Please click 'Open Output Folder' to check the downloaded data. In the folder 'processed-data' inside the download folder all merged data is present.")

        # Merge Label and Text Box with Scrollbar
        merge_label = tk.Label(self, text="Columns which have not/can't be merged:", font=("Helvetica", 12, "bold"))
        merge_label.pack(pady=10, padx=10)
        merge_frame = tk.Frame(self)
        merge_frame.pack(pady=10, padx=10)
        merge_text_box = tk.Text(
            merge_frame, height=5, width=58, wrap="word", font=("Helvetica", 12),
            state="disabled", bg="#f0f0f0", relief="flat"
        )
        merge_scroll = tk.Scrollbar(merge_frame, orient="vertical", command=merge_text_box.yview)
        merge_text_box.config(yscrollcommand=merge_scroll.set)
        merge_scroll.pack(side="right", fill="y")
        merge_text_box.pack(side="left", fill="both", expand=True)

        # Selected Columns Label and Text Box with Scrollbar
        selected_label = tk.Label(self, text="Columns which have been merged:", font=("Helvetica", 12, "bold"))
        selected_label.pack(pady=10, padx=10)
        selected_frame = tk.Frame(self)
        selected_frame.pack(pady=10, padx=10)
        selected_text_box = tk.Text(
            selected_frame, height=5, width=58, wrap="word", font=("Helvetica", 12),
            state="disabled", bg="#f0f0f0", relief="flat"
        )
        selected_scroll = tk.Scrollbar(selected_frame, orient="vertical", command=selected_text_box.yview)
        selected_text_box.config(yscrollcommand=selected_scroll.set)
        selected_scroll.pack(side="right", fill="y")
        selected_text_box.pack(side="left", fill="both", expand=True)

        # Button to open the output folder
        open_folder_btn = tk.Button(self, text="Open Output Folder", command=self.open_output_folder)
        open_folder_btn.pack(pady=10)

        # Navigation buttons
        get_navigation_buttons(self, "final_page", back_button_page="merge_columns_explanation_page")

    def on_show_frame(self):
        """
        Update the frame whenever it is shown.
        Retrieves the list of merged and non-merged columns from the previous page and displays them.
        """
        self.columns_which_cant_be_merged = self.controller.get_frame("column_selection_page").columns_which_cant_be_merged
        self.columns = self.controller.get_frame("column_selection_page").columns
        self.selected_columns = self.controller.get_frame("column_selection_page").selected_columns

        self.columns_which_have_not_been_merged = list(set(self.columns_which_cant_be_merged).union(set(self.columns).difference(set(self.selected_columns))))
        self.merge_text_box.insert("end", ', '.join(self.columns_which_have_not_been_merged))
        self.selected_text_box.insert("end", ', '.join(self.selected_columns))

    def open_output_folder(self):
        """
        Open the output folder using the default system file explorer.
        """
        output_folder = get_target_folder()
        if output_folder is None:
            return

        try:
            if sys.platform == 'win32':
                os.startfile(output_folder)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{output_folder}"')
            else:  # Linux variants
                os.system(f'xdg-open "{output_folder}"')
        except Exception as e:
            print(f"Failed to open the folder: {e}")
