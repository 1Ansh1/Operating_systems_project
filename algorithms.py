from abc import ABC, abstractmethod
from collections import deque

# --- Abstract Base Class for all Algorithms ---

class PageReplacementAlgorithm(ABC):
    """
    This is the abstract base class (like a blueprint) for all
    page replacement algorithms.
    """
    def __init__(self, num_frames):
        if num_frames <= 0:
            raise ValueError("Number of frames must be positive.")
        self.num_frames = num_frames
        self.frames = []  # This list will represent physical memory
        self.page_faults = 0
        self.page_hits = 0

    @abstractmethod
    def process_page_request(self, page_number, workload_future=None):
        """
        This is the main method that each algorithm must implement.
        It will process a single page request.
        It must (internally) handle hits and faults.
        """
        pass

    def get_stats(self):
        """
        Returns a dictionary of the final performance statistics.
        (This is the corrected version with raw numbers for plotting)
        """
        total_requests = self.page_hits + self.page_faults
        hit_ratio_raw = (self.page_hits / total_requests) if total_requests > 0 else 0
        miss_ratio_raw = (self.page_faults / total_requests) if total_requests > 0 else 0
        
        return {
            "Total Requests": total_requests,
            "Page Faults": self.page_faults,
            "Page Hits": self.page_hits,
            "Hit Ratio": f"{hit_ratio_raw:.2%}",      # Formatted string
            "Miss Ratio": f"{miss_ratio_raw:.2%}",     # Formatted string
            "Hit Ratio (raw)": hit_ratio_raw,         # Raw number
            "Miss Ratio (raw)": miss_ratio_raw        # Raw number
        }

# --- 1. FIFO (First-In, First-Out) Module ---

class FIFO(PageReplacementAlgorithm):
    def __init__(self, num_frames):
        super().__init__(num_frames)
        self.queue = deque() # Tracks arrival order

    def process_page_request(self, page_number, workload_future=None):
        # Check for a Page Hit
        if page_number in self.frames:
            self.page_hits += 1
            return

        # --- Process a Page Fault ---
        self.page_faults += 1
        
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
            self.queue.append(page_number)
        else:
            page_to_evict = self.queue.popleft()
            self.frames.remove(page_to_evict)
            self.frames.append(page_number)
            self.queue.append(page_number)

# --- 2. LRU (Least Recently Used) Module ---

class LRU(PageReplacementAlgorithm):
    def __init__(self, num_frames):
        super().__init__(num_frames)
        # self.frames list is used as the LRU stack

    def process_page_request(self, page_number, workload_future=None):
        # Check for a Page Hit
        if page_number in self.frames:
            self.page_hits += 1
            # A hit: move page to end (most recently used)
            self.frames.remove(page_number)
            self.frames.append(page_number)
            return

        # --- Process a Page Fault ---
        self.page_faults += 1
        
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
        else:
            # Evict LRU page (at front of list)
            self.frames.pop(0) 
            self.frames.append(page_number)

# --- 3. Optimal (OPT) Module ---

class Optimal(PageReplacementAlgorithm):
    def __init__(self, num_frames):
        super().__init__(num_frames)

    def process_page_request(self, page_number, workload_future):
        # Check for a Page Hit
        if page_number in self.frames:
            self.page_hits += 1
            return

        # --- Process a Page Fault ---
        self.page_faults += 1
        
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
        else:
            # Evict page used furthest in the future
            page_to_evict = self._find_furthest_used_page(workload_future)
            self.frames.remove(page_to_evict)
            self.frames.append(page_number)

    def _find_furthest_used_page(self, future_workload):
        next_use = {}
        for page in self.frames:
            try:
                future_index = future_workload.index(page)
                next_use[page] = future_index
            except ValueError:
                # Page is never used again, perfect to evict
                return page
        
        # Evict page with the largest future_index
        return max(next_use, key=next_use.get)

# --- 4. MGLRU (Multi-Generational LRU) Module ---

class MGLRU(PageReplacementAlgorithm):
    def __init__(self, num_frames, num_generations=4, aging_threshold=10):
        super().__init__(num_frames)
        self.num_generations = num_generations
        self.aging_threshold = aging_threshold
        
        self.generations = [deque() for _ in range(num_generations)]
        self.page_map = {} # Tracks {page -> gen_index}
        self.current_page_count = 0
        self.age_tick_counter = 0

    def _age_pages(self):
        for i in range(self.num_generations - 2, -1, -1):
            if self.generations[i]:
                page_to_age = self.generations[i].popleft()
                next_gen = i + 1
                self.generations[next_gen].append(page_to_age)
                self.page_map[page_to_age] = next_gen
                return

    def process_page_request(self, page_number, workload_future=None):
        self.age_tick_counter += 1
        if self.age_tick_counter >= self.aging_threshold:
            self._age_pages()
            self.age_tick_counter = 0
            
        if page_number in self.page_map:
            self.page_hits += 1
            current_gen = self.page_map[page_number]
            if current_gen != 0:
                self.generations[current_gen].remove(page_number)
                self.generations[0].append(page_number)
                self.page_map[page_number] = 0
            return

        self.page_faults += 1
        
        if self.current_page_count == self.num_frames:
            victim_found = False
            for i in range(self.num_generations - 1, -1, -1):
                if self.generations[i]:
                    page_to_evict = self.generations[i].popleft()
                    del self.page_map[page_to_evict]
                    self.current_page_count -= 1
                    victim_found = True
                    break
            
            if not victim_found:
                print("MGLRU Error: Frames full but no victim found.")
                return

        self.generations[0].append(page_number)
        self.page_map[page_number] = 0
        self.current_page_count += 1