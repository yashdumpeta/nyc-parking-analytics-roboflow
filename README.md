# 🏙️ NYC Curb Utilization & Opportunity Cost Engine (v1.0)
> **AI-Driven Municipal Revenue & Parking Telemetry on York Ave (React + FastAPI + Roboflow)**

---

## 📌 Executive Summary
Urban curb space is one of the most valuable yet unoptimized municipal assets. On the **West Curb of York Avenue (between 72nd & 73rd St, Manhattan)**, parking is free and unrestricted outside of street sweeping. The city collects **$0** in parking revenue from this high-demand block, while adjacent curbs operate on paid meters.

This project implements an end-to-end Computer Vision (CV) pipeline that ingests live CCTV snapshots from the **NYC Department of Transportation (NYCDOT)**, detects vehicle occupancy across defined curb zones using Roboflow Inference, and computes real-time **unrealized municipal revenue (opportunity cost)** based on **Manhattan Zone M2 parking meter rates ($5.00/hr)**.

---

## 🖥️ Live Telemetry Dashboard Preview

<!-- Demo Showcase Placeholder: Add demo GIF/video here -->
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🏙️ NYC Curb Telemetry & Revenue Engine                 🟢 NYCDOT LIVE  [Force Snapshot]     │
├──────────────────────────────────────────────────────────┬──────────────────────────────────┤
│ 📹 NYC DOT CCTV Feed | York Ave & 72nd St  [yolov8m-640] │ ⚙️ AI Detection Tuning           │
│ 🟢 ACTIVE • 🟢 In Zone • 🟠 Out Zone • Occupancy: 4/7    │   Confidence Threshold: 25%      │
│ ┌──────────────────────────────────────────────────────┐ │   Model: yolov8m-640             │
│ │ [ Live Camera Stream with Polygon Overlay & BBoxes ] │ │   Anchor: BOTTOM_CENTER          │
│ └──────────────────────────────────────────────────────┘ │ 📐 Zone Alignment (Shift X/Y)    │
│ ┌──────────────────────────┬───────────────────────────┐ │ 💰 Municipal Rate Simulation     │
│ │ Curb Occupancy: 57.1%    │ Hourly Loss: $20.00 / hr  │ │   Meter Rate: $5.00 / hr         │
│ │ Daily Loss: $250.00      │ Annual Loss: $78,000.00   │ │   Capacity: 7 spots              │
│ └──────────────────────────┴───────────────────────────┘ └──────────────────────────────────┘
```

---

## 🛠️ Core Components

| Component | File / Directory | Description |
| :--- | :--- | :--- |
| **Modern React Dashboard** | [`frontend/`](frontend/) | High-aesthetic dark obsidian telemetry dashboard (Vite + React 19 + TypeScript + Tailwind CSS + Lucide Icons) with live video player, HUD overlays, real-time metric cards, and 60 FPS tuning controls. |
| **FastAPI Backend & Streamer** | [`api.py`](api.py) | High-performance asynchronous FastAPI server providing real-time telemetry JSON, dynamic parameter tuning (`/api/v1/config`), force snapshot refresh (`/api/v1/refresh`), and continuous MJPEG live streaming (`/api/v1/stream`). |
| **Vision Core Pipeline** | [`vision_core.py`](vision_core.py) | Roboflow Inference SDK (`yolov8m-640` / `curbside-parking-mpa/1`) + `supervision` pipeline for strict vehicle detection (filtering out pedestrians/cyclists), bottom-center zone triggering, visual anchor dots, and runtime zone alignment. |
| **Financial Engine** | [`financial_engine.py`](financial_engine.py) | Temporal sliding-window filter for occlusion smoothing, computing hourly, daily (12.5 hrs), and annual (312 meter days) unrealized revenue. |
| **NYC DOT Stream Reader** | [`nycdot_stream.py`](nycdot_stream.py) | Handles fetching live snapshots from the NYC DOT camera feed with caching (`poll_interval`) via sync and async HTTP clients. |
| **Interactive Zone Drawer** | [`zone_drawer.py`](zone_drawer.py) | OpenCV GUI calibration tool to establish custom parking zones on live frames, auto-sorting polygon points to `zones.json`. |
| **Unified Runner** | [`run.py`](run.py) / [`run.sh`](run.sh) | Single-command launcher that orchestrates backend health checks, launches the React frontend, and opens the browser. |

---

## 🔌 API Endpoints

* **`GET /`** — Health check, API status, and registered routes.
* **`GET /api/v1/analytics`** — Real-time financial telemetry JSON (`smoothed_occupied_count`, `occupancy_percentage`, opportunity costs, detection breakdown).
* **`GET /api/v1/config` & `POST /api/v1/config`** — Get or dynamically update model ID, confidence threshold, trigger anchor, zone offsets, and meter rates on the fly.
* **`POST /api/v1/refresh`** — Forces an immediate fresh camera snapshot fetch from NYCDOT and re-runs inference.
* **`GET /api/v1/stream`** — Serves a continuous live, annotated MJPEG video stream with visual anchor indicators.
* **`GET /api/v1/frame`** — Returns the single most recent annotated JPEG frame.

---

## 🚀 Getting Started

### 1. Environment & Dependency Installation

#### Backend (Python 3.10+)
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required Python packages
pip install -r requirements.txt
```

#### Frontend (Node.js 18+)
```bash
cd frontend
npm install
cd ..
```

---

### 2. Roboflow API Key Configuration (Optional)

Public models (e.g. `yolov8n-640` or `yolov8m-640`) run out-of-the-box without requiring an API key. If you intend to use custom fine-tuned Roboflow models (such as `curbside-parking-mpa/1`), create a `.env` or `.env.local` file in the project root:

```env
ROBOFLOW_API_KEY=your_roboflow_api_key_here
MODEL_ID=yolov8m-640
```

---

### 3. Run the Entire Fullstack Platform

#### Option A: Unified Single-Command Launch (Recommended)
Launch both the FastAPI backend and Modern React Dashboard simultaneously:

```bash
# Using Python
python run.py

# Or using the shell wrapper
./run.sh
```

This starts the FastAPI backend, verifies the health check, boots the Vite React frontend, and automatically opens your browser at **`http://localhost:5173`**. Pressing `Ctrl+C` cleanly shuts down all processes.

#### Option B: Manual Multi-Terminal Launch

**Terminal 1: FastAPI Backend**
```bash
source .venv/bin/activate
uvicorn api:app --reload --port 8000
```

**Terminal 2: React Frontend**
```bash
cd frontend
npm run dev
```

---

### 4. Running the Automated Test Suite

Execute the hermetic unit and integration test suite:

```bash
pytest -v
```

---

## 📜 License
Distributed under the [MIT License](LICENSE).
