from sys import excepthook

import numpy as np
import time
import cv2
import requests

class NYCDOTStreamReader:
    def __init__(self, image_url : str, poll_interval: float = 2.0):
        print("Initialising NYC-DOT Stream Reader...\n")
        
        self.image_url = image_url
        self.poll_interval = poll_interval
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self._last_fetch_time = 0.0
        self._cached_frame = None
        

    
    def get_latest_frame(self) -> np.ndarray | None:
        
        current_time = time.time()
        if self._cached_frame is not None and ((current_time - self._last_fetch_time) < self.poll_interval):
            return self._cached_frame

        try:
            response = requests.get(self.image_url, headers=self.headers, timeout=5)
            response.raise_for_status()
        except requests.Timeout:
            print("Warning: timed out while fetching image; continuing.")
        except requests.RequestException as e:
            print(f"Warning: network error while fetching image: {e}")
        else:
            if response.status_code == 200:
                image_array = np.frombuffer(response.content, dtype=np.uint8)
                frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if frame is not None:
                    self._cached_frame = frame
                    self._last_fetch_time = current_time
                    print(f"Success! Image shape: {frame.shape}, dtype: {frame.dtype}\n")
                    return frame

        return None
            




if __name__ == "__main__":
    
    YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
    
    # 1. Instantiate your reader class
    stream_reader = NYCDOTStreamReader(YORK_AVE_URL, poll_interval=5.0)  
    
    # 2. Print a starting message
    print("Finished initialising NYC-DOT Stream Reader Object.\n")
    print("Starting stream loop... Press 'q' in the window to quit.\n")
    
    # 3. Enter a 'while True' loop:
    while(True):
        frame = stream_reader.get_latest_frame()
        
        
    #    - Call get_latest_frame()
    #    - If frame is not None, display it with cv2.imshow("NYC DOT Feed Test", frame)
    #    - Check cv2.waitKey(500) for key press 'q' to break the loop
    # 4. Clean up windows with cv2.destroyAllWindows()