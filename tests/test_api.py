import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock vision_core so API route tests remain lightweight and hermetic
mock_vc = MagicMock()
sys.modules["vision_core"] = mock_vc

from fastapi.testclient import TestClient
from api import app, global_state


async def _noop_loop():
    return


@pytest.fixture
def client():
    # Provide TestClient without starting background loops
    with patch("api.vision_pipeline_loop", side_effect=_noop_loop):
        with TestClient(app, raise_server_exceptions=True) as test_client:
            yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "routes" in data
    assert "/api/v1/analytics" in data["routes"]
    assert "/api/v1/stream" in data["routes"]


def test_analytics_endpoint_empty_and_populated(client):
    # When no frame processed yet
    global_state["telemetry"] = {}
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    assert response.json() == {}

    # Seed mock telemetry
    global_state["telemetry"] = {
        "smoothed_occupied_count": 4,
        "occupancy_percentage": 57.14,
        "hourly_opportunity_cost": 20.00,
        "daily_opportunity_cost": 250.00,
        "annual_opportunity_cost": 78000.00,
        "hourly_rate": 5.00,
        "total_capacity": 7,
        "operating_hours_per_day": 12.5,
    }

    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["smoothed_occupied_count"] == 4
    assert data["hourly_opportunity_cost"] == 20.00

    # Test dynamic query parameters override
    response_custom = client.get("/api/v1/analytics?hourly_rate=10.0&total_capacity=5")
    assert response_custom.status_code == 200
    custom_data = response_custom.json()
    assert custom_data["smoothed_occupied_count"] == 4
    # 4 * $10.00 = $40.00
    assert custom_data["hourly_opportunity_cost"] == 40.00
    assert custom_data["total_capacity"] == 5
    assert custom_data["occupancy_percentage"] == 80.0
