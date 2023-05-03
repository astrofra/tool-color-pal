# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Image Viewer")
        self.geometry("800x600")

        self.zoom_factor = 1.0
        self.zoom_factors = [1.0, 1.5, 2.0, 2.5, 3.0]

        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open", command=self.open_file)

        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, pady=10)

        zoom_in_button = tk.Button(control_frame, text="+", command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT)

        zoom_out_button = tk.Button(control_frame, text="-", command=self.zoom_out)
        zoom_out_button.pack(side=tk.LEFT)

        self.label = tk.Label(self)
        self.label.pack(expand=True, padx=20, pady=20)

    def open_file(self):
        file_name = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])

        if file_name:
            self.original_image = Image.open(file_name)
            self.display_image()

    def display_image(self):
        image = self.original_image.resize((int(self.original_image.width * self.zoom_factor), int(self.original_image.height * self.zoom_factor)), Image.ANTIALIAS)
        tk_image = ImageTk.PhotoImage(image)

        self.label.config(image=tk_image)
        self.label.image = tk_image

    def zoom_in(self):
        if self.zoom_factor < self.zoom_factors[-1]:
            current_index = self.zoom_factors.index(self.zoom_factor)
            self.zoom_factor = self.zoom_factors[current_index + 1]
            self.display_image()

    def zoom_out(self):
        if self.zoom_factor > self.zoom_factors[0]:
            current_index = self.zoom_factors.index(self.zoom_factor)
            self.zoom_factor = self.zoom_factors[current_index - 1]
            self.display_image()

if __name__ == "__main__":
    app = ImageViewer()
    app.mainloop()
