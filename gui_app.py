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
    """
    Main application window for the image editor.

    Args:
        root (tk.Tk): The Tkinter root window to attach the UI to.
    """

    def __init__(self, root):
        """
        Initialize the ImageEditorApp with the main window.
        
        Args:
            root (tk.Tk): The Tkinter root window to attach the UI to.
        """
        # Store the root window reference
        self.root = root
        # Set window title
        self.root.title("HIT137 Image Editor")
        # Set initial window size (width x height)
        self.root.geometry("1000x600")

        # Core components: image processor and undo/redo history
        # ImageProcessor handles all image transformations
        self.processor = ImageProcessor()
        # HistoryManager manages undo/redo functionality
        self.history = HistoryManager()
        # Track the current file path for save operations
        self.current_path = None

        # Build the menu bar
        self.create_menu()
        # Build the main user interface
        self.create_ui()

    def create_menu(self):
        """
        Create the application menu bar with File and Edit menus.
        
        File menu includes: Open, Save, Save As, and Exit options.
        Edit menu includes: Undo and Redo options.
        """
        # Create the main menu bar
        menubar = tk.Menu(self.root)

        # Create File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_image)
        filemenu.add_command(label="Save", command=self.save_image)
        filemenu.add_command(label="Save As", command=self.save_as)
        filemenu.add_separator()  # Add a visual separator
        filemenu.add_command(label="Exit", command=self.root.quit)

        # Create Edit menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_command(label="Redo", command=self.redo)

        # Add menus to the menu bar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)

        # Attach the menu bar to the root window
        self.root.config(menu=menubar)

    def create_ui(self):
        """
        Build the main UI layout with image canvas and control panel.

        Layout:
        - Left area: Canvas displaying the current image
        - Right area: Control panel with transformation buttons and sliders
        - Bottom area: Status bar showing file name and image dimensions
        """
        # Create main container frame that holds the image canvas and control panel
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        # Image display area (uses a Label to hold a PhotoImage)
        # The canvas shows the currently loaded/edited image
        self.canvas = tk.Label(main, bg="gray")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right-side control panel containing transformation buttons and sliders
        panel = tk.Frame(main, width=200)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Transformation buttons: Grayscale and Edge Detection
        tk.Button(panel, text="Grayscale", command=self.do_grayscale).pack(fill=tk.X)
        tk.Button(panel, text="Edge Detection", command=self.do_edge).pack(fill=tk.X)
        
        # Blur slider control
        # Range: 1 to 31 (must be odd for kernel size)
        tk.Label(panel, text="Blur").pack()
        self.blur_slider = tk.Scale(panel, from_=1, to=31, orient=tk.HORIZONTAL, command=self.do_blur)
        self.blur_slider.pack(fill=tk.X)

        # Brightness slider control
        # Range: -100 to 100 for darker to brighter adjustments
        tk.Label(panel, text="Brightness").pack()
        self.brightness_slider = tk.Scale(panel, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.do_brightness)
        self.brightness_slider.pack(fill=tk.X)

        # Contrast slider control
        # Range: 1.0 to 5.0 in steps of 0.1 for contrast adjustment
        tk.Label(panel, text="Contrast").pack()
        self.contrast_slider = tk.Scale(panel, from_=1, to=5, resolution=0.1, orient=tk.HORIZONTAL, command=self.do_contrast)
        self.contrast_slider.pack(fill=tk.X)

        # Rotation buttons: 90, 180, 270 degrees
        tk.Button(panel, text="Rotate 90", command=lambda: self.do_rotate(90)).pack(fill=tk.X)
        tk.Button(panel, text="Rotate 180", command=lambda: self.do_rotate(180)).pack(fill=tk.X)
        tk.Button(panel, text="Rotate 270", command=lambda: self.do_rotate(270)).pack(fill=tk.X)

        # Flip buttons: horizontal and vertical flipping
        tk.Button(panel, text="Flip Horizontal", command=lambda: self.do_flip("h")).pack(fill=tk.X)
        tk.Button(panel, text="Flip Vertical", command=lambda: self.do_flip("v")).pack(fill=tk.X)

        # Resize buttons: scale by 0.5x and 1.5x factors
        tk.Button(panel, text="Resize 50%", command=lambda: self.do_resize(0.5)).pack(fill=tk.X)
        tk.Button(panel, text="Resize 150%", command=lambda: self.do_resize(1.5)).pack(fill=tk.X)

        # Status bar at the bottom: displays file name and image dimensions
        self.status = tk.Label(self.root, text="No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Helpers ----------

    def check_image(self):
        """
        Verify that an image is loaded before performing operations.
        
        Returns:
            bool: True if an image is loaded, False otherwise.
                 Shows an error dialog if no image is loaded.
        """
        # Check if the processor has a valid image loaded
        if self.processor.get_image() is None:
            # Show error message box to the user
            messagebox.showerror("Error", "Please open an image first!")
            return False
        return True

    def update_display(self):
        """
        Refresh the canvas and status bar to reflect the current image.
        
        Converts the OpenCV BGR image to RGB for Tkinter display and updates
        the status bar with file name and image dimensions.
        """
        # Get the current image from the processor
        img = self.processor.get_image()
        # Convert BGR (OpenCV standard) to RGB (Pillow/Tkinter standard)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Convert numpy array to PIL Image
        pil = Image.fromarray(rgb)
        # Convert PIL Image to Tkinter PhotoImage for display
        tkimg = ImageTk.PhotoImage(pil)
        # Update the canvas label with the new image
        self.canvas.config(image=tkimg)
        # Keep a reference to prevent garbage collection of the image
        self.canvas.image = tkimg

        # Get image dimensions (height, width, channels)
        h, w = img.shape[:2]
        # Extract filename from path, or use "Unsaved" if no path
        name = self.current_path.split("/")[-1] if self.current_path else "Unsaved"
        # Update status bar with filename and dimensions
        self.status.config(text=f"{name} - {w}x{h}")

    # ---------- File ----------

    def open_image(self):
        """
        Open an image file and load it into the processor.
        
        Prompts user with a file dialog to select an image file (.jpg, .png, .bmp),
        loads it into the ImageProcessor, resets the undo/redo history, and updates
        the display.
        """
        # Show file dialog and get selected file path
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.bmp")])
        if path:
            # Read the image file using OpenCV (returns BGR numpy array)
            img = cv2.imread(path)
            # Load the image into the processor
            self.processor.set_image(img)
            # Store the file path for future save operations
            self.current_path = path
            # Reset history when a new file is opened to avoid mixing undo/redo from different images
            self.history = HistoryManager()
            # Refresh the display with the new image
            self.update_display()

    def save_image(self):
        """
        Save the current image to the existing file path.
        
        If no path has been set (e.g., new unsaved image), this method does nothing.
        Use save_as() to save to a new path.
        """
        # Verify that an image is loaded
        if not self.check_image():
            return
        # Check if a file path exists from a previous open or save operation
        if self.current_path:
            # Write the current image to the existing file path
            cv2.imwrite(self.current_path, self.processor.get_image())
            # Show confirmation message to user
            messagebox.showinfo("Saved", "Image saved!")

    def save_as(self):
        """
        Save the current image to a user-selected path.
        
        Prompts user with a file dialog to choose a save location and filename,
        then writes the current image to that path. Updates current_path after save.
        """
        # Verify that an image is loaded
        if not self.check_image():
            return
        # Show save dialog with .jpg as default extension
        path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if path:
            # Write the current image to the selected path
            cv2.imwrite(path, self.processor.get_image())
            # Update current_path so subsequent save() calls use this new path
            self.current_path = path

    # ---------- Undo / Redo ----------

    def undo(self):
        """
        Undo the last operation using HistoryManager.
        
        Retrieves the previous image state from the undo stack and updates the display.
        """
        # Verify that an image is loaded before attempting undo
        if self.check_image():
            # Get the previous state from the history manager
            previous_image = self.history.undo(self.processor.get_image())
            # Load the previous state into the processor
            self.processor.set_image(previous_image)
            # Refresh the display
            self.update_display()

    def redo(self):
        """
        Redo the last undone operation using HistoryManager.
        
        Retrieves a previously undone image state from the redo stack and updates the display.
        """
        # Verify that an image is loaded before attempting redo
        if self.check_image():
            # Get the next state from the history manager
            next_image = self.history.redo(self.processor.get_image())
            # Load the next state into the processor
            self.processor.set_image(next_image)
            # Refresh the display
            self.update_display()

    # ---------- Actions ----------

    def apply(self, func):
        """
        Helper method that encapsulates the pattern of applying transformations.
        
        This method:
        1. Verifies an image is loaded
        2. Pushes the current state to the undo history
        3. Applies the transformation function
        4. Updates the display
        
        Args:
            func: A callable that performs the transformation on self.processor.image.
        """
        # Verify that an image is loaded before applying transformation
        if not self.check_image():
            return
        # Save the current state to enable undo functionality
        self.history.push(self.processor.get_image())
        # Apply the transformation function
        func()
        # Refresh the display with the transformed image
        self.update_display()
    # ---------- Action wrappers (connected to UI controls) ----------
    # Each wrapper calls apply() with the appropriate processor method.
    # All operations are tracked in undo/redo history.
    
    def do_grayscale(self):
        """
        Apply grayscale filter to the current image.
        
        Converts the image from color to grayscale.
        This operation is recorded in the undo history.
        """
        self.apply(self.processor.grayscale)

    def do_edge(self):
        """
        Apply edge detection to the current image.
        
        Detects edges in the image using the Canny edge detection algorithm.
        This operation is recorded in the undo history.
        """
        self.apply(self.processor.edge_detect)

    def do_rotate(self, a):
        """
        Rotate the image by the specified angle.
        
        Args:
            a (int): Rotation angle in degrees (typically 90, 180, or 270).
        """
        # Use lambda to pass the angle parameter to the rotate method
        self.apply(lambda: self.processor.rotate(a))

    def do_flip(self, m):
        """
        Flip the image horizontally or vertically.
        
        Args:
            m (str): 'h' for horizontal flip, any other value for vertical flip.
        """
        # Use lambda to pass the mode parameter to the flip method
        self.apply(lambda: self.processor.flip(m))

    def do_resize(self, s):
        """
        Resize the image by the specified scale factor.
        
        Args:
            s (float): Scale factor (e.g., 0.5 for 50%, 1.5 for 150%).
        """
        # Use lambda to pass the scale factor to the resize method
        self.apply(lambda: self.processor.resize(s))

    def do_blur(self, v):
        """
        Apply blur filter with kernel size from the slider.
        
        Args:
            v (str): Slider value converted to int for kernel size.
                    Must be an odd number between 1 and 31.
        """
        # Convert slider value to int and pass to blur method
        self.apply(lambda: self.processor.blur(int(v)))

    def do_brightness(self, v):
        """
        Adjust image brightness using the slider value.
        
        Args:
            v (str): Slider value converted to int for brightness adjustment.
                    Range: -100 (darker) to 100 (brighter).
        """
        # Convert slider value to int and pass to brightness method
        self.apply(lambda: self.processor.brightness(int(v)))

    def do_contrast(self, v):
        """
        Adjust image contrast using the slider value.
        
        Args:
            v (str): Slider value converted to float for contrast adjustment.
                    Range: 1.0 (low contrast) to 5.0 (high contrast).
        """
        # Convert slider value to float and pass to contrast method
        self.apply(lambda: self.processor.contrast(float(v)))
