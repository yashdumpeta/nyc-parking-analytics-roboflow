"""
Manual diagnostic script for fetching and viewing a single NYC DOT webcam frame.
Run directly with: python tests/test_single_frame.py
"""

import cv2
import numpy as np
import requests

YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0"
}


def fetch_and_display():
    try:
        response = requests.get(YORK_AVE_URL, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            image_array = np.frombuffer(response.content, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if frame is not None:
                print(f"Success! Image shape: {frame.shape}, dtype: {frame.dtype}\n")
                cv2.imshow("Single Snapshot Test", frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print("Failed to decode image from buffer.")
        else:
            print(f"Failed to fetch image. Status code: {response.status_code}")
    except Exception as exc:
        print(f"Error fetching frame: {exc}")


if __name__ == "__main__":
    fetch_and_display()
