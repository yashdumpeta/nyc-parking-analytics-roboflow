import asyncio
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from financial_engine import ParkingFinancialEngine
from nycdot_stream import NYCDOTStreamReader
from vision_core import ParkingVisionCore
import cv2

# ---------------------------------------------------- ----------------------------------------------------

#Global Variables
global_state = {
    "annotated_frame" : None,
    "telemetry": {}
}


# Project Constants
YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
POLL_INTERVAL = 2.0

ZONE_FILEPATH = "zones.json"
MODEL_ID = "yolov8m-640"
CONFIDENCE_THRESHOLD = 0.4

HOURLY_RATE = 5.00
OPERATING_HOURS_PER_DAY = 12.5
TOTAL_CAPACITY = 7
WINDOW_SIZE = 20


# ---------------------------------------------------- ----------------------------------------------------

stream_reader = NYCDOTStreamReader(
    image_url=YORK_AVE_URL,
    poll_interval=POLL_INTERVAL
)

vision_core = ParkingVisionCore(
    zone_filepath=ZONE_FILEPATH,
    model_id=MODEL_ID,
    confidence=CONFIDENCE_THRESHOLD
)

financial_engine = ParkingFinancialEngine(
    hourly_rate=HOURLY_RATE,
    operating_hours_per_day=OPERATING_HOURS_PER_DAY,
    total_capacity=TOTAL_CAPACITY,
    window_size=WINDOW_SIZE
)


# ---------------------------------------------------- ----------------------------------------------------

async def vision_pipeline_loop():
    """
    Runs continuously in the background. Fetches the stream, runs inference, 
    and updates the global state without blocking API requests.
    """
    print("[System] Background AI Inference loop started...\n")
    while True:
        frame = await stream_reader.get_latest_frame_async()
        if frame is not None:
            # Run inference in a separate thread to keep the event loop responsive
            annotated_frame, occupied_count = await asyncio.to_thread(vision_core.process_frame, frame)
            telemetry = financial_engine.calculate_telemetry(occupied_count)
            
            # Update the global state
            global_state["annotated_frame"] = annotated_frame
            global_state["telemetry"] = telemetry
        await asyncio.sleep(0.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting...\n")
    asyncio.create_task(vision_pipeline_loop())
    yield
    print("App is shutting down...\n")


app = FastAPI(title="NYCDOT Parking Smart Analytics", lifespan=lifespan)
@app.get("/")
def root():
    """Returns a simple health/status message for the API root."""
    return {
        "message": "NYC Parking Smart Analytics API is running.",
        "routes": ["/api/v1/analytics", "/api/v1/frame"],
    }


@app.get("/api/v1/analytics")
def get_analytics():
    """Returns the latest JSON financial telemetry instantly."""
    return global_state["telemetry"]


async def frame_generator():
    """Generates a continuous byte stream of JPEG images."""
    while True:
        frame = global_state["annotated_frame"]
        if frame is not None:
            success, encoded_image = cv2.imencode(".jpg", frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + encoded_image.tobytes() + b'\r\n')
        
        # Non-blocking async sleep
        await asyncio.sleep(0.1)
        

@app.get("/api/v1/stream")
def get_video_stream():
    """
    Streams the live annotated video to the browser.
    """
    # Use multipart/x-mixed-replace to create a continuous video feed
    return StreamingResponse(
        frame_generator(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
    
    
@app.get("/api/v1/frame")
def get_latest_frame_image():
    """
    Returns the most recent annotated frame as a JPEG image.
    """
    frame = global_state["annotated_frame"]
    
    if frame is None:
        return {"error": "No frame processed yet. Call /api/v1/analytics first."}
    
    # Compress the NumPy array into a JPEG byte stream
    success, encoded_image = cv2.imencode(".jpg", frame)
    if not success:
        return {"error": "Failed to encode image"}
        
    # Return the raw image bytes with the correct HTTP media type
    return Response(content=encoded_image.tobytes(), media_type="image/jpeg")


    








