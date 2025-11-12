import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_comparison_graph(results_data, output_filename="comparison_plot.png"):
    """
    Generates and saves a line graph comparing the miss ratios of
    different algorithms across a range of frame counts.
    """
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not results_data:
        print("Reporting Error: No results data to plot.")
        return

    df = pd.DataFrame(results_data)
    
    if df.empty:
        print("Reporting Error: DataFrame is empty, cannot plot.")
        return

    plt.figure(figsize=(12, 8))
    
    for alg_name in df['Algorithm'].unique():
        alg_df = df[df['Algorithm'] == alg_name]
        
        # --- THIS IS THE KEY FIX ---
        # We must plot the (raw) numeric column, not the string
        plt.plot(alg_df['Frames'], alg_df['Miss Ratio (raw)'], marker='o', linestyle='-', label=alg_name)
        # --- END OF FIX ---

    plt.title('Page Replacement Algorithm Comparison', fontsize=16)
    plt.xlabel('Number of Frames', fontsize=12)
    plt.ylabel('Miss Ratio', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    frame_ticks = df['Frames'].unique()
    if len(frame_ticks) > 20:
         step = 2 if len(frame_ticks) < 50 else 5
         plt.xticks(frame_ticks[::step])
    else:
         plt.xticks(frame_ticks)
         
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    plt.ylim(0, 1)
    
    try:
        plt.savefig(filepath)
        print(f"\n[+] Success! Comparison graph saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving plot: {e}")


def save_csv_report(results_data, output_filename="comparison_results.csv"):
    """
    Saves the final results DataFrame to a CSV file.
    
    Args:
        results_data (list of dicts): The same data used for plotting.
        output_filename (str): The name of the file to save the CSV.
    """
    
    # 1. Ensure the 'results' directory exists
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not results_data:
        print("Reporting Error: No results data to save to CSV.")
        return

    # 2. Convert to DataFrame
    df = pd.DataFrame(results_data)
    
    # 3. Clean up the DataFrame for export
    # We want to show the nice string-formatted ratios
    # And drop the raw numeric ones for the final report
    if 'Hit Ratio (raw)' in df.columns:
        df = df.drop(columns=['Hit Ratio (raw)'])
    if 'Miss Ratio (raw)' in df.columns:
        df = df.drop(columns=['Miss Ratio (raw)'])
        
    # Re-order columns for a nicer report
    cols = ['Algorithm', 'Frames', 'Page Faults', 'Page Hits', 'Total Requests', 'Miss Ratio', 'Hit Ratio']
    # Filter columns that actually exist in the dataframe
    final_cols = [c for c in cols if c in df.columns]
    df = df[final_cols]
    
    # 4. Save to CSV
    try:
        df.to_csv(filepath, index=False)
        print(f"[+] Success! CSV report saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving CSV report: {e}")



def plot_timeline_events(timeline, output_filename="timeline_plot.png"):
    """
    Generates a scatter plot visualizing the timeline of page hits
    and faults.
    
    Args:
        timeline (list of tuples): The timeline data from the algorithm.
        output_filename (str): The name of the file to save the plot.
    """
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not timeline:
        print("Reporting Error: No timeline data to plot.")
        return

    # 1. Separate hits and faults
    hits = []    # Stores (step, page)
    faults = []  # Stores (step, page)
    
    for entry in timeline:
        step, page, event = entry[0], entry[1], entry[2]
        if event == "Hit":
            hits.append((step, page))
        else: # "Fault"
            faults.append((step, page))

    # 2. Create lists for plotting
    #    (Handle empty lists just in case)
    hits_x = [h[0] for h in hits] if hits else [0]
    hits_y = [h[1] for h in hits] if hits else [0]
    faults_x = [f[0] for f in faults] if faults else [0]
    faults_y = [f[1] for f in faults] if faults else [0]

    # 3. Create the plot
    plt.figure(figsize=(15, 8)) # A wide figure is good for timelines
    
    # Plot faults *first* (as a larger 'X')
    if faults:
        plt.scatter(faults_x, faults_y, color='red', marker='x', s=50, label='Page Fault')
    # Plot hits *second* (as a smaller dot)
    if hits:
        plt.scatter(hits_x, hits_y, color='green', marker='o', s=10, alpha=0.7, label='Page Hit')

    # 4. Format the plot
    plt.title('Timeline of Page Hits and Faults', fontsize=16)
    plt.xlabel('Simulation Step', fontsize=12)
    plt.ylabel('Page Number', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Set axis limits
    plt.xlim(0, max(hits_x + faults_x) + 1)
    all_pages = hits_y + faults_y
    plt.ylim(min(all_pages) - 1, max(all_pages) + 1)
    
    # 5. Save the plot
    try:
        plt.savefig(filepath)
        print(f"[+] Success! Timeline plot saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving timeline plot: {e}")

# --- ADD THIS FIRST FUNCTION ---
def save_timeline_report(timeline, output_filename="timeline_report.txt"):
    """
    Saves a step-by-step timeline report to a text file.
    """
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write("--- Page Replacement Timeline ---\n\n")
            f.write(f"{'Step':<5} | {'Page':<5} | {'Event':<5} | {'Evicted':<7} | Frames State\n")
            f.write("-" * 60 + "\n")
            
            for entry in timeline:
                if len(entry) == 4: # Hit (no eviction)
                    step, page, event, frames = entry
                    evicted = "---"
                else: # Fault (with eviction)
                    step, page, event, frames, evicted_page = entry
                    evicted = str(evicted_page) if evicted_page is not None else "---"
                
                # The 'frames' state for MGLRU might be a list of tuples,
                # so we need to handle that.
                if frames and isinstance(frames[0], tuple):
                    frames_str = ", ".join(map(str, frames))
                else:
                    frames_str = ", ".join(map(str, frames))

                f.write(f"{step:<5} | {page:<5} | {event:<5} | {evicted:<7} | {frames_str}\n")
        
        print(f"[+] Success! Timeline report saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving timeline report: {e}")

# --- AND ADD THIS SECOND FUNCTION ---
def plot_timeline_events(timeline, output_filename="timeline_plot.png"):
    """
    Generates a scatter plot visualizing the timeline of page hits
    and faults.
    """
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not timeline:
        print("Reporting Error: No timeline data to plot.")
        return

    # 1. Separate hits and faults
    hits = []    # Stores (step, page)
    faults = []  # Stores (step, page)
    
    for entry in timeline:
        step, page, event = entry[0], entry[1], entry[2]
        if event == "Hit":
            hits.append((step, page))
        else: # "Fault"
            faults.append((step, page))

    # 2. Create lists for plotting
    hits_x = [h[0] for h in hits] if hits else []
    hits_y = [h[1] for h in hits] if hits else []
    faults_x = [f[0] for f in faults] if faults else []
    faults_y = [f[1] for f in faults] if faults else []

    # Handle case where one list is empty
    if not hits_x and not faults_x:
        print("No hits or faults to plot.")
        return
    
    # 3. Create the plot
    plt.figure(figsize=(15, 8)) # A wide figure is good for timelines
    
    if faults:
        plt.scatter(faults_x, faults_y, color='red', marker='x', s=50, label='Page Fault')
    if hits:
        plt.scatter(hits_x, hits_y, color='green', marker='o', s=10, alpha=0.7, label='Page Hit')

    # 4. Format the plot
    plt.title('Timeline of Page Hits and Faults', fontsize=16)
    plt.xlabel('Simulation Step', fontsize=12)
    plt.ylabel('Page Number', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Set axis limits
    all_steps = hits_x + faults_x
    all_pages = hits_y + faults_y
    plt.xlim(0, max(all_steps) + 1 if all_steps else 1)
    plt.ylim(min(all_pages) - 1 if all_pages else 0, max(all_pages) + 1 if all_pages else 1)
    
    # 5. Save the plot
    try:
        plt.savefig(filepath)
        print(f"[+] Success! Timeline plot saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving timeline plot: {e}")

def plot_mglru_generations(generation_log, num_generations, output_filename="mglru_generations_plot.png"):
    """
    Generates a stacked area plot showing the size of MGLRU
    generations over time.
    """
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not generation_log:
        print("Reporting Error: No MGLRU generation data to plot.")
        return

    # 1. Convert log to DataFrame
    columns = ['Step'] + [f'Gen {i}' for i in range(num_generations)]
    df = pd.DataFrame(generation_log, columns=columns)
    df = df.set_index('Step')

    # 2. Create the plot
    # A stacked area plot is perfect for this
    plt.figure(figsize=(15, 8))
    
    # We create a stacked area plot
    # `x` is the steps (the index), `y` is the list of columns
    try:
        plt.stackplot(df.index, [df[col] for col in df.columns], labels=df.columns)
    except Exception as e:
        print(f"Error plotting MGLRU stackplot: {e}")
        return

    # 3. Format the plot
    plt.title('MGLRU Generation Sizes Over Time', fontsize=16)
    plt.xlabel('Simulation Step', fontsize=12)
    plt.ylabel('Number of Pages (Total Frames)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Set axis limits
    plt.xlim(0, df.index.max())
    # The Y-axis max is the total number of frames, which is the sum of pages
    plt.ylim(0, df.sum(axis=1).max() * 1.1) # Add 10% headroom

    # 4. Save the plot
    try:
        plt.savefig(filepath)
        print(f"[+] Success! MGLRU generation plot saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving MGLRU plot: {e}")