import os

# Set environment variables BEFORE importing Roboflow libraries
os.environ["CORE_MODEL_GAZE_ENABLED"] = "False"
os.environ["CORE_MODEL_SAM_ENABLED"] = "False"
os.environ["CORE_MODEL_YOLO_WORLD_ENABLED"] = "False"
os.environ["USE_INFERENCE_MODELS"] = "False"

from inference import get_model
import json, cv2, numpy as np
import inference, supervision as sv
from nycdot_stream import NYCDOTStreamReader
from enum import IntEnum

class COCOVehicleClass(IntEnum):
    CAR = 2
    MOTORCYCLE = 3
    BUS = 5
    TRUCK = 7

class ParkingVisionCore:
    def __init__(self, zone_filepath: str = "zones.json", model_id: str = "yolov8n-640", confidence: float = 0.4):
        # Load zone matrix
        polygon_arr = self._load_zone_from_json(zone_filepath)
        
        # Instantiate a PolygonZone object for the West Curb parking lane
        self.zone = sv.PolygonZone(polygon=polygon_arr, triggering_anchors=[sv.Position.BOTTOM_CENTER])
        
        # Instantiate annotators for visualization
        self.zone_annotator = sv.PolygonZoneAnnotator(
            zone=self.zone,
            color=sv.Color.GREEN,
            thickness=1,
            text_scale=0.35,
            text_thickness=1,
            text_padding=6,
        )
        self.box_annotator = sv.BoxAnnotator(thickness=1)
        self.label_annotator = sv.LabelAnnotator(
            text_scale=0.16,
            text_thickness=1,
            text_padding=1,
            border_radius=1,
            text_position=sv.Position.TOP_LEFT,
            text_offset=(0, 0),
        )
        
        # Load Roboflow Inference Model
        self.confidence = confidence
        self.model = get_model(model_id=model_id)
        print(f"[Success] Loaded Roboflow model '{model_id}' with confidence threshold {confidence}.\n")

    def process_frame(self, frame: np.ndarray, verbose: bool = False) -> tuple[np.ndarray, int]:
        if verbose:
            print("[Verbose] Starting inference on frame...")

        # Run inference on the frame using the loaded model
        results = self.model.infer(frame, confidence=self.confidence)[0]
        
        # Convert the inference results to a Detections object for easier processing
        detections = sv.Detections.from_inference(results)

        if verbose:
            print(f"[Verbose] Total detections: {len(detections)}")

        # Vehicle detection filtering: Only keep detections that match vehicle class IDs
        vehicle_ids = [vehicle.value for vehicle in COCOVehicleClass]

        # Create a mask checking which detected class IDs match vehicles
        mask = np.isin(detections.class_id, vehicle_ids)
        vehicle_detections = detections[mask]

        if verbose:
            print(f"[Verbose] Vehicle detections: {len(vehicle_detections)}")

        # Check which vehicle detections are inside the defined zone
        is_inside_zone = self.zone.trigger(detections=vehicle_detections)

        # Slice vehicle_detections to only those inside the zone
        zone_vehicles = vehicle_detections[is_inside_zone]
        occupied_count = len(zone_vehicles)

        if verbose:
            print(f"[Verbose] Zone vehicles: {occupied_count}")

        # Make a copy of the frame; annotate the copy with zone, bounding boxes, and labels
        annotated_frame = frame.copy()
        labels = [
            f"{class_name} {confidence:0.2f}"
            for class_name, confidence in zip(vehicle_detections.data["class_name"], vehicle_detections.confidence)
        ]

        annotated_frame = self.box_annotator.annotate(scene=annotated_frame, detections=vehicle_detections)
        annotated_frame = self.label_annotator.annotate(scene=annotated_frame, detections=vehicle_detections, labels=labels)
        annotated_frame = self.zone_annotator.annotate(scene=annotated_frame)

        return annotated_frame, occupied_count
        
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
        

if __name__ == "__main__":
    
    YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
    vision_core = ParkingVisionCore(zone_filepath="zones.json", model_id="yolov8m-640", confidence=0.2)
    stream_reader = NYCDOTStreamReader(YORK_AVE_URL, poll_interval=120.0)
    
    print("\nStarting Vision Core Stream... Press 'q' in the window to exit.\n")
    
    while True:
        frame = stream_reader.get_latest_frame(force=True)
        if frame is not None:
            annotated_frame, occupied_count = vision_core.process_frame(frame)
            print(f"Occupied Count: {occupied_count}")

            # Source frame is 352x240 - upscale before viewing so boxes/labels are more visible
            display_frame = cv2.resize(annotated_frame, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
            
            cv2.putText(
                display_frame,
                f"West Curb Occupancy: {occupied_count} vehicles",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )
            
            cv2.imshow("NYC Curb Utilization - Vision Core", display_frame)
            
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()