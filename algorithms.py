from abc import ABC, abstractmethod
from collections import deque

# --- Abstract Base Class for all Algorithms ---

class PageReplacementAlgorithm(ABC):
    """
    This is the abstract base class (like a blueprint) for all
    page replacement algorithms. It ensures every algorithm we
    write has the same standard methods.
    """
    def __init__(self, num_frames):
        if num_frames <= 0:
            raise ValueError("Number of frames must be positive.")
        self.num_frames = num_frames
        self.frames = []  # This list will represent physical memory
        self.page_faults = 0
        self.page_hits = 0

    @abstractmethod
    def process_page_request(self, page_number):
        """
        This is the main method that each algorithm must implement.
        It will process a single page request.
        """
        pass

    def get_stats(self):
        """
        Returns a dictionary of the final performance statistics.
        """
        total_requests = self.page_hits + self.page_faults
        hit_ratio = (self.page_hits / total_requests) if total_requests > 0 else 0
        miss_ratio = (self.page_faults / total_requests) if total_requests > 0 else 0
        
        return {
            "Total Requests": total_requests,
            "Page Faults": self.page_faults,
            "Page Hits": self.page_hits,
            "Hit Ratio": f"{hit_ratio:.2%}",
            "Miss Ratio": f"{miss_ratio:.2%}"
        }

# --- 1. FIFO (First-In, First-Out) Module ---

class FIFO(PageReplacementAlgorithm):
    """
    Implements the First-In, First-Out (FIFO) algorithm.
    Uses a simple queue (deque) to track the order of pages.
    """
    def __init__(self, num_frames):
        super().__init__(num_frames)
        # We use a deque (double-ended queue) as our queue
        # self.frames will store what's in memory
        # self.queue will store the *order* they arrived
        self.queue = deque()

    def process_page_request(self, page_number):
        """
        Processes a single page request using FIFO logic.
        """
        # Check for a Page Hit
        if page_number in self.frames:
            self.page_hits += 1
            # No page fault, no eviction, so we're done.
            return

        # --- Process a Page Fault ---
        self.page_faults += 1
        
        # If frames are not full, just add the new page
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
            self.queue.append(page_number) # Add to the back of the queue
        else:
            # Frames are full, we must evict.
            # 1. Find the oldest page (front of the queue)
            page_to_evict = self.queue.popleft() # Remove from front
            
            # 2. Remove it from memory (frames)
            self.frames.remove(page_to_evict)
            
            # 3. Add the new page to memory and the queue
            self.frames.append(page_number)
            self.queue.append(page_number) # Add to back

# --- 2. LRU (Least Recently Used) Module ---

class LRU(PageReplacementAlgorithm):
    """
    Implements the Least Recently Used (LRU) algorithm.
    
    We use the self.frames list as our LRU tracker.
    - The page at index 0 is the LEAST recently used.
    - The page at the end (index -1) is the MOST recently used.
    """
    def __init__(self, num_frames):
        super().__init__(num_frames)

    def process_page_request(self, page_number):
        """
        Processes a single page request using LRU logic.
        """
        
        # Check for a Page Hit
        if page_number in self.frames:
            self.page_hits += 1
            # --- This is the key LRU logic ---
            # A hit means this page is now the "most recently used".
            # So, we remove it from its current position...
            self.frames.remove(page_number)
            # ...and append it to the end of the list.
            self.frames.append(page_number)
            return

        # --- Process a Page Fault ---
        self.page_faults += 1
        
        # If frames are not full, just add the new page to the end
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
        else:
            # Frames are full, we must evict.
            # 1. Evict the LRU page (the one at the front, index 0)
            self.frames.pop(0) 
            
            # 2. Add the new page to the end (making it the MRU page)
            self.frames.append(page_number)

# --- 3. Optimal (OPT) Module (Corrected) ---

class Optimal(PageReplacementAlgorithm):
    """
    Implements the Optimal (OPT) page replacement algorithm.
    
    This algorithm is theoretical and looks into the "future"
    (the rest of the workload) to make the best possible eviction choice.
    """
    def __init__(self, num_frames):
        # We don't need the workload here.
        # It will be passed to process_page_request.
        super().__init__(num_frames)

    def process_page_request(self, page_number, workload_future):
        """
        Processes a single page request using Optimal logic.
        
        Args:
            page_number (int): The page being requested.
            workload_future (list): The *entire* future workload,
                                    starting from the *next* request.
        """
        
        # Check for a Page Hit
        if page_number in self.frames:
            self.page_hits += 1
            # No logic needed on a hit, just return
            return

        # --- Process a Page Fault ---
        self.page_faults += 1
        
        # If frames are not full, just add the new page
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
        else:
            # Frames are full, we must evict.
            # This is the core Optimal logic.
            
            # 1. Find which page in our frames is used
            #    furthest in the future.
            page_to_evict = self._find_furthest_used_page(workload_future)
            
            # 2. Replace it
            self.frames.remove(page_to_evict)
            self.frames.append(page_number)

    def _find_furthest_used_page(self, future_workload):
        """
        Helper function to find the page in frames that is used
        furthest in the future.
        """
        
        # Store the index of the *next* use for each page in frames
        # {page: next_use_index}
        next_use = {}
        
        # Find the next use for each page currently in our frames
        for page in self.frames:
            try:
                # Find the first index of 'page' in the future
                future_index = future_workload.index(page)
                next_use[page] = future_index
            except ValueError:
                # If the page is *never* used again in the future,
                # it's the PERFECT page to evict.
                # We can return it immediately.
                return page
        
        # If all pages are used again, we find the one
        # used *furthest* away (highest index).
        # We get the page with the maximum 'future_index' value
        page_to_evict = max(next_use, key=next_use.get)
        return page_to_evict