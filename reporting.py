import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_comparison_graph(results_data, output_filename="comparison_plot.png"):
    
    
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
        
        plt.plot(alg_df['Frames'], alg_df['Miss Ratio (raw)'], marker='o', linestyle='-', label=alg_name)
        

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
    
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not results_data:
        print("Reporting Error: No results data to save to CSV.")
        return

    df = pd.DataFrame(results_data)
    

    if 'Hit Ratio (raw)' in df.columns:
        df = df.drop(columns=['Hit Ratio (raw)'])
    if 'Miss Ratio (raw)' in df.columns:
        df = df.drop(columns=['Miss Ratio (raw)'])
        
    cols = ['Algorithm', 'Frames', 'Page Faults', 'Page Hits', 'Total Requests', 'Miss Ratio', 'Hit Ratio']
    final_cols = [c for c in cols if c in df.columns]
    df = df[final_cols]
    
    try:
        df.to_csv(filepath, index=False)
        print(f"[+] Success! CSV report saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving CSV report: {e}")



def plot_timeline_events(timeline, output_filename="timeline_plot.png"):
    
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not timeline:
        print("Reporting Error: No timeline data to plot.")
        return

    hits = []    
    faults = []  
    
    for entry in timeline:
        step, page, event = entry[0], entry[1], entry[2]
        if event == "Hit":
            hits.append((step, page))
        else: 
            faults.append((step, page))


    hits_x = [h[0] for h in hits] if hits else [0]
    hits_y = [h[1] for h in hits] if hits else [0]
    faults_x = [f[0] for f in faults] if faults else [0]
    faults_y = [f[1] for f in faults] if faults else [0]

    plt.figure(figsize=(15, 8)) 
    
    if faults:
        plt.scatter(faults_x, faults_y, color='red', marker='x', s=50, label='Page Fault')
    if hits:
        plt.scatter(hits_x, hits_y, color='green', marker='o', s=10, alpha=0.7, label='Page Hit')

    plt.title('Timeline of Page Hits and Faults', fontsize=16)
    plt.xlabel('Simulation Step', fontsize=12)
    plt.ylabel('Page Number', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.xlim(0, max(hits_x + faults_x) + 1)
    all_pages = hits_y + faults_y
    plt.ylim(min(all_pages) - 1, max(all_pages) + 1)
    
    try:
        plt.savefig(filepath)
        print(f"[+] Success! Timeline plot saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving timeline plot: {e}")

def save_timeline_report(timeline, output_filename="timeline_report.txt"):
   
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
                if len(entry) == 4: 
                    step, page, event, frames = entry
                    evicted = "---"
                else: 
                    step, page, event, frames, evicted_page = entry
                    evicted = str(evicted_page) if evicted_page is not None else "---"
                
               
                if frames and isinstance(frames[0], tuple):
                    frames_str = ", ".join(map(str, frames))
                else:
                    frames_str = ", ".join(map(str, frames))

                f.write(f"{step:<5} | {page:<5} | {event:<5} | {evicted:<7} | {frames_str}\n")
        
        print(f"[+] Success! Timeline report saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving timeline report: {e}")


def plot_timeline_events(timeline, output_filename="timeline_plot.png"):
   
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not timeline:
        print("Reporting Error: No timeline data to plot.")
        return

    hits = []    
    faults = []  
    
    for entry in timeline:
        step, page, event = entry[0], entry[1], entry[2]
        if event == "Hit":
            hits.append((step, page))
        else: 
            faults.append((step, page))

 
    hits_x = [h[0] for h in hits] if hits else []
    hits_y = [h[1] for h in hits] if hits else []
    faults_x = [f[0] for f in faults] if faults else []
    faults_y = [f[1] for f in faults] if faults else []

    if not hits_x and not faults_x:
        print("No hits or faults to plot.")
        return
    
    plt.figure(figsize=(15, 8)) 
    
    if faults:
        plt.scatter(faults_x, faults_y, color='red', marker='x', s=50, label='Page Fault')
    if hits:
        plt.scatter(hits_x, hits_y, color='green', marker='o', s=10, alpha=0.7, label='Page Hit')

    plt.title('Timeline of Page Hits and Faults', fontsize=16)
    plt.xlabel('Simulation Step', fontsize=12)
    plt.ylabel('Page Number', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    all_steps = hits_x + faults_x
    all_pages = hits_y + faults_y
    plt.xlim(0, max(all_steps) + 1 if all_steps else 1)
    plt.ylim(min(all_pages) - 1 if all_pages else 0, max(all_pages) + 1 if all_pages else 1)
    
    try:
        plt.savefig(filepath)
        print(f"[+] Success! Timeline plot saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving timeline plot: {e}")

def plot_mglru_generations(generation_log, num_generations, output_filename="mglru_generations_plot.png"):
    
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not generation_log:
        print("Reporting Error: No MGLRU generation data to plot.")
        return

    columns = ['Step'] + [f'Gen {i}' for i in range(num_generations)]
    df = pd.DataFrame(generation_log, columns=columns)
    df = df.set_index('Step')

    plt.figure(figsize=(15, 8))
    
    try:
        plt.stackplot(df.index, [df[col] for col in df.columns], labels=df.columns)
    except Exception as e:
        print(f"Error plotting MGLRU stackplot: {e}")
        return

    plt.title('MGLRU Generation Sizes Over Time', fontsize=16)
    plt.xlabel('Simulation Step', fontsize=12)
    plt.ylabel('Number of Pages (Total Frames)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.xlim(0, df.index.max())
    plt.ylim(0, df.sum(axis=1).max() * 1.1) 

    try:
        plt.savefig(filepath)
        print(f"[+] Success! MGLRU generation plot saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving MGLRU plot: {e}")