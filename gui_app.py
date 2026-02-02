"""Simple Tkinter-based image editor GUI.

This module provides `ImageEditorApp`, a lightweight Tkinter application
that wraps `ImageProcessor` operations with a basic UI: open/save, undo/redo,
and common image transformations (grayscale, blur, edge detection,
brightness/contrast, rotate, flip, resize).

The GUI expects OpenCV-style BGR numpy arrays from `image_processor`.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from image_processor import ImageProcessor
from history_manager import HistoryManager


class ImageEditorApp:
    """Main application window for the image editor.

    Args:
        root (tk.Tk): The Tkinter root window to attach the UI to.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 Image Editor")
        self.root.geometry("1000x600")

        # Core components: image processor and undo/redo history
        self.processor = ImageProcessor()
        self.history = HistoryManager()
        self.current_path = None

        self.create_menu()
        self.create_ui()

    def create_menu(self):
        """Create the application menu (File / Edit)."""
        menubar = tk.Menu(self.root)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_image)
        filemenu.add_command(label="Save", command=self.save_image)
        filemenu.add_command(label="Save As", command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_command(label="Redo", command=self.redo)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)

        self.root.config(menu=menubar)

    def create_ui(self):
        """Build the main UI: image canvas and control panel.

        The left area shows the current image and the right panel exposes
        transformation controls and sliders.
        """
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        # Image display area (uses a Label to hold a PhotoImage)
        self.canvas = tk.Label(main, bg="gray")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right-side control panel
        panel = tk.Frame(main, width=200)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(panel, text="Grayscale", command=self.do_grayscale).pack(fill=tk.X)
        tk.Button(panel, text="Edge Detection", command=self.do_edge).pack(fill=tk.X)

        tk.Label(panel, text="Blur").pack()
        self.blur_slider = tk.Scale(panel, from_=1, to=31, orient=tk.HORIZONTAL, command=self.do_blur)
        self.blur_slider.pack(fill=tk.X)

        tk.Label(panel, text="Brightness").pack()
        self.brightness_slider = tk.Scale(panel, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.do_brightness)
        self.brightness_slider.pack(fill=tk.X)

        tk.Label(panel, text="Contrast").pack()
        self.contrast_slider = tk.Scale(panel, from_=1, to=5, resolution=0.1, orient=tk.HORIZONTAL, command=self.do_contrast)
        self.contrast_slider.pack(fill=tk.X)

        tk.Button(panel, text="Rotate 90", command=lambda: self.do_rotate(90)).pack(fill=tk.X)
        tk.Button(panel, text="Rotate 180", command=lambda: self.do_rotate(180)).pack(fill=tk.X)
        tk.Button(panel, text="Rotate 270", command=lambda: self.do_rotate(270)).pack(fill=tk.X)

        tk.Button(panel, text="Flip Horizontal", command=lambda: self.do_flip("h")).pack(fill=tk.X)
        tk.Button(panel, text="Flip Vertical", command=lambda: self.do_flip("v")).pack(fill=tk.X)

        tk.Button(panel, text="Resize 50%", command=lambda: self.do_resize(0.5)).pack(fill=tk.X)
        tk.Button(panel, text="Resize 150%", command=lambda: self.do_resize(1.5)).pack(fill=tk.X)

        self.status = tk.Label(self.root, text="No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Helpers ----------

    def check_image(self):
        """Return True if an image is loaded; otherwise show error and return False."""
        if self.processor.get_image() is None:
            messagebox.showerror("Error", "Please open an image first!")
            return False
        return True

    def update_display(self):
        """Refresh the canvas and status bar to reflect the current image."""
        img = self.processor.get_image()
        # Convert BGR (OpenCV) -> RGB (Pillow) before creating PhotoImage
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        tkimg = ImageTk.PhotoImage(pil)
        self.canvas.config(image=tkimg)
        # keep reference to avoid GC removing the image
        self.canvas.image = tkimg

        h, w = img.shape[:2]
        name = self.current_path.split("/")[-1] if self.current_path else "Unsaved"
        self.status.config(text=f"{name} - {w}x{h}")

    # ---------- File ----------

    def open_image(self):
        """Open an image file and load it into the processor."""
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.bmp")])
        if path:
            img = cv2.imread(path)
            self.processor.set_image(img)
            self.current_path = path
            # reset history when a new file is opened
            self.history = HistoryManager()
            self.update_display()

    def save_image(self):
        """Save the current image to the existing path (if any)."""
        if not self.check_image():
            return
        if self.current_path:
            cv2.imwrite(self.current_path, self.processor.get_image())
            messagebox.showinfo("Saved", "Image saved!")

    def save_as(self):
        """Save the current image to a user-selected path."""
        if not self.check_image():
            return
        path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if path:
            cv2.imwrite(path, self.processor.get_image())

    # ---------- Undo / Redo ----------

    def undo(self):
        """Undo the last operation using `HistoryManager`."""
        if self.check_image():
            self.processor.set_image(self.history.undo(self.processor.get_image()))
            self.update_display()

    def redo(self):
        """Redo the last undone operation using `HistoryManager`."""
        if self.check_image():
            self.processor.set_image(self.history.redo(self.processor.get_image()))
            self.update_display()

    # ---------- Actions ----------

    def apply(self, func):
        """Helper that pushes current state to history, applies `func`, updates UI.

        `func` is expected to be a callable that mutates `self.processor.image`.
        """
        if not self.check_image():
            return
        self.history.push(self.processor.get_image())
        func()
        self.update_display()
    # ---------- Action wrappers (connected to UI controls) ----------
    # Each small wrapper calls `apply` with the appropriate processor method.
    def do_grayscale(self):
        """Apply grayscale to the current image."""
        self.apply(self.processor.grayscale)

    def do_edge(self):
        """Apply edge detection to the current image."""
        self.apply(self.processor.edge_detect)

    def do_rotate(self, a):
        """Rotate the image by angle `a` (90/180/270)."""
        self.apply(lambda: self.processor.rotate(a))

    def do_flip(self, m):
        """Flip the image horizontally ('h') or vertically (other)."""
        self.apply(lambda: self.processor.flip(m))

    def do_resize(self, s):
        """Resize the image by scale factor `s`."""
        self.apply(lambda: self.processor.resize(s))

    def do_blur(self, v):
        """Blur with kernel size taken from slider value `v`."""
        self.apply(lambda: self.processor.blur(int(v)))

    def do_brightness(self, v):
        """Adjust brightness using slider value `v`."""
        self.apply(lambda: self.processor.brightness(int(v)))

    def do_contrast(self, v):
        """Adjust contrast using slider value `v`."""
        self.apply(lambda: self.processor.contrast(float(v)))
