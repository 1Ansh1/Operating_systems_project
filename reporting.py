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