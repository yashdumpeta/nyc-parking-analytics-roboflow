import time
import requests
import streamlit as st

# Configure page layout and title
st.set_page_config(
    page_title="NYC Curb Utilization Engine",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Base URL
API_BASE_URL = "http://127.0.0.1:8000"
ANALYTICS_ENDPOINT = f"{API_BASE_URL}/api/v1/analytics"
STREAM_ENDPOINT = f"{API_BASE_URL}/api/v1/stream"

# App Header
st.title("🏙️ NYC Curb Utilization & Opportunity Cost Engine")
st.caption("AI-driven municipal parking telemetry & real-time revenue loss monitoring — West Curb, York Ave (72nd & 73rd St)")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️  Simulation Settings")
    st.markdown("Adjust parameters for curb capacity and rate metrics.")

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
        "Total Curb Capacity (Vehicles)",
        min_value=1,
        max_value=20,
        value=7,
        step=1,
        help="Maximum designated parking spaces along the block",
    )

    window_size = st.slider(
        "Temporal Filter Window Size",
        min_value=1,
        max_value=50,
        value=20,
        step=1,
        help="Sliding window size (frames) for occlusion smoothing",
    )

    st.divider()
    st.markdown("**API Status & Endpoint**")
    st.code(API_BASE_URL, language="text")

# Main Dashboard Layout: 2 Columns
col1, col2 = st.columns([3, 2], gap="medium")

# Column 1: Live Video Feed
with col1:
    with st.container(border=True):
        st.subheader("📹 Live Camera Feed (York Ave & 72nd St)")
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

# Column 2: Live Analytics Fragment (polling every 1s)
with col2:
    @st.fragment(run_every=1)
    def render_analytics():
        with st.container(border=True):
            st.subheader("📊 Real-Time Financial Telemetry")
            
            try:
                response = requests.get(ANALYTICS_ENDPOINT, timeout=1.5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if not data:
                        st.warning("Backend processing active. Awaiting first frame inference...")
                        return

                    occ_percentage = data.get("occupancy_percentage", 0.0)
                    smoothed_count = data.get("smoothed_occupied_count", 0)
                    hourly_cost = data.get("hourly_opportunity_cost", 0.0)
                    daily_cost = data.get("daily_opportunity_cost", 0.0)
                    annual_cost = data.get("annual_opportunity_cost", 0.0)

                    # Connection status indicator
                    st.success("API Connected • Polling every 1s", icon="🟢")

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
                            delta=f"Based on ${hourly_rate:.2f}/hr",
                            border=True,
                        )

                    # Opportunity Costs Card Container
                    with st.container(border=True):
                        st.markdown("**💰 Unrealized Municipal Revenue (Opportunity Cost)**")
                        st.write(f"- **Daily Revenue Loss (12.5 hrs):** `${daily_cost:,.2f}`")
                        st.write(f"- **Annual Revenue Loss (312 days):** `${annual_cost:,.2f}`")


                else:
                    st.error(f"API Error ({response.status_code}): Unable to fetch analytics telemetry.")
            except requests.RequestException:
                st.warning("⚠️ Waiting for FastAPI backend connection at `http://127.0.0.1:8000`...")

    render_analytics()
