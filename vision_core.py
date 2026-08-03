import os
# Set environment variables BEFORE importing Roboflow libraries
os.environ["CORE_MODEL_GAZE_ENABLED"] = "False"
os.environ["CORE_MODEL_SAM_ENABLED"] = "False"
os.environ["CORE_MODEL_YOLO_WORLD_ENABLED"] = "False"

from inference import get_model
import json, cv2, numpy as np
import inference, supervision as sv
from nycdot_stream import NYCDOTStreamReader



class ParkingVisionCore:
    
    def _load_zone_from_json(self, file_path: str) -> np.ndarray:
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
        
    def __init__(self, zone_filepath: str = "zones.json", model_id: str = "yolov8n-640", confidence: float = 0.4):
        
        # Load zone matrix
        polygon_arr = self._load_zone_from_json(zone_filepath)
        
        # Instantiate a PolygonZone object for the West Curb parking lane
        self.zone = sv.PolygonZone(polygon=polygon_arr, triggering_anchors=[sv.Position.BOTTOM_CENTER])
        
        # Instantiate annotators for visualization
        self.zone_annotator = sv.PolygonZoneAnnotator(zone=self.zone, color=sv.Color.GREEN, thickness=2)
        self.box_annotator = sv.BoxAnnotator(thickness=2)
        self.label_annotator = sv.LabelAnnotator(text_scale=0.5)
        
        # Load Roboflow Inference Model
        self.confidence = confidence
        self.model = get_model(model_id=model_id)
        print(f"[Success] Loaded Roboflow model '{model_id}' with confidence threshold {confidence}.\n")



if __name__ == "__main__":
    vision_core = ParkingVisionCore(zone_filepath="zones.json", model_id="yolov8n-640", confidence=0.4)