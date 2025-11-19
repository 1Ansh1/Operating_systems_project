import pandas as pd

class MetricsCollector:
    
    def __init__(self):
        self.hits = 0
        self.faults = 0
        self.total_requests = 0
        

        self.timeline = []

    def record_hit(self, step, page, frames):
        self.hits += 1
        self.total_requests += 1
        self.timeline.append((step, page, False, list(frames)))

    def record_fault(self, step, page, frames):
        self.faults += 1
        self.total_requests += 1
        self.timeline.append((step, page, True, list(frames)))

    def get_stats(self):
        
        hit_ratio = (self.hits / self.total_requests) if self.total_requests > 0 else 0
        miss_ratio = (self.faults / self.total_requests) if self.total_requests > 0 else 0
        
        return {
            "Total Requests": self.total_requests,
            "Page Faults": self.faults,
            "Page Hits": self.hits,
            "Hit Ratio": hit_ratio,
            "Miss Ratio": miss_ratio
        }

    def get_timeline_dataframe(self):

        return pd.DataFrame(
            self.timeline,
            columns=["Step", "Page", "Is Fault", "Frames State"]
        )