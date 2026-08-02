import numpy as np
import time
import cv2
import requests

class NYCDOTStreamReader:
    def __init__(self, image_url : str, poll_interval: float = 2.0):
        self.image_url = image_url
        self.poll_interval = poll_interval
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self._last_fetch_time = 0.0
        self._cached_frame = None
        
        print("Initialised NYC-DOT Stream Reader...\n")

    
    def get_latest_frame(self) -> np.ndarray | None:
        
        
        
        return None





if __name__ == "__main__":
    
    TEST_URL = "https://webcams.nyctmc.org/google_popup.php?cid=1022"
    
    # 1. Instantiate your reader class
    # 2. Print a starting message
    # 3. Enter a 'while True' loop:
    #    - Call get_latest_frame()
    #    - If frame is not None, display it with cv2.imshow("NYC DOT Feed Test", frame)
    #    - Check cv2.waitKey(500) for key press 'q' to break the loop
    # 4. Clean up windows with cv2.destroyAllWindows()