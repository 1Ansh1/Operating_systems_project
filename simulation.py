def run_single_process(algorithm_instance, workload, num_frames):
    
    algo = algorithm_instance
    
   
    for i, page_number in enumerate(workload):
       
        future_workload = workload[i+1:]
        
        algo.process_page_request(page_number, workload_future=future_workload)
            
    return algo.get_stats()