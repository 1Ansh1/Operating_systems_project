from metrics import MetricsCollector

from metrics import MetricsCollector
import algorithms as alg_module # Import the module itself

def run_single_process(algorithm_instance, workload, num_frames):
    """
    Runs a simulation for a single process.
    
    This is the "engine" that connects all the modules.
    """
    
    metrics = MetricsCollector()
    algo = algorithm_instance
    
    # Check if the algorithm is Optimal so we can pass the future workload
    is_optimal = isinstance(algo, alg_module.Optimal)
    
    # 3. Run the main simulation loop
    for i, page_number in enumerate(workload):
        step = i + 1
        
        # Is it a hit or a fault?
        if page_number in algo.frames:
            # --- Page Hit ---
            if is_optimal:
                # Optimal doesn't need to do anything on a hit
                algo.process_page_request(page_number, []) # Pass empty list
            else:
                # LRU and others need to process hits
                algo.process_page_request(page_number)
            
            metrics.record_hit(step, page_number, algo.frames)
        else:
            # --- Page Fault ---
            if is_optimal:
                # Pass the future workload (from the *next* step on)
                future_workload = workload[i+1:]
                algo.process_page_request(page_number, future_workload)
            else:
                algo.process_page_request(page_number)
                
            metrics.record_fault(step, page_number, algo.frames)
            
    # 4. Return the results
    return metrics