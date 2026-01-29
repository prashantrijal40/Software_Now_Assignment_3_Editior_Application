class HistoryManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, image):
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
