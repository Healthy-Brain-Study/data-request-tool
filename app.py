import ctypes
import os
import platform
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from pages.page_01_introduction import IntroductionPage
from pages.page_02_pep_install_instructions import PepInstallInstructionsPage
from pages.page_03_token_download_instructions import TokenDownloadInstructionsPage
from pages.page_04_token_upload import TokenUploadPage
from pages.page_05_pep_overview import PEPOverviewPage
from pages.page_06_download_folder_selection import DownloadFolderSelectionPage
from pages.page_07_download_progress import DownloadProgressPage
from pages.page_08_unzip import UnzipPage
from pages.page_09_merge_files_introduction import MergeFilesIntroductionPage
from pages.page_10_merge_participants_explanation import MergeParticipantsExplanationPage
from pages.page_11_merge_files_folder_selection import MergeFilesFolderSelectionPage
from pages.page_12_column_selection import ColumnSelectionPage
from pages.page_13_combine_columns_progress import CombineColumnsProgressPage
from pages.page_overview_final import FinalPage

from helpers.functions import get_filepath_for_executable


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except AttributeError:
    pass  # This will pass if the function is not available on the Windows version or if you're using Unix


class Controller(tk.Tk):
    """Main application controller that manages switching between different pages in the GUI.

    Attributes:
        container (tk.Frame): Container for all pages.
        frames (dict): Holds instances of all the pages.
        name_to_class_map (dict): Mapping of page names to their class types for dynamic instantiation.
        platform (str): Current operating system.
        logo_image (tk.PhotoImage): The application logo image for window icon.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the main application controller."""
        super().__init__(*args, **kwargs)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.platform = platform.system().lower()

        font_size = 12 if self.platform == "windows" else 14

        s = ttk.Style()
        s.configure(".", font=("Helvetica", font_size))

        self.name_to_class_map = {
            "introduction_page": IntroductionPage,
            "pep_install_instructions_page": PepInstallInstructionsPage,
            "token_download_instructions_page": TokenDownloadInstructionsPage,
            "token_upload_page": TokenUploadPage,
            "pep_overview_page": PEPOverviewPage,
            "download_folder_selection_page": DownloadFolderSelectionPage,
            "download_progress_page": DownloadProgressPage,
            "unzip_page": UnzipPage,
            "combine_columns_introduction_page": MergeFilesIntroductionPage,
            "merge_participants_explanation_page": MergeParticipantsExplanationPage,
            "combine_columns_folder_selection_page": MergeFilesFolderSelectionPage,
            "column_selection_page": ColumnSelectionPage,
            "combine_columns_progress_page": CombineColumnsProgressPage,
            "final_page": FinalPage
        }

        self.frames = {}
        for F in self.name_to_class_map.values():
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.title("HBS - Data Request Tool")

        icon_image = Image.open(get_filepath_for_executable(os.path.join('static', 'logo.png')))
        photo_icon = ImageTk.PhotoImage(icon_image)
        self.logo_image = photo_icon
        self.iconphoto(True, photo_icon)

        self.show_frame('start_page')

    def show_frame(self, name):
        """Raise the frame associated with 'name' to the top of the stack."""
        frame = self.frames[self.get_class_from_name(name)]
        frame.tkraise()

        try:
            frame.on_show_frame()
        except Exception:
            pass

    def get_next_page(self, page):
        """Get the name of the next page following 'page'."""
        if page in self.name_to_class_map:
            pages_list = list(self.name_to_class_map.keys())
            page_index = pages_list.index(page)

            if not (page_index + 1 > (len(pages_list) - 1)):
                return pages_list[page_index + 1]

        return ""

    def get_previous_page(self, page):
        """Get the name of the previous page before 'page'."""
        if page in self.name_to_class_map:
            pages_list = list(self.name_to_class_map.keys())
            page_index = pages_list.index(page)

            if page_index - 1 >= 0:
                return pages_list[page_index - 1]

        return ""

    def get_frame(self, name):
        """Return the frame associated with 'name'."""
        return self.frames[self.get_class_from_name(name)]

    def get_class_from_name(self, name):
        """Return the class associated with 'name' from the map; default to IntroductionPage."""
        return self.name_to_class_map.get(name, IntroductionPage)

    def adjust_window_size(self):
        """Adjust the window size based on the current layout."""
        self.update_idletasks()
        self.geometry("")


app = Controller()
app.mainloop()
