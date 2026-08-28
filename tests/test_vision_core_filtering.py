import numpy as np
import pytest
import supervision as sv


def test_vehicle_filtering_logic():
    # Simulate detections with a mix of cars, trucks, and people/pedestrians
    boxes = np.array([
        [10, 20, 50, 60],
        [70, 80, 110, 120],
        [130, 140, 150, 160],
        [170, 180, 210, 220],
    ])
    confidences = np.array([0.85, 0.75, 0.90, 0.65])
    # COCO class IDs: 2=car, 7=truck, 0=person, 1=bicycle
    class_ids = np.array([2, 7, 0, 1])
    class_names = ["car", "truck", "person", "bicycle"]

    detections = sv.Detections(
        xyxy=boxes,
        confidence=confidences,
        class_id=class_ids,
        data={"class_name": class_names},
    )

    VALID_VEHICLE_NAMES = {"car", "truck", "bus", "motorcycle", "van", "vehicle", "automobile"}
    EXCLUDED_NAMES = {"person", "pedestrian", "bicycle", "bench", "traffic light", "fire hydrant", "backpack", "umbrella", "handbag", "dog", "cat"}
    COCO_VEHICLE_IDS = {2, 3, 5, 7}

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

    filtered = detections[np.array(mask, dtype=bool)]

    # Only 'car' and 'truck' should remain (2 vehicles), 'person' and 'bicycle' must be rejected
    assert len(filtered) == 2
    assert "person" not in filtered.data["class_name"]
    assert "bicycle" not in filtered.data["class_name"]
    assert set(filtered.data["class_name"]) == {"car", "truck"}
