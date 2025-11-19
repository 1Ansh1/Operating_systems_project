import random

def parse_workload(filepath):
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
       
        content = content.replace(',', ' ').replace('\n', ' ')
        
       
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
    
    page_requests = []
    
    if type == 'random':
        for _ in range(length):
            page_requests.append(random.randint(0, max_page_num))
            
    elif type == 'sequential':
        for i in range(length):
            page_requests.append(i % (max_page_num + 1))
            
    elif type == 'locality':
        
        
        locality_size = max(1, max_page_num // 4) 
        
        current_page = random.randint(0, max_page_num)
        page_requests.append(current_page)
        
        for _ in range(length - 1):
            if random.random() < 0.8:
                offset = random.randint(-locality_size, locality_size)
                next_page = current_page + offset
               
                next_page = max(0, min(next_page, max_page_num)) 
                current_page = next_page
            else: 
                current_page = random.randint(0, max_page_num)
                
            page_requests.append(current_page)
            
    else:
        raise ValueError(f"Unknown workload type: '{type}'")
        
    return page_requests

def generate_multiprocess_workload(length, num_processes, max_page_per_process, type='locality'):
  
    trace = []
    
    process_generators = {}
    for i in range(num_processes):
        pid = i + 1
        
        process_generators[pid] = generate_workload(length, max_page_per_process, type)

   
    process_indices = {pid: 0 for pid in range(1, num_processes + 1)}

    for _ in range(length):
        
        active_pid = random.randint(1, num_processes)
        
       
        page_index = process_indices[active_pid]
        
        if page_index < length:
            page_num = process_generators[active_pid][page_index]
            trace.append((active_pid, page_num))
            process_indices[active_pid] += 1
        else:
           
            other_pid = (active_pid % num_processes) + 1
            page_index = process_indices[other_pid]
            if page_index < length:
                page_num = process_generators[other_pid][page_index]
                trace.append((other_pid, page_num))
                process_indices[other_pid] += 1

  
    return trace[:length]