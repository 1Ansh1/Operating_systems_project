import argparse
import algorithms
import workload
import simulation
import reporting 
from tqdm import tqdm

def run_single_simulation(args):
    """
    Runs a SINGLE simulation based on the arguments.
    """
    page_requests = []
    if args.workload_file:
        print(f"Parsing workload from: {args.workload_file}")
        page_requests = workload.parse_workload(args.workload_file)
    else:
        w_type, w_len, w_max = args.generate_workload
        w_len, w_max = int(w_len), int(w_max)
        print(f"Generating workload: {w_type}, Length={w_len}, Max Page={w_max}")
        page_requests = workload.generate_workload(w_len, w_max, w_type)

    if not page_requests:
        print("Error: No workload to process. Exiting.")
        return

    algo_instance = get_algorithm_instance(args.alg, args.frames, page_requests)
    if not algo_instance:
        print(f"Error: Algorithm '{args.alg}' is not implemented.")
        return

    print(f"--- Running Simulation ---")
    print(f"Algorithm: {args.alg}")
    print(f"Frames: {args.frames}")
    print(f"Total Page Requests: {len(page_requests)}")
    print("--------------------------")

    stats = simulation.run_single_process(algo_instance, page_requests, args.frames)
    
    print("\n--- Simulation Results ---")
    print(f"Total Requests: {stats['Total Requests']}")
    print(f"Page Hits: {stats['Page Hits']}")
    print(f"Page Faults: {stats['Page Faults']}")
    print(f"Hit Ratio: {stats['Hit Ratio']}")   # Uses the formatted string
    print(f"Miss Ratio: {stats['Miss Ratio']}") # Uses the formatted string
    print("--------------------------\n")


def run_comparison_simulation(args):
    """
    Runs a COMPARISON simulation, looping through algorithms and frame counts.
    """
    page_requests = []
    if args.workload_file:
        print(f"Parsing workload from: {args.workload_file}")
        page_requests = workload.parse_workload(args.workload_file)
    else:
        w_type, w_len, w_max = args.generate_workload
        w_len, w_max = int(w_len), int(w_max)
        print(f"Generating workload: {w_type}, Length={w_len}, Max Page={w_max}")
        page_requests = workload.generate_workload(w_len, w_max, w_type)

    if not page_requests:
        print("Error: No workload to process. Exiting.")
        return
    
    alg_list = ['FIFO', 'LRU', 'Optimal', 'MGLRU']
    
    min_frames = args.compare[0]
    max_frames = args.compare[1]
    frame_range = range(min_frames, max_frames + 1)
    
    results_data = []
    
    print(f"--- Running Comparison Simulation ---")
    print(f"Workload Length: {len(page_requests)}")
    print(f"Algorithms: {', '.join(alg_list)}")
    print(f"Frame Range: {min_frames} to {max_frames}")
    
    total_sims = len(alg_list) * len(frame_range)
    with tqdm(total=total_sims, desc="Running Simulations") as pbar:
        for alg_name in alg_list:
            for num_frames in frame_range:
                try:
                    algo_instance = get_algorithm_instance(alg_name, num_frames, page_requests)
                    
                    stats = simulation.run_single_process(algo_instance, page_requests, num_frames)
                    
                    stats['Algorithm'] = alg_name
                    stats['Frames'] = num_frames
                    results_data.append(stats)
                except Exception as e:
                    print(f"\n[!] Error during simulation: {alg_name} @ {num_frames} frames.")
                    print(f"    Error: {e}")
                    # Continue to the next simulation
                
                pbar.update(1)

    print("\nSimulations complete. Generating plot...")

    # --- THIS IS THE KEY FIX ---
    # The old conversion loop is no longer needed and has been removed.
    # We just pass the raw results_data to the reporting function.
    # --- END OF FIX ---

    reporting.plot_comparison_graph(results_data)
    reporting.save_csv_report(results_data)


def get_algorithm_instance(alg_name, num_frames, page_requests):
    """
    Factory function to get an initialized algorithm instance.
    """
    if alg_name == 'FIFO':
        return algorithms.FIFO(num_frames)
    elif alg_name == 'LRU':
        return algorithms.LRU(num_frames)
    elif alg_name == 'Optimal':
        return algorithms.Optimal(num_frames)
    elif alg_name == 'MGLRU':
        return algorithms.MGLRU(num_frames)
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Page Replacement Algorithm Simulator")
    
    workload_group = parser.add_mutually_exclusive_group(required=True)
    workload_group.add_argument('--workload_file',
                                type=str,
                                help='Path to a workload trace file.')
    workload_group.add_argument('--generate_workload',
                                nargs=3,
                                metavar=('TYPE', 'LENGTH', 'MAX_PAGE'),
                                help="Generate a workload: TYPE LENGTH MAX_PAGE (e.g., 'random 100 20')")

    mode_group = parser.add_mutually_exclusive_group(required=True)
    
    mode_group.add_argument('--single',
                            nargs=2,
                            metavar=('ALG', 'FRAMES'),
                            help="Run a single simulation: ALG FRAMES (e.g., 'FIFO 4')")
                            
    mode_group.add_argument('--compare',
                            nargs=2,
                            type=int,
                            metavar=('MIN_F', 'MAX_F'),
                            help="Run a comparison: MIN_FRAMES MAX_FRAMES (e.g., '1 20')")

    args = parser.parse_args()

    if args.single:
        args.alg = args.single[0]
        args.frames = int(args.single[1])
        if args.alg not in ['FIFO', 'LRU', 'Optimal', 'MGLRU']:
             parser.error(f"Algorithm '{args.alg}' is not a valid choice.")
        if args.frames <= 0:
             parser.error("Number of frames must be positive.")
        
        run_single_simulation(args)
        
    elif args.compare:
        run_comparison_simulation(args)

if __name__ == "__main__":
    main()