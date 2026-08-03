import json
import math
import cv2
import numpy as np
from nycdot_stream import NYCDOTStreamReader

points = []  # List to store the clicked points


def sort_points(pts):
    """
    Sorts a list of points (x, y) counter-clockwise/clockwise around their centroid
    to prevent self-intersecting polygons when drawn or saved.
    """
    if len(pts) <= 2:
        return pts
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    
    # Sort points by polar angle relative to the centroid
    return sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


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

    window_name = "West Curb Zone Drawer | 'z': Undo | 'r': Reset | 'e': New Image | 'c': Confirm | 'q': Quit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print("\n--- INSTRUCTIONS ---")
    print("1. Left-click along the 4 corners of the West Curb parking lane.")
    print("2. Press 'z' to undo/remove the last clicked point.")
    print("3. Press 'r' to reset all points.")
    print("4. Press 'e' to fetch a new image from the stream.")
    print("5. Press 'c' to confirm and print the NumPy array coordinates.")
    print("6. Press 'q' to quit.\n")
    
    failed_retries_count = 0
    while True:
        display_frame = frame.copy()  # Create a copy of the frame to draw on
        
        # Draw circles at original clicked positions
        for point in points:
            cv2.circle(display_frame, point, radius=3, color=(0, 255, 0), thickness=-1)
            
        # Sort points relative to centroid to form a clean, non-self-intersecting polygon
        sorted_pts = sort_points(points)
        for i in range(1, len(sorted_pts)):
            cv2.line(display_frame, sorted_pts[i - 1], sorted_pts[i], color=(255, 0, 0), thickness=1)
        
        # Close the polygon by connecting the last point to the first point if there are at least 3 points
        if len(sorted_pts) >= 3:
            cv2.line(display_frame, sorted_pts[-1], sorted_pts[0], color=(255, 0, 0), thickness=1)  
            
        # Display the frame with drawn points and lines
        cv2.imshow(window_name, display_frame)
 
        key = cv2.waitKey(50) & 0xFF
        if key == ord('z'):
            if points:
                removed = points.pop()
                print(f"Undo: Removed last recorded point {removed}")
            else:
                print("No points to undo.")
        elif key == ord('r'):
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
                sorted_pts = sort_points(points)
                data = {"zone_points": sorted_pts}
                with open("zones.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"[Success] Zone points saved to 'zones.json': {sorted_pts}")
                break
        elif key == ord('q'):
            print("Quitting...")
            break
                    
    cv2.destroyAllWindows()                
                
        
        

if __name__ == "__main__":
    YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
    run_zone_drawer(YORK_AVE_URL)
    