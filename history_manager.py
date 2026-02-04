# Define a class to manage undo and redo operations for images
class HistoryManager:
     # Constructor method, called when a HistoryManager object is created
    def __init__(self):
        # Stack to store previous, undone image states
        self.undo_stack = []
        self.redo_stack = []

    def push(self, image): # Definining the function push
        if image is not None:
            self.undo_stack.append(image.copy())
            self.redo_stack.clear()

    def undo(self, current):
        if self.undo_stack:
            self.redo_stack.append(current.copy())
            return self.undo_stack.pop()
        return current

    def redo(self, current):
        if self.redo_stack:
            self.undo_stack.append(current.copy())
            return self.redo_stack.pop()
        return current
