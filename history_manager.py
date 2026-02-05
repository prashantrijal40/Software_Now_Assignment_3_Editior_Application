# Define a class to manage undo and redo operations for images
class HistoryManager:
    """
    Manages undo/redo functionality for image editing operations.
    
    This class maintains two stacks to track image states:
    - undo_stack: stores previous states for undo operations
    - redo_stack: stores undone states for redo operations
    """
    
    # Constructor method, called when a HistoryManager object is created
    def __init__(self):
        """Initialize the HistoryManager with empty undo and redo stacks."""
        # Stack to store previous image states for undo operations
        self.undo_stack = []
        # Stack to store undone image states for redo operations
        self.redo_stack = []

    # Save the current image state before making changes
    # This allows us to undo later
    def push(self, image):
        """
        Push a copy of the current image state onto the undo stack.
        
        This is called when a new edit is made to the image.
        Clears the redo stack since a new edit invalidates redo history.
        
        Args:
            image: The image object to store. Must have a copy() method.
                   If None, the operation is skipped.
        """
        # Check if the image is not empty
        if image is not None:
            # Save a copy of the image to the undo stack
            self.undo_stack.append(image.copy())
            # Clear the redo stack because a new action was performed
            self.redo_stack.clear()
    # Define the undo function to restore the previous image state
    def undo(self, current):
        """
        Undo the last operation by reverting to the previous image state.
        
        Retrieves the previous state from the undo stack and saves the
        current state to the redo stack for potential redo operation.
        
        Args:
            current: The current image state to save in redo_stack.
        
        Returns:
            The previous image state from undo_stack, or current if 
            undo_stack is empty (no undo history available).
        """
        # Check if there are states available to undo
        if self.undo_stack:
            # Push current state to redo stack so it can be redone later
            self.redo_stack.append(current.copy())
            # Return the previous state from undo stack
            return self.undo_stack.pop()
        # If undo stack is empty, return current state unchanged
        return current
    # Define the redo function to reapply an undone image state
    def redo(self, current):
        """
        Redo the last undone operation by restoring a previously undone state.
        
        Retrieves a state from the redo stack and saves the current state
        to the undo stack to maintain undo history.
        
        Args:
            current: The current image state to save in undo_stack.
        
        Returns:
            The next image state from redo_stack, or current if redo_stack 
            is empty (no redo history available).
        """
        # Check if there are states available to redo
        if self.redo_stack:
            # Push current state to undo stack to maintain undo history
            self.undo_stack.append(current.copy())
            # Return the redone state from redo stack
            return self.redo_stack.pop()

        # If nothing to redo, return current unchanged
        return current
