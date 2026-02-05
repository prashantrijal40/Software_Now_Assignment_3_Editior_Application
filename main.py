"""
This is the main entry point for the Image Editor Application.

This module initializes and launches the Image Editor GUI application using tkinter.
It imports the ImageEditorApp class from the gui_app module and also sets up the main
window and application event loop.

Attributes used in this module:
    ImageEditorApp: The main GUI application class from gui_app module.
    tk: tkinter library for creating the GUI window.
"""

from gui_app import ImageEditorApp
import tkinter as tk


if __name__ == "__main__":
    """Initialize and run the Image Editor application."""
    # To create the main tkinter window that will host the application
    root = tk.Tk()
    
    # To instantiate the ImageEditorApp class and pass the root window to it
    app = ImageEditorApp(root)
    
    # To start the event loop to display the GUI and handle user interactions
    root.mainloop()
