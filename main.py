import argparse
import algorithms
import workload
import simulation
import multi_process_simulation as multi_sim 
import reporting 
from tqdm import tqdm

def run_single_simulation(args):
    
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

    algo_instance = get_algorithm_instance(args.alg, args.frames)
    if not algo_instance:
        print(f"Error: Algorithm '{args.alg}' is not implemented.")
        return

    print(f"--- Running Single-Process Simulation ---")
    print(f"Algorithm: {args.alg}")
    print(f"Frames: {args.frames}")
    print(f"Total Page Requests: {len(page_requests)}")
    print("--------------------------")

    stats = simulation.run_single_process(algo_instance, page_requests, args.frames)
    
    print("\n--- Simulation Results ---")
    print_stats(stats)
    timeline_data = algo_instance.get_timeline()
    reporting.save_timeline_report(timeline_data)
    
    
    reporting.plot_timeline_events(timeline_data)
    if isinstance(algo_instance, algorithms.MGLRU):
        gen_log = algo_instance.get_generation_log()
        num_gens = algo_instance.num_generations
        reporting.plot_mglru_generations(gen_log, num_gens)


def run_comparison_simulation(args):
    
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
    min_frames, max_frames = args.compare
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
                    algo_instance = get_algorithm_instance(alg_name, num_frames)
                    stats = simulation.run_single_process(algo_instance, page_requests, num_frames)
                    stats['Algorithm'] = alg_name
                    stats['Frames'] = num_frames
                    results_data.append(stats)
                except Exception as e:
                    print(f"\n[!] Error during simulation: {alg_name} @ {num_frames} frames. Error: {e}")
                
                pbar.update(1)

    print("\nSimulations complete. Generating outputs...")
    reporting.plot_comparison_graph(results_data)
    reporting.save_csv_report(results_data)


def run_multi_process_simulation(args):
    
    try:
        alloc_strategy = args.multi[0]
        alg_name = args.multi[1]
        total_frames = int(args.multi[2])
        num_processes = int(args.multi[3])
    except Exception:
        print("Error: Invalid arguments for --multi mode.")
        print("Expected: --multi <fixed|global> <ALG> <FRAMES> <NUM_PROCS>")
        return

    if args.workload_file:
        print("Error: --multi mode requires a *generated* workload.")
        print("Please use --generate_multiprocess instead.")
        return
    if not args.generate_multiprocess:
        print("Error: --multi mode requires --generate_multiprocess.")
        return

    try:
        w_type = args.generate_multiprocess[0]
        w_len = int(args.generate_multiprocess[1])
        w_max_per_proc = int(args.generate_multiprocess[2])
    except Exception:
        print("Error: Invalid arguments for --generate_multiprocess.")
        print("Expected: --generate_multiprocess <TYPE> <LENGTH> <MAX_PAGE_PER_PROC>")
        return

    alg_class = get_algorithm_class(alg_name)
    if not alg_class:
        print(f"Error: Algorithm '{alg_name}' not found.")
        return
        
    print(f"Generating multi-process workload...")
    mp_workload = workload.generate_multiprocess_workload(w_len, num_processes, w_max_per_proc, w_type)
    
    print(f"--- Running Multi-Process Simulation ---")
    print(f"Allocation: {alloc_strategy}")
    print(f"Algorithm: {alg_name}")
    print(f"Total Frames: {total_frames}")
    print(f"Num Processes: {num_processes}")
    print(f"Workload: {w_type}, Length={w_len}")
    print("----------------------------------------")

    stats = {}
    if alloc_strategy == 'fixed':
        stats = multi_sim.run_fixed_allocation_sim(alg_class, mp_workload, total_frames, num_processes)
    elif alloc_strategy == 'global':
        stats = multi_sim.run_global_allocation_sim(alg_class, mp_workload, total_frames)
    else:
        print(f"Error: Unknown allocation strategy '{alloc_strategy}'.")
        return

    print("\n--- Multi-Process Results ---")
    print_stats(stats)


def get_algorithm_class(alg_name):
   
    if alg_name == 'FIFO':
        return algorithms.FIFO
    elif alg_name == 'LRU':
        return algorithms.LRU
    elif alg_name == 'Optimal':
        return algorithms.Optimal
    elif alg_name == 'MGLRU':
        return algorithms.MGLRU
    else:
        return None

def get_algorithm_instance(alg_name, num_frames):
   
    alg_class = get_algorithm_class(alg_name)
    if alg_class:
        return alg_class(num_frames)
    return None

def print_stats(stats):
   
    print(f"Total Requests: {stats.get('Total Requests', 'N/A')}")
    print(f"Page Hits: {stats.get('Page Hits', 'N/A')}")
    print(f"Page Faults: {stats.get('Page Faults', 'N/A')}")
    print(f"Hit Ratio: {stats.get('Hit Ratio', 'N/A')}")
    print(f"Miss Ratio: {stats.get('Miss Ratio', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Page Replacement Algorithm Simulator")
    
    workload_group = parser.add_mutually_exclusive_group(required=True)
    workload_group.add_argument('--workload_file', type=str,
                                help='(Single-Process) Path to a workload trace file.')
    workload_group.add_argument('--generate_workload', nargs=3,
                                metavar=('TYPE', 'LEN', 'MAX_P'),
                                help="(Single-Process) Generate a workload.")
    workload_group.add_argument('--generate_multiprocess', nargs=3,
                                metavar=('TYPE', 'LEN', 'MAX_P_PER_PROC'),
                                help="(Multi-Process) Generate a multi-process workload.")

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--single', nargs=2,
                            metavar=('ALG', 'FRAMES'),
                            help="Run a single-process simulation.")
    mode_group.add_argument('--compare', nargs=2, type=int,
                            metavar=('MIN_F', 'MAX_F'),
                            help="Run a single-process comparison plot.")
    mode_group.add_argument('--multi', nargs=4,
                            metavar=('ALLOC', 'ALG', 'FRAMES', 'NUM_PROCS'),
                            help="Run a multi-process simulation (e.g., 'fixed FIFO 128 4')")

    args = parser.parse_args()

    if args.single:
        args.alg = args.single[0]
        args.frames = int(args.single[1])
        run_single_simulation(args)
        
    elif args.compare:
        run_comparison_simulation(args)
        
    elif args.multi:
        run_multi_process_simulation(args)

if __name__ == "__main__":
    main()