from fastapi import FastAPI
from financial_engine import ParkingFinancialEngine
from nycdot_stream import NYCDOTStreamReader
from vision_core import ParkingVisionCore

#Global Variables
latest_annotated_frame = None


# Project Constants
YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
POLL_INTERVAL = 60.0

ZONE_FILEPATH = "zones.json"
MODEL_ID = "yolov8m-640"
CONFIDENCE_THRESHOLD = 0.4

HOURLY_RATE = 5.00
OPERATING_HOURS_PER_DAY = 12.5
TOTAL_CAPACITY = 7
WINDOW_SIZE = 20


# ------------------------------------

app = FastAPI(title="NYCDOT Parking Smart Analytics")


# TODO 1: Instantiate stream_reader (NYCDOTStreamReader)
stream_reader = NYCDOTStreamReader(
    image_url=YORK_AVE_URL,
    poll_interval=POLL_INTERVAL
)

# TODO 2: Instantiate vision_core (ParkingVisionCore with yolov8m-640)
vision_core = ParkingVisionCore(
    zone_filepath=ZONE_FILEPATH,
    model_id=MODEL_ID,
    confidence=CONFIDENCE_THRESHOLD
)

# TODO 3: Instantiate financial_engine (ParkingFinancialEngine)
financial_engine = ParkingFinancialEngine(
    hourly_rate=HOURLY_RATE,
    operating_hours_per_day=OPERATING_HOURS_PER_DAY,
    total_capacity=TOTAL_CAPACITY,
    window_size=WINDOW_SIZE
)








