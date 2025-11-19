import algorithms
import math
from collections import defaultdict

def run_global_allocation_sim(alg_class, workload, total_frames):
    
    
   
    global_sim = alg_class(total_frames)
    
 
    for i, (pid, page_num) in enumerate(workload):
     
        page_to_request = (pid, page_num)
        
        future_workload = []
        
      
        if isinstance(global_sim, algorithms.Optimal):
            future_workload = workload[i+1:]
        
        global_sim.process_page_request(page_to_request, workload_future=future_workload)
        
 
    return global_sim.get_stats()


def run_fixed_allocation_sim(alg_class, workload, total_frames, num_processes):
    
    
    if total_frames < num_processes:
        print(f"Warning: Total frames ({total_frames}) is less than num processes ({num_processes}).")
        print("Allocating 1 frame per process.")
        frames_per_process = 1
    else:
   
        frames_per_process = math.floor(total_frames / num_processes)


    simulators = {}
    for pid in range(1, num_processes + 1):
        simulators[pid] = alg_class(frames_per_process)


    process_workloads = defaultdict(list)
    for pid, page_num in workload:
        process_workloads[pid].append(page_num)

    
    process_workloads_future = defaultdict(lambda: defaultdict(list))
    if alg_class == algorithms.Optimal:
        for pid, trace in process_workloads.items():
            for i in range(len(trace)):
                process_workloads_future[pid][i] = trace[i+1:]

   
    
    
    process_step = defaultdict(int) 
    
    for pid, page_num in workload:
        sim = simulators[pid]
        
        future = []
        if isinstance(sim, algorithms.Optimal):
            step = process_step[pid]
            future = process_workloads_future[pid][step]
            
        sim.process_page_request(page_num, workload_future=future)
        process_step[pid] += 1

   
    total_stats = {
        "Total Requests": 0,
        "Page Faults": 0,
        "Page Hits": 0,
    }
    
    for pid, sim in simulators.items():
        stats = sim.get_stats() 
        total_stats["Total Requests"] += stats["Total Requests"]
        total_stats["Page Faults"] += stats["Page Faults"]
        total_stats["Page Hits"] += stats["Page Hits"]

   
    hit_ratio = (total_stats["Page Hits"] / total_stats["Total Requests"]) if total_stats["Total Requests"] > 0 else 0
    miss_ratio = (total_stats["Page Faults"] / total_stats["Total Requests"]) if total_stats["Total Requests"] > 0 else 0
    
    total_stats["Hit Ratio"] = f"{hit_ratio:.2%}"
    total_stats["Miss Ratio"] = f"{miss_ratio:.2%}"
    
    return total_stats