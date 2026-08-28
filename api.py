import asyncio
from contextlib import asynccontextmanager
import os
import tempfile
import time

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_cache"))
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

import cv2
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from financial_engine import ParkingFinancialEngine
from nycdot_stream import NYCDOTStreamReader
from vision_core import ParkingVisionCore

# --------------------------------------------------------------------------------------------------
# Project Constants & Defaults
# --------------------------------------------------------------------------------------------------
YORK_AVE_URL = "https://webcams.nyctmc.org/api/cameras/d45fb588-de4c-4139-9e27-5b2d4c371b3d/image"
POLL_INTERVAL = 1.0

ZONE_FILEPATH = "zones.json"
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "yolov8m-640")
DEFAULT_CONFIDENCE = 0.25
DEFAULT_ANCHOR = "BOTTOM_CENTER"

HOURLY_RATE = 5.00
OPERATING_HOURS_PER_DAY = 12.5
TOTAL_CAPACITY = 7
WINDOW_SIZE = 20

# --------------------------------------------------------------------------------------------------
# Global State
# --------------------------------------------------------------------------------------------------
global_state = {
    "annotated_frame": None,
    "telemetry": {},
    "active_streams_count": 0,
    "raw_occupied_count": 0,
    "total_detected_count": 0,
    "detections_detail": [],
    "last_updated": 0.0,
    "force_refresh_requested": False,
    "config": {
        "model_id": DEFAULT_MODEL_ID,
        "confidence_threshold": DEFAULT_CONFIDENCE,
        "trigger_anchor": DEFAULT_ANCHOR,
        "hourly_rate": HOURLY_RATE,
        "operating_hours_per_day": OPERATING_HOURS_PER_DAY,
        "total_capacity": TOTAL_CAPACITY,
        "zone_offset_x": 0,
        "zone_offset_y": 0,
        "zone_scale": 1.0,
    },
}

stream_reader = NYCDOTStreamReader(image_url=YORK_AVE_URL, poll_interval=POLL_INTERVAL)

financial_engine = ParkingFinancialEngine(
    hourly_rate=HOURLY_RATE,
    operating_hours_per_day=OPERATING_HOURS_PER_DAY,
    total_capacity=TOTAL_CAPACITY,
    window_size=WINDOW_SIZE,
)

vision_core: ParkingVisionCore | None = None


def get_vision_core() -> ParkingVisionCore:
    global vision_core
    if vision_core is None:
        cfg = global_state["config"]
        vision_core = ParkingVisionCore(
            zone_filepath=ZONE_FILEPATH,
            model_id=cfg["model_id"],
            confidence=cfg["confidence_threshold"],
            trigger_anchor=cfg["trigger_anchor"],
        )
    return vision_core


# --------------------------------------------------------------------------------------------------
# Background Vision Loop
# --------------------------------------------------------------------------------------------------
async def execute_inference_step(force_fetch: bool = False):
    """Executes a single fetch and inference step, updating global state."""
    try:
        frame = await stream_reader.get_latest_frame_async(force=force_fetch)
        if frame is not None:
            core = get_vision_core()
            annotated_frame, occupied_count, total_detected, details = await asyncio.to_thread(
                core.process_frame, frame
            )
            cfg = global_state["config"]
            telemetry = financial_engine.calculate_telemetry(
                raw_occupied_count=occupied_count,
                hourly_rate=cfg["hourly_rate"],
                operating_hours_per_day=cfg["operating_hours_per_day"],
                total_capacity=cfg["total_capacity"],
            )

            global_state["annotated_frame"] = annotated_frame
            global_state["telemetry"] = telemetry
            global_state["raw_occupied_count"] = occupied_count
            global_state["total_detected_count"] = total_detected
            global_state["detections_detail"] = details
            global_state["last_updated"] = time.time()
    except Exception as exc:
        print(f"[Warning] Error in background inference step: {exc}")


async def vision_pipeline_loop():
    print("[System] Background AI Inference loop started...\n")
    while True:
        is_streaming = global_state["active_streams_count"] > 0
        force = global_state.pop("force_refresh_requested", False)

        await execute_inference_step(force_fetch=force)

        # 2 FPS when client is viewing stream, 15s when idle
        sleep_interval = 0.5 if is_streaming else 15.0
        await asyncio.sleep(sleep_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting...\n")
    asyncio.create_task(vision_pipeline_loop())
    yield
    print("App is shutting down...\n")


# --------------------------------------------------------------------------------------------------
# FastAPI Application & Endpoints
# --------------------------------------------------------------------------------------------------
app = FastAPI(
    title="NYCDOT Parking Smart Analytics API",
    description="Real-time municipal parking telemetry and computer vision inference API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigUpdate(BaseModel):
    model_id: str | None = None
    confidence_threshold: float | None = Field(None, ge=0.01, le=1.0)
    trigger_anchor: str | None = None
    hourly_rate: float | None = Field(None, ge=0.0)
    operating_hours_per_day: float | None = Field(None, ge=0.0, le=24.0)
    total_capacity: int | None = Field(None, ge=1)
    zone_offset_x: int | None = None
    zone_offset_y: int | None = None
    zone_scale: float | None = Field(None, ge=0.1, le=3.0)
    reset_zone: bool | None = False


@app.get("/")
def root():
    return {
        "message": "NYC Parking Smart Analytics API is running.",
        "routes": [
            "/api/v1/analytics",
            "/api/v1/config",
            "/api/v1/refresh",
            "/api/v1/frame",
            "/api/v1/stream",
        ],
    }


@app.get("/api/v1/config")
def get_config():
    """Returns the current active system configuration and zone coordinates."""
    cfg = global_state["config"].copy()
    if vision_core is not None:
        cfg["current_zone"] = vision_core.get_current_zone()
    return cfg


@app.post("/api/v1/config")
def update_config(update: ConfigUpdate):
    """Updates runtime configuration (model, confidence, zone offsets, financial rates)."""
    cfg = global_state["config"]
    core = get_vision_core()

    if update.confidence_threshold is not None:
        cfg["confidence_threshold"] = update.confidence_threshold
        core.update_confidence(update.confidence_threshold)

    if update.model_id is not None and update.model_id != cfg["model_id"]:
        cfg["model_id"] = update.model_id
        core.update_model(update.model_id)

    if update.trigger_anchor is not None:
        cfg["trigger_anchor"] = update.trigger_anchor
        core.update_trigger_anchor(update.trigger_anchor)

    if update.reset_zone:
        cfg["zone_offset_x"] = 0
        cfg["zone_offset_y"] = 0
        cfg["zone_scale"] = 1.0
        core.reset_zone()
    elif (
        update.zone_offset_x is not None
        or update.zone_offset_y is not None
        or update.zone_scale is not None
    ):
        dx = update.zone_offset_x if update.zone_offset_x is not None else cfg["zone_offset_x"]
        dy = update.zone_offset_y if update.zone_offset_y is not None else cfg["zone_offset_y"]
        scale = update.zone_scale if update.zone_scale is not None else cfg["zone_scale"]
        cfg["zone_offset_x"] = dx
        cfg["zone_offset_y"] = dy
        cfg["zone_scale"] = scale
        core.set_zone_offset(dx=dx, dy=dy, scale=scale)

    if update.hourly_rate is not None:
        cfg["hourly_rate"] = update.hourly_rate
    if update.operating_hours_per_day is not None:
        cfg["operating_hours_per_day"] = update.operating_hours_per_day
    if update.total_capacity is not None:
        cfg["total_capacity"] = update.total_capacity

    return {"status": "success", "config": cfg}


@app.post("/api/v1/refresh")
async def force_refresh():
    """Forces an immediate fresh snapshot fetch from NYCDOT and runs inference."""
    await execute_inference_step(force_fetch=True)
    return {
        "status": "success",
        "message": "Forced snapshot fetch and inference complete.",
        "telemetry": global_state["telemetry"],
    }


@app.get("/api/v1/analytics")
def get_analytics(
    hourly_rate: float | None = None,
    operating_hours_per_day: float | None = None,
    total_capacity: int | None = None,
):
    """
    Returns real-time financial telemetry, detection counts, and full diagnostic details.
    """
    base_telemetry = global_state.get("telemetry", {})
    if not base_telemetry:
        return {}

    cfg = global_state["config"]
    rate = hourly_rate if hourly_rate is not None else cfg["hourly_rate"]
    hours = operating_hours_per_day if operating_hours_per_day is not None else cfg["operating_hours_per_day"]
    capacity = total_capacity if total_capacity is not None else cfg["total_capacity"]

    count = base_telemetry.get("smoothed_occupied_count", 0)
    fin = financial_engine.compute_telemetry(
        count=count,
        hourly_rate=rate,
        operating_hours_per_day=hours,
        total_capacity=capacity,
    )

    response_payload = {
        **fin,
        "raw_occupied_count": global_state.get("raw_occupied_count", 0),
        "total_detected_count": global_state.get("total_detected_count", 0),
        "detections_detail": global_state.get("detections_detail", []),
        "last_updated": global_state.get("last_updated", 0.0),
        "config": cfg,
    }
    if vision_core is not None:
        response_payload["zone_points"] = vision_core.get_current_zone()

    return response_payload


async def frame_generator():
    """Generates a continuous multipart MJPEG stream."""
    global_state["active_streams_count"] += 1
    print(f"[System] Stream client connected. Active streams: {global_state['active_streams_count']}")
    try:
        while True:
            frame = global_state["annotated_frame"]
            if frame is not None:
                success, encoded_image = cv2.imencode(".jpg", frame)
                if success:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + encoded_image.tobytes() + b"\r\n"
                    )
            await asyncio.sleep(0.1)
    finally:
        global_state["active_streams_count"] -= 1
        print(f"[System] Stream client disconnected. Active streams: {global_state['active_streams_count']}")


@app.get("/api/v1/stream")
def get_video_stream():
    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/api/v1/frame")
def get_latest_frame_image():
    frame = global_state["annotated_frame"]
    if frame is None:
        raise HTTPException(status_code=404, detail="No frame processed yet.")

    success, encoded_image = cv2.imencode(".jpg", frame)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image.")

    return Response(content=encoded_image.tobytes(), media_type="image/jpeg")


# --------------------------------------------------------------------------------------------------
# Static Frontend Serving (For Single-Container Production Deployments)
# --------------------------------------------------------------------------------------------------
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)


