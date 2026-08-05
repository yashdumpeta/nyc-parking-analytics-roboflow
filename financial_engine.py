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


        
        