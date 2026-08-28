from collections import deque

class TemporalOccupancyFilter:
    
    
    def __init__(self, window_size: int = 20):
        # Using deque for size management + time complexity
        self.buffer = deque(maxlen=window_size)
        print(f"[Success] Initialized TemporalOccupancyFilter with window size {window_size}.\n")
    
    def update(self, raw_count: int) -> int:
        # Append the new raw count to the buffer and compute the smoothed count
        self.buffer.append(raw_count)
        smoothed_count = max(self.buffer)
        
        return smoothed_count

class ParkingFinancialEngine:
    def __init__(self, hourly_rate: float, operating_hours_per_day: float, total_capacity: int = 7, window_size: int = 20):
        self.total_capacity = total_capacity
        self.hourly_rate = hourly_rate
        self.operating_hours_per_day = operating_hours_per_day
        self.temporal_filter = TemporalOccupancyFilter(window_size=window_size)
        print(f"[Success] Initialized ParkingFinancialEngine with total capacity {total_capacity}, hourly rate {hourly_rate}, and operating {operating_hours_per_day} hours per day .\n")
        
    def compute_telemetry(
        self,
        count: int,
        hourly_rate: float | None = None,
        operating_hours_per_day: float | None = None,
        total_capacity: int | None = None,
    ) -> dict:
        """
        Computes financial telemetry from a known count without advancing the filter buffer.
        """
        rate = hourly_rate if hourly_rate is not None else self.hourly_rate
        hours = operating_hours_per_day if operating_hours_per_day is not None else self.operating_hours_per_day
        capacity = total_capacity if total_capacity is not None else self.total_capacity

        effective_count = min(count, capacity)
        occupancy_percentage = (effective_count / capacity * 100) if capacity > 0 else 0.0
        hourly_opportunity_cost = effective_count * rate
        daily_opportunity_cost = hourly_opportunity_cost * hours
        # 312 operating days/year based on 6 paid meter days/week * 52 weeks (Sundays free in NYC)
        annual_opportunity_cost = daily_opportunity_cost * 312

        return {
            "smoothed_occupied_count": effective_count,
            "occupancy_percentage": round(occupancy_percentage, 2),
            "hourly_opportunity_cost": round(hourly_opportunity_cost, 2),
            "daily_opportunity_cost": round(daily_opportunity_cost, 2),
            "annual_opportunity_cost": round(annual_opportunity_cost, 2),
            "hourly_rate": round(rate, 2),
            "total_capacity": capacity,
            "operating_hours_per_day": hours,
        }

    def calculate_telemetry(
        self,
        raw_occupied_count: int,
        hourly_rate: float | None = None,
        operating_hours_per_day: float | None = None,
        total_capacity: int | None = None,
    ) -> dict:
        # get the smoothed count of occupied spaces based on the sliding window of recent counts
        smoothed_occupied_count = self.temporal_filter.update(raw_occupied_count)
        return self.compute_telemetry(
            count=smoothed_occupied_count,
            hourly_rate=hourly_rate,
            operating_hours_per_day=operating_hours_per_day,
            total_capacity=total_capacity,
        )
        

if __name__ == "__main__":
    financial_engine = ParkingFinancialEngine(
        hourly_rate=5.00,
        operating_hours_per_day=12.5,
        total_capacity=7,
        window_size=20
    )
    
    # Simulate a noisy sequence where occlusion causes transient drops (5 -> 2 -> 1)
    simulated_raw_counts = [0, 2, 5, 5, 5, 2, 1, 5, 5, 6]
    
    print("\n--- SIMULATION TEST ---")
    for raw in simulated_raw_counts:
        telemetry = financial_engine.calculate_telemetry(raw)
        print(f"Raw Count: {raw} | Smoothed: {telemetry['smoothed_occupied_count']} | Occupancy: {telemetry['occupancy_percentage']}% | Daily Revenue: ${telemetry['daily_opportunity_cost']}")
    
        