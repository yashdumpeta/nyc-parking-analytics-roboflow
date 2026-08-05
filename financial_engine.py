from collections import deque

class TemporalOccupancyFilter:
    
    # using deque due to DS efficiency and clean state management
    # Automatic Bounded Sizing w/ maxLen, so the deque automatically manages the sliding window in memory for us and has a fixed amount of size 
    # Time complexity of O(1) for append and pop operations, making it efficient for real-time applications.
    def __init__(self, window_size: int = 5):
        self.buffer = deque(maxlen=window_size)
        print(f"[Success] Initialized TemporalOccupancyFilter with window size {window_size}.\n")
    
    def update(self, raw_count: int) -> int:
        self.buffer.append(raw_count)
        smoothed_count = max(self.buffer)
        return smoothed_count

class ParkingFinancialEngine:
    def __init__(self, hourly_rate: float, operating_hours_per_day: float, total_capacity: int = 7, window_size: int = 5):
        self.total_capacity = total_capacity
        self.hourly_rate = hourly_rate
        self.operating_hours_per_day = operating_hours_per_day
        self.temporal_filter = TemporalOccupancyFilter(window_size=window_size)
        print(f"[Success] Initialized ParkingFinancialEngine with total capacity {total_capacity}, hourly rate {hourly_rate}, and operating hours per day {operating_hours_per_day}.\n")
        
    def calculate_telemetry(self, raw_occupied_count: int) -> dict:
        smoothed_occupied_count = self.temporal_filter.update(raw_occupied_count)
        occupancy_percentage = (smoothed_occupied_count / self.total_capacity) * 100
        estimated_daily_revenue = smoothed_occupied_count * self.hourly_rate * self.operating_hours_per_day
        
        telemetry_data = {
            "smoothed_occupied_count": smoothed_occupied_count,
            "occupancy_percentage": occupancy_percentage,
            "estimated_daily_revenue": estimated_daily_revenue
        }
        
        return telemetry_data
        
        
        