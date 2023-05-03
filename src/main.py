# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from functools import partial


class OctreeNode:
    def __init__(self, level, parent):
        self.color_count = 0
        self.red_sum = 0
        self.green_sum = 0
        self.blue_sum = 0
        self.children = [None] * 8
        self.level = level
        self.parent = parent

    def is_leaf(self):
        return self.color_count > 0

    def get_mean_color(self):
        return (
            self.red_sum // self.color_count,
            self.green_sum // self.color_count,
            self.blue_sum // self.color_count,
        )

    def insert(self, color):
        if self.level == 7:
            self.color_count += 1
            self.red_sum += color[0]
            self.green_sum += color[1]
            self.blue_sum += color[2]
        else:
            idx = self.get_color_index(color)
            if not self.children[idx]:
                self.children[idx] = OctreeNode(self.level + 1, self)
            self.children[idx].insert(color)

    def get_color_index(self, color):
        idx = 0
        mask = 0x80 >> self.level
        if color[0] & mask:
            idx |= 4
        if color[1] & mask:
            idx |= 2
        if color[2] & mask:
            idx |= 1
        return idx

    def merge(self):
        self.color_count = sum(child.color_count for child in self.children if child)
        self.red_sum = sum(child.red_sum for child in self.children if child)
        self.green_sum = sum(child.green_sum for child in self.children if child)
        self.blue_sum = sum(child.blue_sum for child in self.children if child)

        for i in range(8):
            self.children[i] = None

class Octree:
    def __init__(self):
        self.root = OctreeNode(0, None)
        self.leaf_nodes = []

    def insert(self, color):
        node = self.root
        while not node.is_leaf():
            idx = node.get_color_index(color)
            if not node.children[idx]:
                node.children[idx] = OctreeNode(node.level + 1, node)
                if node.children[idx].level == 7:
                    self.leaf_nodes.append(node.children[idx])
            node = node.children[idx]
        node.insert(color)

    def reduce_colors(self, num_colors):
        while len(self.leaf_nodes) > num_colors:
            min_node = min(self.leaf_nodes, key=lambda node: node.color_count)
            min_node.parent.merge()
            self.leaf_nodes.remove(min_node)
            self.leaf_nodes.extend(child for child in min_node.parent.children if child)

        return [node.get_mean_color() for node in self.leaf_nodes if node.is_leaf()]


class ImageViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Image Viewer")
        self.geometry("800x600")

        self.zoom_factor = 1.0
        self.zoom_factors = [0.25, 0.5, 1.0, 1.5,
                             2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        
        self.file_path = None
        self.file_observer = None

        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open", command=self.open_file)

        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, pady=10)

        zoom_in_button = tk.Button(
            control_frame, text="+", command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT)

        self.zoom_label = tk.Label(
            control_frame, text=f"{self.zoom_factor * 100:.0f}%")
        self.zoom_label.pack(side=tk.LEFT, padx=5)

        zoom_out_button = tk.Button(
            control_frame, text="-", command=self.zoom_out)
        zoom_out_button.pack(side=tk.LEFT)

        self.label = tk.Label(self)
        self.label.pack(expand=True, padx=20, pady=20)

        self.calculate_palette_button = tk.Button(self, text="Calculate Palette", command=self.calculate_palette)
        self.calculate_palette_button.pack(side="bottom")

        # Bind mouse wheel event
        self.label.bind("<MouseWheel>", self.on_mouse_wheel)

    def calculate_palette(self):
        if self.original_image is not None:
            octree = Octree()
            for y in range(self.original_image.height):
                for x in range(self.original_image.width):
                    color = self.original_image.getpixel((x, y))
                    r = (color[0] // 16) * 16
                    g = (color[1] // 16) * 16
                    b = (color[2] // 16) * 16
                    octree.insert((r, g, b))

            palette = octree.reduce_colors(16)

            print("Palette :")
            for color in palette:
                print(color)


    def open_file(self):
        file_name = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])

        if file_name:
            self.file_path = file_name
            self.original_image = Image.open(file_name)
            self.display_image()
            self.watch_file()

    def watch_file(self):
        if self.file_observer is not None:
            self.file_observer.stop()

        event_handler = FileSystemEventHandler()
        event_handler.on_modified = self.on_file_modified

        self.file_observer = Observer()
        self.file_observer.schedule(event_handler, os.path.dirname(self.file_path), recursive=False)
        self.file_observer.start()

    def on_file_modified(self, event):
        modified_file_path = os.path.join(event.src_path, os.path.basename(self.file_path))
        print(event)
        print(modified_file_path, " =? ", self.file_path)
        if os.path.abspath(modified_file_path) == os.path.abspath(self.file_path):
            self.original_image = Image.open(self.file_path)
            self.display_image()

    def display_image(self):
        if self.zoom_factor > 1.0:
            resample_method = Image.NEAREST
        else:
            resample_method = Image.ANTIALIAS

        image = self.original_image.resize(
            (int(self.original_image.width * self.zoom_factor),
             int(self.original_image.height * self.zoom_factor)),
            resample=resample_method,
        )
        tk_image = ImageTk.PhotoImage(image)

        self.label.config(image=tk_image)
        self.label.image = tk_image

    def update_zoom_label(self):
        self.zoom_label.config(text=f"{self.zoom_factor * 100:.0f}%")

    def zoom_in(self):
        if self.zoom_factor < self.zoom_factors[-1]:
            current_index = self.zoom_factors.index(self.zoom_factor)
            self.zoom_factor = self.zoom_factors[current_index + 1]
            self.display_image()
            self.update_zoom_label()

    def zoom_out(self):
        if self.zoom_factor > self.zoom_factors[0]:
            current_index = self.zoom_factors.index(self.zoom_factor)
            self.zoom_factor = self.zoom_factors[current_index - 1]
            self.display_image()
            self.update_zoom_label()

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()


if __name__ == "__main__":
    app = ImageViewer()
    app.mainloop()
