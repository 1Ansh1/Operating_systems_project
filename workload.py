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