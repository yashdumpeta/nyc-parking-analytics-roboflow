import json
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


def run_zone_drawer(image_url: str):
    global points
    stream_reader = NYCDOTStreamReader(image_url=image_url, poll_interval=5.0)
    frame = stream_reader.get_latest_frame()

    if frame is None:
        print("[Error] Could not fetch snapshot from NYC DOT feed.")
        return

    window_name = "West Curb Zone Drawer | 'r': Reset | 'e': New Image | 'c': Confirm | 'q': Quit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print("\n--- INSTRUCTIONS ---")
    print("1. Left-click along the 4 corners of the West Curb parking lane.")
    print("2. Press 'r' to reset points if you make a mistake.")
    print("3. Press 'e' to fetch a new image from the stream.")
    print("4. Press 'c' to confirm and print the NumPy array coordinates.")
    print("5. Press 'q' to quit.\n")
    
    failed_retries_count = 0
    while True:
        display_frame = frame.copy()  # Create a copy of the frame to draw on
        
        # TODO 5: Draw circles and lines for recorded points
        # Loop through 'points':
        for i, point in enumerate(points):
            #   a. Draw a small filled circle at each point using cv2.circle()
            cv2.circle(display_frame, point, radius=3, color=(0, 255, 0), thickness=-1)
            #   b. If i > 0, draw a line between points[i-1] and points[i] using cv2.line()
            if i > 0:
                cv2.line(display_frame, points[i - 1], point, color=(255, 0, 0), thickness=1)
        
        # close the polygon by connecting the last point to the first point if there are at least 3 points
        if len(points) >= 3:
            cv2.line(display_frame, points[-1], points[0], color=(255, 0, 0), thickness=1)  
            
        # Display the frame with drawn points and lines
        cv2.imshow(window_name, display_frame)
 
        key = cv2.waitKey(50) & 0xFF
        if key == ord('r'):
            points.clear()
            print("Points reset.")
        elif key == ord('e'):
            print("Fetching a new image...")
            new_frame = stream_reader.get_latest_frame(force=True)
            if new_frame is not None:
                frame = new_frame
                points.clear()
                failed_retries_count = 0
                print("New image loaded. Points reset.")
            else:
                failed_retries_count += 1
                print(f"[Warning] Could not fetch a new image. Please try again in a couple of seconds (Attempt {failed_retries_count}).")
                if failed_retries_count >= 5:
                    print(f"\n[Info] You have had {failed_retries_count} failed attempts to fetch a new image consecutively.")
                    print("This could be due to:")
                    print("  1. The NYCDOT webcam server rate-limiting requests or experiencing temporary downtime.")
                    print("  2. A temporary disruption in your network connection.")
                    print("  3. The camera stream URL itself being modified or offline.")
                    print("If this persists, please double-check your network or try restarting the script later.\n")
        elif key == ord('c'):
            if len(points) < 3:
                print("Error: At least 3 points are required to define a polygon.")
            else:
                data = {"zone_points": points}
                with open("zones.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"[Success] Zone points saved to 'zones.json': {points}")
                break
        elif key == ord('q'):
            print("Quitting...")
            break
                    
    cv2.destroyAllWindows()                
                
        
        

if __name__ == "__main__":
    YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
    run_zone_drawer(YORK_AVE_URL)
    