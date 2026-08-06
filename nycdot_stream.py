import time

import cv2
import numpy as np
import requests
import httpx


class NYCDOTStreamReader:
    def __init__(self, image_url: str, poll_interval: float = 60.0) -> None:
        print("Initializing NYC-DOT Stream Reader...\n")

        self.image_url = image_url
        self.poll_interval = poll_interval
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self._last_fetch_time = 0.0
        self._cached_frame = None

    def get_latest_frame(self, force: bool = False) -> np.ndarray | None:
        current_time = time.time()

        if not force and self._cached_frame is not None and ((current_time - self._last_fetch_time) < self.poll_interval):
            return self._cached_frame

        try:
            response = requests.get(self.image_url, headers=self.headers, timeout=5)
            response.raise_for_status()
        except requests.Timeout:
            print("Warning: timed out while fetching image; continuing.")
        except requests.RequestException as exc:
            print(f"Warning: network error while fetching image: {exc}")
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

    async def get_latest_frame_async(self, force: bool = False) -> np.ndarray | None:
        current_time = time.time()

        if not force and self._cached_frame is not None and ((current_time - self._last_fetch_time) < self.poll_interval):
            return self._cached_frame

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.image_url, headers=self.headers, timeout=5.0)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"Warning: error while fetching image: {exc}")
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

    stream_reader = NYCDOTStreamReader(YORK_AVE_URL, poll_interval=120.0)

    print("Finished initializing NYC-DOT Stream Reader object.\n")
    print("Starting stream loop... Press 'q' in the window to quit.\n")

    while True:
        frame = stream_reader.get_latest_frame()

        if frame is not None:
            cv2.imshow("NYC DOT Feed Test", frame)

        if cv2.waitKey(500) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
        