# 🏙️ NYC Curb Utilization & Opportunity Cost Engine
> **AI-Driven Municipal Revenue & Parking Telemetry on York Ave**

---

## 📌 Executive Summary
Urban curb space is one of the most valuable yet unoptimized municipal assets. On the **West Curb of York Avenue (between 72nd & 73rd St, Manhattan)**, parking is free and unrestricted outside of street sweeping. The city collects **$0** in parking revenue from this high-demand block, while adjacent curbs operate on paid meters.

This project implements an end-to-end Computer Vision (CV) pipeline that ingests live CCTV snapshots from the **NYC Department of Transportation (NYCDOT)**, detects vehicle occupancy across defined curb zones, and computes real-time **unrealized municipal revenue (opportunity cost)** based on **Manhattan Zone M2 parking meter rates ($5.00/hr)**.

---

## 🛠️ Core Components

| Component | File | Description |
| :--- | :--- | :--- |
| **NYC DOT Stream Reader** | [nycdot_stream.py](nycdot_stream.py) | Handles fetching the latest snapshot from the NYC DOT camera feed and provides a reusable frame source for the pipeline. |
| **Interactive Zone Drawer** | [zone_drawer.py](zone_drawer.py) | Interactive GUI using OpenCV to draw custom parking zones directly on live frames, saving coordinates to `zones.json`. |
| **Vision Core Pipeline** | [vision_core.py](vision_core.py) | Roboflow Inference SDK (YOLOv8m-640) and Supervision pipeline that processes webcams and filters for vehicle classes. |
| **Financial Engine** | [financial_engine.py](financial_engine.py) | Temporal filter (sliding window) to smooth vehicle counts and calculate hourly, daily, and annual opportunity costs. |
| **FastAPI Web Service** | [api.py](api.py) | Asynchronous FastAPI server that operates a non-blocking background inference loop, optimized to only fetch/process frames when clients are actively streaming. |

---

## 🔌 API Endpoints

* **`GET /`** — API status and available routes.
* **`GET /api/v1/analytics`** — Instantly returns cached financial telemetry.
* **`GET /api/v1/stream`** — Serves a live, annotated MJPEG video stream of the curb.
* **`GET /api/v1/frame`** — Returns the most recent annotated JPEG frame.

---

## 🚀 Getting Started

### 1. Setup Environment & Dependencies
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Draw the Parking Zone
Run the interactive tool to establish your detection zone. Left-click to create points around the parking lane, and press `c` to confirm and save.
```bash
python zone_drawer.py
```
*Keyboard controls:* `z` (Undo last point) \| `r` (Reset all points) \| `e` (Fetch new frame) \| `c` (Confirm & save) \| `q` (Quit)

### 3. Run the API Server
Start the web app locally using Uvicorn:
```bash
uvicorn api:app --reload
```
Navigate to `http://127.0.0.1:8000` to interact with the API endpoints.
