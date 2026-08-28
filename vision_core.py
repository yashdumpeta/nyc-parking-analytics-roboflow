import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_cache"))
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

# Set environment variables BEFORE importing Roboflow libraries
os.environ["CORE_MODEL_GAZE_ENABLED"] = "false"
os.environ["CORE_MODEL_SAM_ENABLED"] = "false"
os.environ["CORE_MODEL_YOLO_WORLD_ENABLED"] = "false"
os.environ["USE_INFERENCE_MODELS"] = "false"

from enum import IntEnum
import json
import cv2
import numpy as np
import supervision as sv
import torch

if hasattr(torch, "mps") and not hasattr(torch.mps, "current_device"):
    torch.mps.current_device = lambda: 0

from nycdot_stream import NYCDOTStreamReader


class COCOVehicleClass(IntEnum):
    CAR = 2
    MOTORCYCLE = 3
    BUS = 5
    TRUCK = 7


ANCHOR_MAP = {
    "BOTTOM_CENTER": sv.Position.BOTTOM_CENTER,
    "CENTER": sv.Position.CENTER,
    "BOTTOM_LEFT": sv.Position.BOTTOM_LEFT,
    "BOTTOM_RIGHT": sv.Position.BOTTOM_RIGHT,
    "TOP_CENTER": sv.Position.TOP_CENTER,
}


class ParkingVisionCore:
    DEFAULT_ZONE_POINTS = [[310, 61], [329, 65], [86, 152], [61, 137]]

    def __init__(
        self,
        zone_filepath: str = "zones.json",
        model_id: str = "yolov8m-640",
        confidence: float = 0.25,
        trigger_anchor: str = "BOTTOM_CENTER",
    ):
        self.zone_filepath = zone_filepath
        self.model_id = model_id
        self.confidence = confidence
        self.trigger_anchor_name = trigger_anchor if trigger_anchor in ANCHOR_MAP else "BOTTOM_CENTER"

        # Load base zone matrix
        self.base_polygon = self._load_zone_from_json(zone_filepath)
        self.current_polygon = self.base_polygon.copy()

        # Zone offset state
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0

        # Build PolygonZone and annotators
        self._rebuild_zone()

        # Annotators
        self.box_annotator = sv.BoxAnnotator(thickness=1)
        self.label_annotator = sv.LabelAnnotator(
            text_scale=0.18,
            text_thickness=1,
            text_padding=2,
            border_radius=2,
            text_position=sv.Position.TOP_LEFT,
            text_offset=(0, 0),
        )

        # Lazily load Roboflow inference model
        from inference import get_model

        self.model = get_model(model_id=model_id)
        print(f"[Success] Loaded Roboflow model '{model_id}' with confidence {confidence}.\n")

    def _rebuild_zone(self):
        anchor_enum = ANCHOR_MAP.get(self.trigger_anchor_name, sv.Position.BOTTOM_CENTER)
        self.zone = sv.PolygonZone(
            polygon=self.current_polygon,
            triggering_anchors=[anchor_enum],
        )
        self.zone_annotator = sv.PolygonZoneAnnotator(
            zone=self.zone,
            color=sv.Color.GREEN,
            thickness=1,
            text_scale=0.35,
            text_thickness=1,
            text_padding=6,
        )

    def update_confidence(self, confidence: float):
        self.confidence = max(0.01, min(1.0, float(confidence)))

    def update_model(self, model_id: str):
        if model_id != self.model_id:
            from inference import get_model

            print(f"[System] Switching model from '{self.model_id}' to '{model_id}'...")
            self.model = get_model(model_id=model_id)
            self.model_id = model_id

    def update_trigger_anchor(self, trigger_anchor: str):
        if trigger_anchor in ANCHOR_MAP:
            self.trigger_anchor_name = trigger_anchor
            self._rebuild_zone()

    def set_zone_offset(self, dx: int = 0, dy: int = 0, scale: float = 1.0):
        self.offset_x = dx
        self.offset_y = dy
        self.scale = scale

        cx = float(np.mean(self.base_polygon[:, 0]))
        cy = float(np.mean(self.base_polygon[:, 1]))

        transformed = []
        for x, y in self.base_polygon:
            nx = cx + (x - cx) * scale + dx
            ny = cy + (y - cy) * scale + dy
            transformed.append([int(round(nx)), int(round(ny))])

        self.current_polygon = np.array(transformed, dtype=np.int32)
        self._rebuild_zone()

    def reset_zone(self):
        self.current_polygon = self.base_polygon.copy()
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self._rebuild_zone()

    def get_current_zone(self) -> list[list[int]]:
        return self.current_polygon.tolist()

    def process_frame(
        self, frame: np.ndarray, verbose: bool = False
    ) -> tuple[np.ndarray, int, int, list[dict]]:
        """
        Runs inference and zone evaluation.
        Returns:
            annotated_frame: Frame with bounding boxes, zone polygon, and anchor dots.
            occupied_count: Number of vehicles inside the curb zone.
            total_detected_count: Total vehicles detected anywhere in the frame.
            detections_detail: Diagnostic list of every vehicle detection.
        """
        results = self.model.infer(frame, confidence=self.confidence)[0]
        detections = sv.Detections.from_inference(results)

        # Strict vehicle filter: only accept valid vehicle categories, never pedestrians or non-vehicles
        VALID_VEHICLE_NAMES = {"car", "truck", "bus", "motorcycle", "van", "vehicle", "automobile"}
        EXCLUDED_NAMES = {"person", "pedestrian", "bicycle", "bench", "traffic light", "fire hydrant", "backpack", "umbrella", "handbag", "dog", "cat"}
        COCO_VEHICLE_IDS = {2, 3, 5, 7}  # COCO: 2=car, 3=motorcycle, 5=bus, 7=truck (0=person!)

        if "class_name" in detections.data and len(detections) > 0:
            mask = []
            for cid, cname in zip(detections.class_id, detections.data["class_name"]):
                name_str = str(cname).strip().lower()
                if name_str in EXCLUDED_NAMES:
                    mask.append(False)
                elif name_str in VALID_VEHICLE_NAMES:
                    mask.append(True)
                elif cid in COCO_VEHICLE_IDS:
                    mask.append(True)
                else:
                    mask.append(False)
            mask = np.array(mask, dtype=bool)
        else:
            mask = np.isin(detections.class_id, list(COCO_VEHICLE_IDS))

        vehicle_detections = detections[mask]
        total_detected_count = len(vehicle_detections)

        # Determine which vehicles fall inside the curb zone
        is_inside_zone = self.zone.trigger(detections=vehicle_detections)
        zone_vehicles = vehicle_detections[is_inside_zone]
        occupied_count = len(zone_vehicles)

        annotated_frame = frame.copy()
        labels = [
            f"{class_name} {confidence:0.2f}"
            for class_name, confidence in zip(vehicle_detections.data.get("class_name", []), vehicle_detections.confidence)
        ] if len(vehicle_detections) > 0 else []

        # Annotate boxes and labels
        if len(vehicle_detections) > 0:
            annotated_frame = self.box_annotator.annotate(scene=annotated_frame, detections=vehicle_detections)
            annotated_frame = self.label_annotator.annotate(scene=annotated_frame, detections=vehicle_detections, labels=labels)

        # Annotate zone polygon
        annotated_frame = self.zone_annotator.annotate(scene=annotated_frame)

        # Build detailed diagnostic metadata and draw anchor dots
        detections_detail = []
        for i in range(len(vehicle_detections)):
            box = vehicle_detections.xyxy[i].tolist()
            cname = (
                vehicle_detections.data["class_name"][i]
                if "class_name" in vehicle_detections.data
                else f"class_{vehicle_detections.class_id[i]}"
            )
            conf = float(vehicle_detections.confidence[i])
            in_zone = bool(is_inside_zone[i])

            x1, y1, x2, y2 = box
            if self.trigger_anchor_name == "CENTER":
                anchor = [round((x1 + x2) / 2, 1), round((y1 + y2) / 2, 1)]
            elif self.trigger_anchor_name == "BOTTOM_LEFT":
                anchor = [round(x1, 1), round(y2, 1)]
            elif self.trigger_anchor_name == "BOTTOM_RIGHT":
                anchor = [round(x2, 1), round(y2, 1)]
            elif self.trigger_anchor_name == "TOP_CENTER":
                anchor = [round((x1 + x2) / 2, 1), round(y1, 1)]
            else:  # BOTTOM_CENTER
                anchor = [round((x1 + x2) / 2, 1), round(y2, 1)]

            # Draw visual anchor dot on frame (Green if inside zone, Red/Orange if outside)
            pt = (int(round(anchor[0])), int(round(anchor[1])))
            dot_color = (0, 255, 0) if in_zone else (0, 140, 255)
            cv2.circle(annotated_frame, pt, radius=3, color=dot_color, thickness=-1)
            cv2.circle(annotated_frame, pt, radius=4, color=(255, 255, 255), thickness=1)

            detections_detail.append({
                "class_name": str(cname),
                "confidence": round(conf, 3),
                "box": [round(c, 1) for c in box],
                "anchor": anchor,
                "in_zone": in_zone,
            })

        return annotated_frame, occupied_count, total_detected_count, detections_detail

    def _load_zone_from_json(self, file_path: str) -> np.ndarray:
        """Loads zone coordinates from JSON or falls back to default coordinates."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            zone_points = data["zone_points"]
            return np.array(zone_points, dtype=np.int32)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            print(
                f"[Warning] Could not load zone configuration from '{file_path}' ({exc}). "
                "Falling back to default York Ave curb polygon."
            )
            return np.array(self.DEFAULT_ZONE_POINTS, dtype=np.int32)


if __name__ == "__main__":
    YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
    vision_core = ParkingVisionCore(zone_filepath="zones.json", model_id="yolov8m-640", confidence=0.2)
    stream_reader = NYCDOTStreamReader(YORK_AVE_URL, poll_interval=120.0)

    print("\nStarting Vision Core Stream... Press 'q' in the window to exit.\n")

    while True:
        frame = stream_reader.get_latest_frame(force=True)
        if frame is not None:
            annotated_frame, occupied_count, total_count, details = vision_core.process_frame(frame)
            print(f"Occupied Count: {occupied_count} | Total Detected: {total_count}")

            display_frame = cv2.resize(annotated_frame, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
            cv2.putText(
                display_frame,
                f"West Curb: {occupied_count}/{total_count} in zone",
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