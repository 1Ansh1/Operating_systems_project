from abc import ABC, abstractmethod
from collections import deque


class PageReplacementAlgorithm(ABC):

    def __init__(self, num_frames):
        if num_frames <= 0:
            raise ValueError("Number of frames must be positive.")
        self.num_frames = num_frames
        self.frames = []  
        self.page_faults = 0
        self.page_hits = 0
        self.step = 0          
        self.timeline = []     
    @abstractmethod
    def process_page_request(self, page_number, workload_future=None):
        
        pass

    def get_stats(self):
        
        total_requests = self.page_hits + self.page_faults
        hit_ratio_raw = (self.page_hits / total_requests) if total_requests > 0 else 0
        miss_ratio_raw = (self.page_faults / total_requests) if total_requests > 0 else 0
        
        return {
            "Total Requests": total_requests,
            "Page Faults": self.page_faults,
            "Page Hits": self.page_hits,
            "Hit Ratio": f"{hit_ratio_raw:.2%}",
            "Miss Ratio": f"{miss_ratio_raw:.2%}",
            "Hit Ratio (raw)": hit_ratio_raw,
            "Miss Ratio (raw)": miss_ratio_raw
        }

    def get_timeline(self):
        return self.timeline


class FIFO(PageReplacementAlgorithm):
    def __init__(self, num_frames):
        super().__init__(num_frames)
        self.queue = deque()


    def process_page_request(self, page_number, workload_future=None):
        self.step += 1
        if page_number in self.frames:
            self.page_hits += 1
            self.timeline.append((self.step, page_number, "Hit", list(self.frames)))
            return

        self.page_faults += 1
        page_to_evict = None
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
            self.queue.append(page_number)
        else:
            page_to_evict = self.queue.popleft()
            self.frames.remove(page_to_evict)
            self.frames.append(page_number)
            self.queue.append(page_number)
        
        self.timeline.append((self.step, page_number, "Fault", list(self.frames), page_to_evict))



class LRU(PageReplacementAlgorithm):
    def __init__(self, num_frames):
        super().__init__(num_frames)

   
    def process_page_request(self, page_number, workload_future=None):
        self.step += 1
        if page_number in self.frames:
            self.page_hits += 1
            self.frames.remove(page_number)
            self.frames.append(page_number)
            self.timeline.append((self.step, page_number, "Hit", list(self.frames)))
            return

        self.page_faults += 1
        page_to_evict = None
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
        else:
            page_to_evict = self.frames.pop(0) 
            self.frames.append(page_number)
            
        self.timeline.append((self.step, page_number, "Fault", list(self.frames), page_to_evict))



class Optimal(PageReplacementAlgorithm):
    def __init__(self, num_frames):
        super().__init__(num_frames)

    
    def process_page_request(self, page_number, workload_future):
        self.step += 1
        if page_number in self.frames:
            self.page_hits += 1
            self.timeline.append((self.step, page_number, "Hit", list(self.frames)))
            return

        self.page_faults += 1
        page_to_evict = None
        if len(self.frames) < self.num_frames:
            self.frames.append(page_number)
        else:
            page_to_evict = self._find_furthest_used_page(workload_future)
            self.frames.remove(page_to_evict)
            self.frames.append(page_number)
            
        self.timeline.append((self.step, page_number, "Fault", list(self.frames), page_to_evict))

    def _find_furthest_used_page(self, future_workload):
        next_use = {}
        for page in self.frames:
            try:
                future_index = future_workload.index(page)
                next_use[page] = future_index
            except ValueError:
                return page
        return max(next_use, key=next_use.get)



class MGLRU(PageReplacementAlgorithm):
    def __init__(self, num_frames, num_generations=4, aging_threshold=10):
        super().__init__(num_frames)
        self.num_generations = num_generations
        self.aging_threshold = aging_threshold
        
        self.generations = [deque() for _ in range(num_generations)]
        self.page_map = {}
        self.current_page_count = 0
        self.age_tick_counter = 0
        
        
        self.generation_log = [] 
        

    def _age_pages(self):
        for i in range(self.num_generations - 2, -1, -1):
            if self.generations[i]:
                page_to_age = self.generations[i].popleft()
                next_gen = i + 1
                self.generations[next_gen].append(page_to_age)
                self.page_map[page_to_age] = next_gen
                return

    def process_page_request(self, page_number, workload_future=None):
        self.step += 1
        
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
            
            current_frames = list(self.page_map.keys())
            self.timeline.append((self.step, page_number, "Hit", current_frames))
            
            
            self._log_generation_sizes()
            
            return

        self.page_faults += 1
        page_to_evict = None
        if self.current_page_count == self.num_frames:
            for i in range(self.num_generations - 1, -1, -1):
                if self.generations[i]:
                    page_to_evict = self.generations[i].popleft()
                    del self.page_map[page_to_evict]
                    self.current_page_count -= 1
                    break

        self.generations[0].append(page_number)
        self.page_map[page_number] = 0
        self.current_page_count += 1
        
        current_frames = list(self.page_map.keys())
        self.timeline.append((self.step, page_number, "Fault", current_frames, page_to_evict))
        
        
        self._log_generation_sizes()
       

   
    def _log_generation_sizes(self):
        gen_sizes = [len(gen) for gen in self.generations]
        log_entry = (self.step,) + tuple(gen_sizes)
        self.generation_log.append(log_entry)
  

  
    def get_generation_log(self):
        return self.generation_log
 