import cv2
import numpy as np
from nycdot_stream import NYCDOTStreamReader

points = []  # List to store the clicked points


def mouse_callback(event, x, y, flags, param):
    """
    Mouse event callback function.
    Fires automatically whenever a mouse event occurs inside the OpenCV window.
    """
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x,y))
        print(f"Point recorded: ({x}, {y})")

