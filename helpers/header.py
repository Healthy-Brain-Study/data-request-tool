import os
import tkinter as tk


class HeaderComponent(tk.Frame):
    total_steps = 13

    def __init__(self, parent, filename, step_name):
        super().__init__(parent)
        self.configure(bg='lightgray')  # Set background color to distinguish the header

        try:
            page_number = os.path.basename(filename).split("_")[1]
        except:
            page_number = 1

        # Step indicator
        step_indicator = f"Step {page_number} of {self.total_steps}: {step_name}"
        label = tk.Label(self, text=step_indicator, font=("Helvetica", 12), bg='lightgray')
        label.pack(side='left', padx=10, pady=5)
