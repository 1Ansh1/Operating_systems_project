def run_single_process(algorithm_instance, workload, num_frames):
    """
    Runs a simulation for a single process.
    
    This is the "engine" that connects all the modules.
    
    This new, simpler version just feeds page requests to the
    algorithm. The algorithm itself is responsible for tracking
    hits, faults, and its own frame state.
    """
    
    algo = algorithm_instance
    
    # 3. Run the main simulation loop
    for i, page_number in enumerate(workload):
        # We need to pass the future workload for the Optimal algorithm
        future_workload = workload[i+1:]
        
        # The algorithm's .process_page_request() method will
        # internally handle whether it's a hit or a fault.
        algo.process_page_request(page_number, workload_future=future_workload)
            
    # 4. At the end, just get the stats from the algorithm object
    return algo.get_stats()