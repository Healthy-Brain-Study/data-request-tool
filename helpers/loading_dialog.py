import tkinter as tk


class LoadingDialog:
    def __init__(self, parent, message="Loading columns, please wait..."):
        self.top = tk.Toplevel(parent)
        self.top.title("Loading")

        # Create a label inside the Toplevel window and pack it
        self.label = tk.Label(self.top, text=message, height=3, width=50)
        self.label.pack()

        # Make the dialog modal
        self.top.transient(parent)
        self.top.grab_set()

        # Center the dialog on the parent window
        self.center_window(parent)

    def update_text(self, text):
        self.label.config(text=text)

    def center_window(self, parent):
        parent.update_idletasks()  # Update "requested size" from geometry manager

        # Get the size of the parent window and the screen
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()

        # Size of the dialog
        dw = 300
        dh = 100

        # Calculate x, y coordinates to center the dialog on the parent window
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2

        # If the calculated coordinates are off-screen, adjust them
        if x + dw > sw:
            x = sw - dw
        if y + dh > sh:
            y = sh - dh
        if x < 0:
            x = 0
        if y < 0:
            y = 0

        self.top.geometry(f"{dw}x{dh}+{x}+{y}")

    def close(self):
        self.top.grab_release()
        self.top.destroy()
