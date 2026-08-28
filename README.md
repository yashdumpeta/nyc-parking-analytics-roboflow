# 🏙️ NYC Curb Utilization & Opportunity Cost Engine (v1.0)
> **AI-Driven Municipal Revenue & Parking Telemetry on York Ave**

---

## 📌 Executive Summary
Urban curb space is one of the most valuable yet unoptimized municipal assets. On the **West Curb of York Avenue (between 72nd & 73rd St, Manhattan)**, parking is free and unrestricted outside of street sweeping. The city collects **$0** in parking revenue from this high-demand block, while adjacent curbs operate on paid meters.

This project implements an end-to-end Computer Vision (CV) pipeline that ingests live CCTV snapshots from the **NYC Department of Transportation (NYCDOT)**, detects vehicle occupancy across defined curb zones using Roboflow Inference, and computes real-time **unrealized municipal revenue (opportunity cost)** based on **Manhattan Zone M2 parking meter rates ($5.00/hr)**.

---

## 🛠️ Core Components

| Component | File | Description |
| :--- | :--- | :--- |
| **NYC DOT Stream Reader** | [`nycdot_stream.py`](nycdot_stream.py) | Handles fetching live snapshots from the NYC DOT camera feed with caching (`poll_interval`) via sync and async HTTP clients. |
| **Interactive Zone Drawer** | [`zone_drawer.py`](zone_drawer.py) | Interactive OpenCV GUI tool to draw custom parking zones on live frames, auto-sorting polygon points to `zones.json`. |
| **Vision Core Pipeline** | [`vision_core.py`](vision_core.py) | Roboflow Inference SDK (`curbside-parking-mpa/1` or `yolov8m-640`) + `supervision` pipeline for vehicle detection, bottom-center zone triggering, and MPS hardware patching. |
| **Financial Engine** | [`financial_engine.py`](financial_engine.py) | Temporal sliding-window max filter (`TemporalOccupancyFilter`) for occlusion smoothing, computing hourly, daily, and annual opportunity costs. |
| **FastAPI Web Backend** | [`api.py`](api.py) | Asynchronous FastAPI server running a non-blocking background inference loop, dynamically active when streaming clients are connected. |
| **Streamlit Web Dashboard** | [`app.py`](app.py) | Interactive presentation layer featuring live MJPEG video streaming, custom rate/capacity sliders, and auto-refreshing KPI metric cards. |

---

## 🔌 API Endpoints

* **`GET /`** — Health check, API status, and registered routes.
* **`GET /api/v1/analytics`** — Returns real-time financial telemetry JSON (`smoothed_occupied_count`, `occupancy_percentage`, opportunity costs).
* **`GET /api/v1/stream`** — Serves a continuous live, annotated MJPEG video stream of the curb.
* **`GET /api/v1/frame`** — Returns the single most recent annotated JPEG frame.

---

## 🚀 Getting Started

### 1. Environment & Dependency Installation

Create and activate a virtual environment, then install the required dependencies:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

> [!NOTE]
> **Installation Note**: Downloading and building dependencies from `requirements.txt` may take several minutes as it installs computer vision and deep learning packages including the Roboflow Inference SDK, PyTorch, Supervision, OpenCV, and ONNX Runtime.

---

### 2. Roboflow API Key Configuration

If you intend to use custom fine-tuned Roboflow models (such as `curbside-parking-mpa/1`), create a `.env` or `.env.local` file in the project root directory and add your Roboflow API key:

```env
ROBOFLOW_API_KEY=your_roboflow_api_key_here
```

*To obtain your API key, visit the [Roboflow Authentication Documentation](https://docs.roboflow.com/api-reference/authentication#retrieve-an-api-key).*

> [!TIP]
> Public models (e.g. `yolov8n-640` or `yolov8m-640`) run out-of-the-box without requiring a Roboflow API key.

---

### 3. Draw & Calibrate the Parking Zone

Run the interactive calibration tool to establish your detection polygon zone around the curb lane:

```bash
python zone_drawer.py
```

* **Controls**:
  * Left-click 4 corners along the West Curb parking lane.
  * `z` — Undo last point
  * `r` — Reset all points
  * `e` — Fetch new snapshot from NYCDOT stream
  * `c` — Confirm & save polygon coordinates to `zones.json`
  * `q` — Quit

---

### 4. Run the Application

#### Terminal 1: Launch FastAPI Backend
Start the backend web service using Uvicorn:
```bash
source .venv/bin/activate
uvicorn api:app --reload --port 8000
```

#### Terminal 2: Launch Streamlit Presentation Dashboard
In a second terminal window, start the Streamlit web dashboard:
```bash
source .venv/bin/activate
streamlit run app.py
```

By default, Streamlit will automatically open the interactive presentation dashboard in your browser at **`http://localhost:8501`** (if port 8501 is in use by another application, check your terminal output for the assigned port, e.g. `http://localhost:8502`).

---

### 5. Running the Automated Test Suite

Run the hermetic unit and API test suite:

```bash
pytest -v
```
