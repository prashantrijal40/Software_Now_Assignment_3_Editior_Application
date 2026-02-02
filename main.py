#import the ImageEditorApp class that contains all GUI features of the editor
from gui_app import ImageEditorApp

#import tkinter library to create the window and handle GUI
import tkinter as tk

# start the application only when this file is run directly
if __name__ == "__main__":
    root = tk.Tk()                #create main window
    app = ImageEditorApp(root)    #load the image editor into the window
    root.mainloop()               # run the GUI Loop
