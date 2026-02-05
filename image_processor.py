"""image_processor

Small wrapper around OpenCV image operations used by the editor application.

This module exposes the `ImageProcessor` class which stores a single image
in `self.image` and provides common transformations such as grayscale,
blur, edge detection, brightness/contrast adjustment, rotation, flipping,
and resizing. Methods mutate the stored image in-place and return None.

Notes
- Methods assume `self.image` is a valid numpy array in BGR color order as
  used by OpenCV. Callers should set the image with `set_image()` first.
"""

import cv2
import numpy as np

# Define a class for image processing operations
class ImageProcessor:
    """Container for an image and simple OpenCV-based operations.

    Attributes:
        image (np.ndarray|None): Current image in BGR format or None.
    """
    # Constructor method, called when an ImageProcessor object is created
    def __init__(self):
        """Create a new ImageProcessor with no image loaded."""
        self.image = None
    # Method to set (assign) an image to the object
    def set_image(self, img):
        """
        Set the current image.

        Args:
            img (np.ndarray): Image array in BGR color order.
        """
        self.image = img
    # Method to get (return) the current image
    def get_image(self):
        """Return the current image (may be None)."""
        return self.image
    # Method to convert the image to grayscale
    def grayscale(self):
        """
        Convert the current image to grayscale and keep it in BGR shape.

        The image is converted to a single-channel grayscale image and then
        back to BGR so downstream code can assume a 3-channel array.
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def blur(self, k): #need to fix
        """
        Apply a Gaussian blur to the image.

        Args:
            k (int): Kernel size. Will be coerced to an odd integer >= 1.
        """
        k = max(1, int(k))
        if k % 2 == 0:
            k += 1
        # (k, k) must be odd for GaussianBlur
        self.image = cv2.GaussianBlur(self.image, (k, k), 0)
    
    # Method to detect edges in the image
    def edge_detect(self):
        """
        Detecting edges using the Canny algorithm and store as BGR image.

        The Canny output is a single-channel binary edge map; we convert it
        back to BGR so the processor consistently exposes 3-channel images.
        """
        # Convert the image from BGR to grayscal
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        self.image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    # Method to adjust the brightness of the image
    def brightness(self, value):
        """
        Adjust image brightness by adding `value` to pixel intensities.

        Args:
            value (int): Value added to each pixel (positive -> brighter).
        """
        self.image = cv2.convertScaleAbs(self.image, alpha=1, beta=value)
    # Method to adjust the contrast of the image
    def contrast(self, value): #need to fix this
        """
        Adjust image contrast by scaling pixel intensities.

        Args:
            value (float): Multiplicative contrast factor (1.0 = no change).
        """
        self.image = cv2.convertScaleAbs(self.image, alpha=value, beta=0)

    # Rotate the image by a given angle (90, 180, or 270 degrees)
    def rotate(self, angle):
        """
        Rotate the image by one of the supported angles.

        Args:
            angle (int): Rotation angle in degrees. Supported values: 90, 180, 270.
        """
        if angle == 90:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.image = cv2.rotate(self.image, cv2.ROTATE_180)
        elif angle == 270:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # To flip the image either horizontally or vertically
    def flip(self, mode):
        """
        Flip the image horizontally or vertically.

        Args:
            mode (str): 'h' for horizontal flip, any other value for vertical.
        """
        if mode == "h":
            # Flip horizontally
            self.image = cv2.flip(self.image, 1)
        else:
            # Flip vertically
            self.image = cv2.flip(self.image, 0)

    # Resize the image by a scaling factor
    def resize(self, scale):
        """
        Resize the image by a scale factor.

        Args:
            scale (float): Multiplicative scale for width and height.
        """
        h, w = self.image.shape[:2]
        self.image = cv2.resize(self.image, (int(w * scale), int(h * scale)))
        
    def reset(self, original_img):
        """
        Replaces the current image with a fresh copy of the original.
        
        Args:
            original_img (np.ndarray): The backup copy of the original image.
        """
        if original_img is not None:
            self.image = original_img.copy()
