import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.image = None

    def set_image(self, img):
        self.image = img

    def get_image(self):
        return self.image

    def grayscale(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def blur(self, k):
        k = max(1, int(k))
        if k % 2 == 0:
            k += 1
        self.image = cv2.GaussianBlur(self.image, (k, k), 0)

    def edge_detect(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        self.image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def brightness(self, value):
        self.image = cv2.convertScaleAbs(self.image, alpha=1, beta=value)

    def contrast(self, value):
        self.image = cv2.convertScaleAbs(self.image, alpha=value, beta=0)

    def rotate(self, angle):
        if angle == 90:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.image = cv2.rotate(self.image, cv2.ROTATE_180)
        elif angle == 270:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def flip(self, mode):
        if mode == "h":
            self.image = cv2.flip(self.image, 1)
        else:
            self.image = cv2.flip(self.image, 0)

    def resize(self, scale):
        h, w = self.image.shape[:2]
        self.image = cv2.resize(self.image, (int(w * scale), int(h * scale)))
