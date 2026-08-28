import pytest
from financial_engine import TemporalOccupancyFilter, ParkingFinancialEngine


def test_temporal_occupancy_filter_window():
    filt = TemporalOccupancyFilter(window_size=3)
    # Adding elements
    assert filt.update(2) == 2
    assert filt.update(5) == 5
    # Occlusion drop should be smoothed by window max
    assert filt.update(1) == 5
    # Window advances: [5, 1, 3] -> max is 5
    assert filt.update(3) == 5
    # Window advances: [1, 3, 2] -> 5 has rolled off, max is 3
    assert filt.update(2) == 3


def test_parking_financial_engine_defaults():
    engine = ParkingFinancialEngine(
        hourly_rate=5.00,
        operating_hours_per_day=12.5,
        total_capacity=7,
        window_size=5,
    )
    # Occupied count: 4
    telemetry = engine.calculate_telemetry(raw_occupied_count=4)
    
    assert telemetry["smoothed_occupied_count"] == 4
    # 4 / 7 * 100 = 57.14%
    assert telemetry["occupancy_percentage"] == 57.14
    # 4 * $5 = $20.00
    assert telemetry["hourly_opportunity_cost"] == 20.00
    # $20 * 12.5 = $250.00
    assert telemetry["daily_opportunity_cost"] == 250.00
    # $250 * 312 = $78,000.00
    assert telemetry["annual_opportunity_cost"] == 78000.00


def test_parking_financial_engine_capacity_clamping():
    engine = ParkingFinancialEngine(
        hourly_rate=5.00,
        operating_hours_per_day=10.0,
        total_capacity=5,
        window_size=5,
    )
    # When raw detector reports more vehicles than capacity
    telemetry = engine.calculate_telemetry(raw_occupied_count=10)
    assert telemetry["smoothed_occupied_count"] == 5
    assert telemetry["occupancy_percentage"] == 100.0
    assert telemetry["hourly_opportunity_cost"] == 25.00


def test_compute_telemetry_with_custom_overrides():
    engine = ParkingFinancialEngine(
        hourly_rate=5.00,
        operating_hours_per_day=12.5,
        total_capacity=7,
    )
    # Static compute with dynamic overrides without updating window
    telemetry = engine.compute_telemetry(
        count=3,
        hourly_rate=10.00,
        operating_hours_per_day=8.0,
        total_capacity=6,
    )
    assert telemetry["smoothed_occupied_count"] == 3
    assert telemetry["occupancy_percentage"] == 50.0
    assert telemetry["hourly_opportunity_cost"] == 30.00
    assert telemetry["daily_opportunity_cost"] == 240.00
    assert telemetry["annual_opportunity_cost"] == 240.00 * 312
