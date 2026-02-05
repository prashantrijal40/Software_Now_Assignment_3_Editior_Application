"""
This is the main entry point for the Image Editor Application.

This module initializes and launches the Image Editor GUI application using tkinter.
It imports the ImageEditorApp class from the gui_app module and also sets up the main
window and application event loop.

Attributes used in this module:
    ImageEditorApp: The main GUI application class from gui_app module.
    tk: tkinter library for creating the GUI window.
    
    Before running this module, ensure that the gui_app.py, image_processor.py and history_manager.py files are in the same directory
    and that the required libraries from the requirement.txt are installed.
"""

# Import the ImageEditorApp class from gui_app.py
# Import the Tkinter library for creating GUI applications
from gui_app import ImageEditorApp
import tkinter as tk

# Check if this file is run directly (not imported)
if __name__ == "__main__":
    """Initialize and run the Image Editor application."""
    # To create the main tkinter window that will host the application
    root = tk.Tk()
    # To instantiate the ImageEditorApp class and pass the root window to it
    app = ImageEditorApp(root)
    # To start the event loop to display the GUI and handle user interactions
    root.mainloop()
