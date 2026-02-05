"""
Main entry point for the Image Editor Application.

This module initializes and launches the Image Editor GUI application using tkinter.
It imports the ImageEditorApp class from the gui_app module and sets up the main
window and application event loop.

Attributes:
    ImageEditorApp: The main GUI application class from gui_app module.
    tk: tkinter library for creating the GUI window.
"""

from gui_app import ImageEditorApp
import tkinter as tk


if __name__ == "__main__":
    """Initialize and run the Image Editor application."""
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
