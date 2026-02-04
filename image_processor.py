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


class ImageProcessor:
    """Container for an image and simple OpenCV-based operations.

    Attributes:
        image (np.ndarray|None): Current image in BGR format or None.
    """

    def __init__(self):
        """Create a new ImageProcessor with no image loaded."""
        self.image = None

    def set_image(self, img):
        """Set the current image.

        Args:
            img (np.ndarray): Image array in BGR color order.
        """
        self.image = img

    def get_image(self):
        """Return the current image (may be None)."""
        return self.image

    def grayscale(self):
        """Convert the current image to grayscale and keep it in BGR shape.

        The image is converted to a single-channel grayscale image and then
        back to BGR so downstream code can assume a 3-channel array.
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def blur(self, k):
        """Apply a Gaussian blur to the image.

        Args:
            k (int): Kernel size. Will be coerced to an odd integer >= 1.
        """
        k = max(1, int(k))
        if k % 2 == 0:
            k += 1
        # (k, k) must be odd for GaussianBlur
        self.image = cv2.GaussianBlur(self.image, (k, k), 0)

    def edge_detect(self):
        """Detecting edges using the Canny algorithm and store as BGR image.

        The Canny output is a single-channel binary edge map; we convert it
        back to BGR so the processor consistently exposes 3-channel images.
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        self.image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def brightness(self, value):
        """Adjust image brightness by adding `value` to pixel intensities.

        Args:
            value (int): Value added to each pixel (positive -> brighter).
        """
        self.image = cv2.convertScaleAbs(self.image, alpha=1, beta=value)

    def contrast(self, value):
        """Adjust image contrast by scaling pixel intensities.

        Args:
            value (float): Multiplicative contrast factor (1.0 = no change).
        """
        self.image = cv2.convertScaleAbs(self.image, alpha=value, beta=0)

    def rotate(self, angle):
        """Rotate the image by one of the supported angles.

        Args:
            angle (int): Rotation angle in degrees. Supported values: 90, 180, 270.
        """
        if angle == 90:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.image = cv2.rotate(self.image, cv2.ROTATE_180)
        elif angle == 270:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def flip(self, mode):
        """Flip the image horizontally or vertically.

        Args:
            mode (str): 'h' for horizontal flip, any other value for vertical.
        """
        if mode == "h":
            self.image = cv2.flip(self.image, 1)
        else:
            self.image = cv2.flip(self.image, 0)

    def resize(self, scale):
        """Resize the image by a scale factor.

        Args:
            scale (float): Multiplicative scale for width and height.
        """
        h, w = self.image.shape[:2]
        self.image = cv2.resize(self.image, (int(w * scale), int(h * scale)))
