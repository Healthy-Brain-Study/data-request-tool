from tkinter import ttk
import tkinter as tk


def go_to_next_page(page_instance, page):
    next_page = page_instance.controller.get_next_page(page)
    page_instance.controller.show_frame(next_page)


def get_navigation_buttons(page_instance, page, skip_to_page="", skip_button_name="Skip", next_button_name="Next", previous_button_name="Back", show_next=True, show_previous=True, back_button_page=""):
    "Function which adds navigation buttons to a given page, with the possibility to add a skip button to jump to a different page outside of the navigation."
    previous_page = page_instance.controller.get_previous_page(page)
    next_page = page_instance.controller.get_next_page(page)
    button_frame = tk.Frame(page_instance)
    button_frame.pack(side="bottom", fill="x")

    if next_page and show_next:
        def go_to_next_page():
            can_continue = False
            try:
                can_continue = page_instance.on_next_page()
            except:
                can_continue = True

            if can_continue:
                page_instance.controller.show_frame(next_page)

        ttk.Button(button_frame, text=next_button_name, command=go_to_next_page, width=15).pack(side='right', padx=5, pady=5)

    if previous_page and show_previous:
        if back_button_page:
            previous_page = back_button_page

        def go_to_previous_page():
            can_continue = False
            try:
                can_continue = page_instance.on_previous_page()
            except:
                can_continue = True

            if can_continue:
                page_instance.controller.show_frame(previous_page)

        ttk.Button(button_frame, text=previous_button_name, command=go_to_previous_page, width=15).pack(side='right', padx=5, pady=5)

    if skip_to_page:
        def go_to_skip_page():
            page_instance.controller.show_frame(skip_to_page)

        ttk.Button(button_frame, text=skip_button_name, command=go_to_skip_page).pack(side='right', padx=5, pady=5)
