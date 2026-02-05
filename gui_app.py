"""Simple Tkinter-based image editor GUI.

This module provides `ImageEditorApp`, which is a lightweight Tkinter application
that wraps `ImageProcessor` operations with a basic UI: open/save, undo/redo,
and common image transformations (grayscale, blur, edge detection,
brightness/contrast, rotate, flip, resize).

The GUI expects OpenCV-style BGR numpy arrays from `image_processor`.
"""

# Import the Tkinter library for creating GUI applications
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
# Import OpenCV library for image processing
import cv2

# Import ImageProcessor class for image processing operations
from image_processor import ImageProcessor
# Import HistoryManager class for managing undo and redo action
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
        # To store the root window reference
        self.root = root
        # To set window title
        self.root.title("HIT137 Image Editor")
        # To set initial window size (width x height)
        self.root.geometry("1400x900")
        self.root.configure(bg="#2b2b2b")


        # Core components: image processor and undo/redo history
        # ImageProcessor handles all image transformations
        self.processor = ImageProcessor()
        # HistoryManager manages undo/redo functionality
        self.history = HistoryManager()
        # Track the current file path for save operations
        self.current_path = None
        
        self.original_image = None  # Add this to store the very first version
        
        # Track original image state before slider adjustments
        # This allows us to apply slider-based transformations without creating multiple history entries
        self.original_for_sliders = None

        # To build the menu bar
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
        - Left area: Canvas displaying the current image (scaled to fit)
        - Right area: Control panel with transformation buttons and sliders
        - Bottom area: Status bar showing file name and image dimensions
        """
        # Create main container frame that holds the image canvas and control panel
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        # Image display area (uses a Label to hold a PhotoImage)
        # The canvas shows the currently loaded/edited image
        self.canvas = tk.Label(main, bg="gray", text="No image loaded", fg="white", font=("Arial", 20))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Store canvas width and height for image scaling (updated when window is resized)
        self.canvas_width = 600
        self.canvas_height = 500

        # Right-side control panel containing transformation buttons and sliders
        # Use pack_propagate(False) to prevent the frame from shrinking below width=200
        panel = tk.Frame(main, width=260, bg="#e0e0e0")
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        panel.pack_propagate(False)  # Prevent frame from shrinking
        
        tk.Label(panel, text="Editor", font=("Arial", 24, "bold"), bg="#000000", fg="white").pack(pady=20)
        

        # Transformation buttons: Grayscale and Edge Detection
        tk.Button(panel, text="Grayscale", command=self.do_grayscale).pack(fill=tk.X, padx=10, pady=5)
        tk.Button(panel, text="Edge Detection", command=self.do_edge).pack(fill=tk.X, padx=10, pady=5)
        
        # Blur slider contro
        # Range: 1 to 31 (must be odd for kernel size)
        tk.Label(panel, text="Blur", bg="black").pack(padx=5, pady=(10, 5))
        self.blur_slider = tk.Scale(panel, from_=1, to=31, orient=tk.HORIZONTAL, command=self.do_blur)
        self.blur_slider.pack(fill=tk.X, padx=10)

        # Brightness slider control
        # Range: -100 to 100 for darker to brighter adjustments
        tk.Label(panel, text="Brightness", bg="black").pack(padx=5, pady=(10, 5))
        self.brightness_slider = tk.Scale(panel, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.do_brightness)
        self.brightness_slider.pack(fill=tk.X, padx=10)

        # Contrast slider control
        # Range: 1.0 to 5.0 in steps of 0.1 for contrast adjustment
        tk.Label(panel, text="Contrast", bg="black").pack(padx=5, pady=(10, 5))
        self.contrast_slider = tk.Scale(panel, from_=1, to=5, resolution=0.1, orient=tk.HORIZONTAL, command=self.do_contrast)
        self.contrast_slider.pack(fill=tk.X, padx=10)

        # Rotation buttons: 90, 180, 270 degrees
        tk.Button(panel, text="Rotate 90", command=lambda: self.do_rotate(90)).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(panel, text="Rotate 180", command=lambda: self.do_rotate(180)).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(panel, text="Rotate 270", command=lambda: self.do_rotate(270)).pack(fill=tk.X, padx=10, pady=2)

        # Flip buttons: horizontal and vertical flipping
        tk.Button(panel, text="Flip Horizontal", command=lambda: self.do_flip("h")).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(panel, text="Flip Vertical", command=lambda: self.do_flip("v")).pack(fill=tk.X, padx=10, pady=2)
        # Resize buttons: scale by 0.5x and 1.5x factors
        tk.Button(panel, text="Resize 50%", command=lambda: self.do_resize(0.5)).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(panel, text="Resize 150%", command=lambda: self.do_resize(1.5)).pack(fill=tk.X, padx=10, pady=2)

        # Status bar at the bottom: displays file name and image dimensions
        self.status = tk.Label(self.root, text="No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Button(panel, text="Undo", command=self.undo).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(panel, text="Redo", command=self.redo).pack(fill=tk.X, padx=10, pady=2)

        tk.Button(panel, text="RESET TO ORIGINAL", command=self.reset_image).pack(fill=tk.X, padx=10, pady=20)
    # ---------- Helpers ----------

    # Method to check whether an image is loaded before editing
    def check_image(self):
        """
        Verifying that image is loaded before performing operations.
        
        Returns:
            bool: True if an image is loaded, False otherwise.
                 Shows an error dialog if no image is loaded.
        """
        # Check if there is no image in the ImageProcessor
        if self.processor.get_image() is None:
            # Show error message box to the user
            messagebox.showerror("Error", "Please open an image first to Edit!")
            return False
        return True
    
    # Method to check whether an image is loaded before editing
    def update_display(self):
        """
        Refresh the canvas and status bar to reflect the current image.
        
        Converts the OpenCV BGR image to RGB for Tkinter display, scales the image
        to fit the available canvas area, and updates the status bar with file name
        and image dimensions.
        """
        # Get the current image from the processor
        img = self.processor.get_image()
        # Get image dimensions (height, width, channels)
        img_h, img_w = img.shape[:2]
        
        # To fit image in the available canvas area scaling factor is calculated
        # Leave space for the control panel (approximately 200 pixels)
        max_width = self.canvas.master.winfo_width() - 220  # Account for panel width
        max_height = self.canvas.master.winfo_height() - 30  # Account for status bar
        
        # Ensure we have valid dimensions
        if max_width < 100:
            max_width = 600
        if max_height < 100:
            max_height = 500
        
        # Calculate scale to fit image within the canvas while maintaining aspect ratio
        scale = min(max_width / img_w, max_height / img_h, 1.0)  # Don't upscale
        
        # Calculate new dimensions
        display_w = int(img_w * scale)
        display_h = int(img_h * scale)
        
        # Convert BGR (OpenCV standard) to RGB (Pillow/Tkinter standard)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Convert numpy array to PIL Image
        pil = Image.fromarray(rgb)
        # Resize PIL image for display
        pil = pil.resize((display_w, display_h), Image.Resampling.LANCZOS)
        # Convert PIL Image to Tkinter PhotoImage for display
        tkimg = ImageTk.PhotoImage(pil)
        # Update the canvas label with the new image
        self.canvas.config(image=tkimg)
        # Keep a reference to prevent garbage collection of the image
        self.canvas.image = tkimg

        # Extract filename from path, or use "Unsaved" if no path
        name = self.current_path.split("/")[-1] if self.current_path else "Unsaved"
        # Update status bar with filename and original image dimensions
        self.status.config(text=f"{name} - {img_w}x{img_h}")

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
            
            self.original_image = img.copy()  # Save the original image for slider resets
            
            self.current_path = path
            # Reset slider state tracking when a new image is opened
            self.original_for_sliders = None
            # Reset all sliders to their default positions
            self.blur_slider.set(1)
            self.brightness_slider.set(0)
            self.contrast_slider.set(1.0)
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
            # Reset slider state tracking
            self.original_for_sliders = None
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
            # Reset slider state tracking
            self.original_for_sliders = None
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
        # Reset slider state tracking since a new operation is being performed
        self.original_for_sliders = None
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
        
        This method applies blur based on the current slider value without
        creating intermediate history entries. The blur is applied to the 
        original image before any slider adjustment was made.
        
        Args:
            v (str): Slider value converted to int for kernel size.
                    Must be an odd number between 1 and 31.
        """
        # Check if an image is loaded
        if not self.check_image():
            return
        
        # On first slider movement, save the original state
        if self.original_for_sliders is None:
            self.original_for_sliders = self.processor.get_image().copy()
            # Push original state to history only once
            self.history.push(self.original_for_sliders)
        
        # Restore to original and apply current blur value
        self.processor.set_image(self.original_for_sliders.copy())
        self.processor.blur(int(v))
        self.update_display()

    def do_brightness(self, v):
        """
        Adjust image brightness using the slider value.
        
        This method adjusts brightness based on the current slider value without
        creating intermediate history entries. The adjustment is applied to the 
        original image before any slider adjustment was made.
        
        Args:
            v (str): Slider value converted to int for brightness adjustment.
                    Range: -100 (darker) to 100 (brighter).
        """
        # Check if an image is loaded
        if not self.check_image():
            return
        
        # On first slider movement, save the original state
        if self.original_for_sliders is None:
            self.original_for_sliders = self.processor.get_image().copy()
            # Push original state to history only once
            self.history.push(self.original_for_sliders)
        
        # Restore to original and apply current brightness value
        self.processor.set_image(self.original_for_sliders.copy())
        self.processor.brightness(int(v))
        self.update_display()  
        
    def reset_image(self):
        if self.original_image is not None:
        # Save current state to history before resetting (optional, but helpful)
           self.history.push(self.processor.get_image())
        
        # Restore the original image
           self.processor.set_image(self.original_image.copy())
        
        # Reset slider variables and tracking
           self.original_for_sliders = None
           self.blur_slider.set(1)
           self.brightness_slider.set(0)
           self.contrast_slider.set(1.0)
        
           self.update_display()
        else:
           messagebox.showwarning("Warning", "No original image to reset to!")   

    def do_contrast(self, v):
        """
        Adjust image contrast using the slider value.
        
        This method adjusts contrast based on the current slider value without
        creating intermediate history entries. The adjustment is applied to the 
        original image before any slider adjustment was made.
        
        Args:
            v (str): Slider value converted to float for contrast adjustment.
                    Range: 1.0 (low contrast) to 5.0 (high contrast).
        """
        # Check if an image is loaded
        if not self.check_image():
            return
        
        # On first slider movement, save the original state
        if self.original_for_sliders is None:
            self.original_for_sliders = self.processor.get_image().copy()
            # Push original state to history only once
            self.history.push(self.original_for_sliders)
        
        # Restore to original and apply current contrast value
        self.processor.set_image(self.original_for_sliders.copy())
        self.processor.contrast(float(v))
        self.update_display()   
