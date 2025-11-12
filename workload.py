import random

def parse_workload(filepath):
    """
    Reads a workload trace from a specified text file.
    
    The file should contain page numbers as integers, separated
    by commas, spaces, or newlines.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Clean the content: replace newlines/commas with spaces
        content = content.replace(',', ' ').replace('\n', ' ')
        
        # Split by spaces and convert to integers
        page_requests = [int(page) for page in content.split() if page.isdigit()]
        
        if not page_requests:
            print(f"Warning: Workload file '{filepath}' is empty or has invalid format.")
            return []
            
        return page_requests
        
    except FileNotFoundError:
        print(f"Error: Workload file not found at '{filepath}'")
        return []
    except Exception as e:
        print(f"Error parsing workload file '{filepath}': {e}")
        return []

def generate_workload(length, max_page_num, type='random'):
    """
    Generates a synthetic workload (a list of page requests).
    
    Args:
        length (int): The total number of page requests in the trace.
        max_page_num (int): The highest possible page number (e.g., 20).
        type (str): The type of workload to generate:
                    'random' - Any page from 0 to max_page_num.
                    'sequential' - 0, 1, 2, ..., max, 0, 1, 2, ...
                    'locality' - Simulates locality of reference (pages
                                 cluster around a 'hot' page).
    """
    page_requests = []
    
    if type == 'random':
        for _ in range(length):
            page_requests.append(random.randint(0, max_page_num))
            
    elif type == 'sequential':
        for i in range(length):
            page_requests.append(i % (max_page_num + 1))
            
    elif type == 'locality':
        # Simple locality simulation:
        # 80% chance to request a page near the last page (the "hot" set)
        # 20% chance to jump to a new random page (a "cold" miss)
        
        # Define the size of the "hot" set
        locality_size = max(1, max_page_num // 4) 
        
        # Start with a random page
        current_page = random.randint(0, max_page_num)
        page_requests.append(current_page)
        
        for _ in range(length - 1):
            if random.random() < 0.8: # 80% chance of a "hot" request
                # Request a page near the current one
                offset = random.randint(-locality_size, locality_size)
                next_page = current_page + offset
                # Keep it within bounds
                next_page = max(0, min(next_page, max_page_num)) 
                current_page = next_page
            else: # 20% chance of a "cold" request
                current_page = random.randint(0, max_page_num)
                
            page_requests.append(current_page)
            
    else:
        raise ValueError(f"Unknown workload type: '{type}'")
        
    return page_requests

def generate_multiprocess_workload(length, num_processes, max_page_per_process, type='locality'):
    """
    Generates a synthetic multi-process workload.
    
    Each item in the trace is a tuple: (process_id, page_number)
    
    Args:
        length (int): Total number of page requests in the trace.
        num_processes (int): Number of processes to simulate.
        max_page_per_process (int): Max page number *for each* process.
        type (str): The type of workload (e.g., 'locality').
    
    Returns:
        A list of (pid, page) tuples.
    """
    trace = []
    
    # Create a list of 'process' generators, one for each pid
    # Each process will have its own 'locality'
    process_generators = {}
    for i in range(num_processes):
        pid = i + 1
        # We use a trick by generating a *full* workload for each
        # process, and then we'll pick from them.
        # This simulates each process running its own program.
        process_generators[pid] = generate_workload(length, max_page_per_process, type)

    # Simulate a "context switch" by randomly picking which
    # process makes the next request.
    
    # Keep track of the current index for each process's trace
    process_indices = {pid: 0 for pid in range(1, num_processes + 1)}

    for _ in range(length):
        # Pick a process to run next
        # (This is a simple random switch, a real OS is more complex)
        active_pid = random.randint(1, num_processes)
        
        # Get the next page for that process
        page_index = process_indices[active_pid]
        
        if page_index < length: # Check if this process's trace is done
            page_num = process_generators[active_pid][page_index]
            trace.append((active_pid, page_num))
            process_indices[active_pid] += 1
        else:
            # This process finished its trace, just pick another
            # (In a real scenario, this gets more complex, but for
            # simulation, we can just grab from another process)
            other_pid = (active_pid % num_processes) + 1
            page_index = process_indices[other_pid]
            if page_index < length:
                page_num = process_generators[other_pid][page_index]
                trace.append((other_pid, page_num))
                process_indices[other_pid] += 1

    # Ensure we have *exactly* the length requested
    return trace[:length]