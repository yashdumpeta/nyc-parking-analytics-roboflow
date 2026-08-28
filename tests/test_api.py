import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock vision_core so API route tests remain lightweight and hermetic
mock_vc = MagicMock()
mock_vc.get_current_zone.return_value = [[310, 61], [329, 65], [86, 152], [61, 137]]
sys.modules["vision_core"] = mock_vc

from fastapi.testclient import TestClient
from api import app, global_state


async def _noop_loop():
    return


@pytest.fixture
def client():
    with patch("api.vision_pipeline_loop", side_effect=_noop_loop):
        with patch("api.get_vision_core", return_value=mock_vc):
            with TestClient(app, raise_server_exceptions=True) as test_client:
                yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "routes" in data
    assert "/api/v1/analytics" in data["routes"]
    assert "/api/v1/config" in data["routes"]
    assert "/api/v1/refresh" in data["routes"]
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
    global_state["raw_occupied_count"] = 4
    global_state["total_detected_count"] = 5
    global_state["detections_detail"] = [
        {"class_name": "car", "confidence": 0.85, "box": [10, 20, 50, 60], "anchor": [30, 60], "in_zone": True}
    ]

    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["smoothed_occupied_count"] == 4
    assert data["total_detected_count"] == 5
    assert len(data["detections_detail"]) == 1

    # Test dynamic query parameters override
    response_custom = client.get("/api/v1/analytics?hourly_rate=10.0&total_capacity=5")
    assert response_custom.status_code == 200
    custom_data = response_custom.json()
    assert custom_data["smoothed_occupied_count"] == 4
    assert custom_data["hourly_opportunity_cost"] == 40.00
    assert custom_data["total_capacity"] == 5
    assert custom_data["occupancy_percentage"] == 80.0


def test_config_endpoints(client):
    # Test GET config
    res_get = client.get("/api/v1/config")
    assert res_get.status_code == 200
    config_data = res_get.json()
    assert "model_id" in config_data
    assert "confidence_threshold" in config_data

    # Test POST config update
    update_payload = {
        "confidence_threshold": 0.15,
        "hourly_rate": 7.50,
        "total_capacity": 10,
        "zone_offset_x": 10,
        "zone_offset_y": -5,
        "zone_scale": 1.1,
    }
    res_post = client.post("/api/v1/config", json=update_payload)
    assert res_post.status_code == 200
    updated_cfg = res_post.json()["config"]
    assert updated_cfg["confidence_threshold"] == 0.15
    assert updated_cfg["hourly_rate"] == 7.50
    assert updated_cfg["total_capacity"] == 10
    assert updated_cfg["zone_offset_x"] == 10


def test_refresh_endpoint(client):
    with patch("api.execute_inference_step") as mock_exec:
        res = client.post("/api/v1/refresh")
        assert res.status_code == 200
        assert res.json()["status"] == "success"
