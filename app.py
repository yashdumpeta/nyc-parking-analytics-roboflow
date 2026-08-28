import time
import requests
import streamlit as st

# Configure page layout and title
st.set_page_config(
    page_title="NYC Curb Utilization & Opportunity Cost Engine",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Base URL & Endpoints
API_BASE_URL = "http://127.0.0.1:8000"
ANALYTICS_ENDPOINT = f"{API_BASE_URL}/api/v1/analytics"
CONFIG_ENDPOINT = f"{API_BASE_URL}/api/v1/config"
REFRESH_ENDPOINT = f"{API_BASE_URL}/api/v1/refresh"
STREAM_ENDPOINT = f"{API_BASE_URL}/api/v1/stream"


def sync_config_to_backend(payload: dict):
    """Sends updated configuration to the FastAPI backend."""
    try:
        requests.post(CONFIG_ENDPOINT, json=payload, timeout=2.0)
    except requests.RequestException:
        pass


# --------------------------------------------------------------------------------------------------
# Sidebar: Interactive Calibration & Model Settings
# --------------------------------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Detection & Rate Controls")
    st.markdown("Fine-tune model sensitivity, zone calibration, and municipal revenue metrics.")

    # Section 1: AI Model & Sensitivity
    with st.container(border=True):
        st.subheader("🎯 AI Model & Sensitivity")

        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.05,
            max_value=0.90,
            value=0.25,
            step=0.05,
            help="Lower this if cars are visible but not being detected (e.g. 0.15 for low-light/distant cars).",
        )

        model_id = st.selectbox(
            "Inference Model",
            options=["yolov8m-640", "yolov8s-640", "yolov8n-640", "curbside-parking-mpa/1"],
            index=0,
            help="Select the YOLOv8 or custom fine-tuned Roboflow model for vehicle detection.",
        )

        trigger_anchor = st.selectbox(
            "Vehicle Anchor Point",
            options=["BOTTOM_CENTER", "CENTER", "BOTTOM_LEFT", "BOTTOM_RIGHT", "TOP_CENTER"],
            index=0,
            help="The point on the vehicle's bounding box that must fall inside the green polygon to be counted.",
        )

    # Section 2: Polygon Zone Calibration
    with st.container(border=True):
        st.subheader("📐 Zone Alignment & Tuning")
        st.caption("Adjust the curb polygon if vehicles are detected just outside the zone boundaries.")

        col_z1, col_z2 = st.columns(2)
        with col_z1:
            zone_offset_x = st.slider("Shift X", min_value=-80, max_value=80, value=0, step=2)
        with col_z2:
            zone_offset_y = st.slider("Shift Y", min_value=-80, max_value=80, value=0, step=2)

        zone_scale = st.slider("Zone Scale / Padding", min_value=0.6, max_value=1.8, value=1.0, step=0.05)

        if st.button("Reset Zone to Default", icon=":material/restart_alt:", use_container_width=True):
            sync_config_to_backend({"reset_zone": True})
            st.rerun()

    # Section 3: Financial Parameters
    with st.container(border=True):
        st.subheader("💰 Municipal Rate Simulation")

        hourly_rate = st.slider(
            "Hourly Meter Rate ($)",
            min_value=1.00,
            max_value=20.00,
            value=5.00,
            step=0.50,
            format="$%.2f",
            help="Manhattan Zone M2 parking meter rate",
        )

        total_capacity = st.slider(
            "Curb Capacity (Vehicles)",
            min_value=1,
            max_value=20,
            value=7,
            step=1,
            help="Maximum designated parking spaces along the block",
        )

        operating_hours = st.slider(
            "Operating Hours / Day",
            min_value=1.0,
            max_value=24.0,
            value=12.5,
            step=0.5,
            help="Metered enforcement hours per day (NYC standard: 8:00 AM - 8:30 PM = 12.5 hrs)",
        )

    # Sync any slider changes to FastAPI backend
    sync_config_to_backend({
        "confidence_threshold": confidence_threshold,
        "model_id": model_id,
        "trigger_anchor": trigger_anchor,
        "zone_offset_x": zone_offset_x,
        "zone_offset_y": zone_offset_y,
        "zone_scale": zone_scale,
        "hourly_rate": hourly_rate,
        "total_capacity": total_capacity,
        "operating_hours_per_day": operating_hours,
    })

    st.divider()
    st.caption(f"Connected Backend: `{API_BASE_URL}`")


# --------------------------------------------------------------------------------------------------
# Main Header Bar
# --------------------------------------------------------------------------------------------------
header_col1, header_col2 = st.columns([3, 1], vertical_alignment="center")

with header_col1:
    st.title("🏙️ NYC Curb Utilization & Opportunity Cost Engine")
    st.caption("AI-driven municipal parking telemetry & real-time revenue loss monitoring — West Curb, York Ave (72nd & 73rd St)")

with header_col2:
    if st.button("🔄 Force Snapshot Refresh", icon=":material/refresh:", use_container_width=True):
        try:
            requests.post(REFRESH_ENDPOINT, timeout=3.0)
            st.toast("Fresh snapshot fetched from NYCDOT!", icon="📸")
        except requests.RequestException:
            st.error("Failed to connect to backend.")


# --------------------------------------------------------------------------------------------------
# Main Dashboard Layout
# --------------------------------------------------------------------------------------------------
col_video, col_metrics = st.columns([3, 2], gap="large")

# Column 1: Live Video Feed & Diagnostic Detection Inspector
with col_video:
    with st.container(border=True):
        st.subheader("📹 Live Camera Feed & Detection Overlay")
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; background-color: #0e1117; border-radius: 8px; overflow: hidden; padding: 4px;">
                <img src="{STREAM_ENDPOINT}" 
                     style="width: 100%; border-radius: 6px; object-fit: contain;" 
                     alt="NYC DOT Live Camera Stream" />
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("🟢 **Green dot**: Vehicle anchor inside curb zone (Counted) | 🟠 **Orange dot**: Vehicle anchor outside curb zone")


# Column 2: Live Analytics Fragment (polling every 1s)
with col_metrics:
    @st.fragment(run_every=1)
    def render_analytics_panel():
        with st.container(border=True):
            st.subheader("📊 Real-Time Financial Telemetry")

            try:
                params = {
                    "hourly_rate": hourly_rate,
                    "total_capacity": total_capacity,
                    "operating_hours_per_day": operating_hours,
                }
                response = requests.get(ANALYTICS_ENDPOINT, params=params, timeout=1.5)
                if response.status_code == 200:
                    data = response.json()

                    if not data:
                        st.warning("Backend processing active. Awaiting first frame inference...")
                        return

                    occ_percentage = data.get("occupancy_percentage", 0.0)
                    smoothed_count = data.get("smoothed_occupied_count", 0)
                    raw_count = data.get("raw_occupied_count", 0)
                    total_detected = data.get("total_detected_count", 0)
                    hourly_cost = data.get("hourly_opportunity_cost", 0.0)
                    daily_cost = data.get("daily_opportunity_cost", 0.0)
                    annual_cost = data.get("annual_opportunity_cost", 0.0)
                    detections_detail = data.get("detections_detail", [])

                    # Connection status indicator
                    st.success(f"Live Stream Active • Model: `{model_id}` (Conf: {confidence_threshold:.2f})", icon="🟢")

                    # Primary Metrics Grid
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        st.metric(
                            label="Curb Occupancy Rate",
                            value=f"{occ_percentage:.1f}%",
                            delta=f"{smoothed_count}/{total_capacity} Spots Occupied",
                            border=True,
                        )
                    with sub_col2:
                        st.metric(
                            label="Hourly Revenue Loss",
                            value=f"${hourly_cost:.2f}",
                            delta=f"Rate: ${hourly_rate:.2f}/hr",
                            border=True,
                        )

                    # Opportunity Costs Breakdown
                    with st.container(border=True):
                        st.markdown("**💰 Unrealized Municipal Revenue (Opportunity Cost)**")
                        st.write(f"- **Daily Revenue Loss ({operating_hours:.1f} hrs/day):** `${daily_cost:,.2f}`")
                        st.write(f"- **Annual Revenue Loss (312 meter days):** `${annual_cost:,.2f}`")
                        st.progress(min(1.0, smoothed_count / max(1, total_capacity)))

                    # Policy Context Note
                    with st.expander("ℹ️ About Manhattan Zone M2 Opportunity Cost", expanded=False):
                        st.markdown(
                            """
                            **Policy Context**:
                            - The West Curb of York Ave (72nd–73rd St) currently provides **free, unmetered parking**.
                            - Adjacent commercial and residential avenues charge **Zone M2 meter rates ($5.00/hr)**.
                            - This telemetry calculates the **direct opportunity cost** to the NYC Department of Transportation by leaving high-demand curb space unpriced.
                            """
                        )

                else:
                    st.error(f"API Error ({response.status_code}): Unable to fetch analytics telemetry.")
            except requests.RequestException:
                st.warning(f"⚠️ Waiting for FastAPI backend at `{API_BASE_URL}`...")

    render_analytics_panel()
