import algorithms
import math
from collections import defaultdict

def run_global_allocation_sim(alg_class, workload, total_frames):
    """
    Runs a simulation using GLOBAL replacement.
    
    All processes share one pool of frames.
    We create ONE algorithm instance and feed it
    (pid, page) tuples as the "page".
    """
    
    # 1. Create one algorithm instance for the whole system
    #    Our classes are smart enough to treat (pid, page)
    #    as a single hashable "page"
    global_sim = alg_class(total_frames)
    
    # 2. Run the simulation loop
    for i, (pid, page_num) in enumerate(workload):
        # The "page" we request is the (pid, page_num) tuple
        page_to_request = (pid, page_num)
        
        future_workload = []
        
        # For Optimal, we need to create the future trace of tuples
        if isinstance(global_sim, algorithms.Optimal):
            future_workload = workload[i+1:]
        
        global_sim.process_page_request(page_to_request, workload_future=future_workload)
        
    # 3. Return the final stats
    return global_sim.get_stats()


def run_fixed_allocation_sim(alg_class, workload, total_frames, num_processes):
    """
    Runs a simulation using FIXED allocation (Local Replacement).
    
    Each process gets an equal, fixed share of frames.
    We create a SEPARATE algorithm instance for each process.
    """
    
    if total_frames < num_processes:
        print(f"Warning: Total frames ({total_frames}) is less than num processes ({num_processes}).")
        print("Allocating 1 frame per process.")
        frames_per_process = 1
    else:
        # Give each process an equal share
        frames_per_process = math.floor(total_frames / num_processes)

    # 1. Create a dictionary of algorithm instances, one per process
    #    e.g., simulators = { 1: FIFO(16), 2: FIFO(16) }
    simulators = {}
    for pid in range(1, num_processes + 1):
        simulators[pid] = alg_class(frames_per_process)

    # 2. Create a dictionary to hold the workload for each process
    #    e.g., process_workloads = { 1: [10, 11, 12], 2: [5, 6, 7] }
    process_workloads = defaultdict(list)
    for pid, page_num in workload:
        process_workloads[pid].append(page_num)

    # 3. Create a "future" workload dict for the Optimal algorithm
    process_workloads_future = defaultdict(lambda: defaultdict(list))
    if alg_class == algorithms.Optimal:
        for pid, trace in process_workloads.items():
            for i in range(len(trace)):
                process_workloads_future[pid][i] = trace[i+1:]

    # 4. Run the simulation
    #    We route each request to its specific algorithm instance
    
    # Keep track of which step each process is on
    process_step = defaultdict(int) 
    
    for pid, page_num in workload:
        sim = simulators[pid]
        
        future = []
        if isinstance(sim, algorithms.Optimal):
            step = process_step[pid]
            future = process_workloads_future[pid][step]
            
        sim.process_page_request(page_num, workload_future=future)
        process_step[pid] += 1

    # 5. Aggregate the stats from all processes
    total_stats = {
        "Total Requests": 0,
        "Page Faults": 0,
        "Page Hits": 0,
    }
    
    for pid, sim in simulators.items():
        stats = sim.get_stats() # This returns strings, we need raw
        total_stats["Total Requests"] += stats["Total Requests"]
        total_stats["Page Faults"] += stats["Page Faults"]
        total_stats["Page Hits"] += stats["Page Hits"]

    # Calculate final ratios
    hit_ratio = (total_stats["Page Hits"] / total_stats["Total Requests"]) if total_stats["Total Requests"] > 0 else 0
    miss_ratio = (total_stats["Page Faults"] / total_stats["Total Requests"]) if total_stats["Total Requests"] > 0 else 0
    
    total_stats["Hit Ratio"] = f"{hit_ratio:.2%}"
    total_stats["Miss Ratio"] = f"{miss_ratio:.2%}"
    
    return total_stats