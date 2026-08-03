from inference import get_model
import json, cv2, numpy as np
import inference, supervision
from nycdot_stream import NYCDOTStreamReader

class ParkingVisionCore:
    
    def _load_zone_from_json(file_path: str) -> np.ndarray:
        """
        Loads zone coordinates from JSON and returns a 2D int32 NumPy array.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            zone_points = data["zone_points"]
            
            return np.array(zone_points, dtype=np.int32)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"[Error] Zone configuration file '{file_path}' not found. "
                "Please run zone_drawer.py first to generate it!"
            )
        except KeyError:
            raise KeyError(
                f"[Error] Key 'zone_points' not found in '{file_path}'."
            )
        
    def __init__(self):
