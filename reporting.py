import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_comparison_graph(results_data, output_filename="comparison_plot.png"):
    """
    Generates and saves a line graph comparing the miss ratios of
    different algorithms across a range of frame counts.
    
    Args:
        results_data (list of dicts): A list where each dict is a
                                      simulation result.
        output_filename (str): The name of the file to save the plot.
    """
    
    # 1. Ensure the 'results' directory exists
    output_path = "results"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    filepath = os.path.join(output_path, output_filename)
    
    if not results_data:
        print("Reporting Error: No results data to plot.")
        return

    # 2. Convert results to a pandas DataFrame for easy plotting
    df = pd.DataFrame(results_data)
    
    if df.empty:
        print("Reporting Error: DataFrame is empty, cannot plot.")
        return

    # 3. Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot a separate line for each algorithm
    for alg_name in df['Algorithm'].unique():
        alg_df = df[df['Algorithm'] == alg_name]
        plt.plot(alg_df['Frames'], alg_df['Miss Ratio'], marker='o', linestyle='-', label=alg_name)

    # 4. Format the plot
    plt.title('Page Replacement Algorithm Comparison', fontsize=16)
    plt.xlabel('Number of Frames', fontsize=12)
    plt.ylabel('Miss Ratio', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Use a better X-axis, especially for many frames
    frame_ticks = df['Frames'].unique()
    if len(frame_ticks) > 20:
         # If more than 20 points, show every 2nd or 5th tick
         step = 2 if len(frame_ticks) < 50 else 5
         plt.xticks(frame_ticks[::step])
    else:
         plt.xticks(frame_ticks) # Show all ticks if fewer than 20
         
    # Set Y-axis to be a percentage
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    plt.ylim(0, 1) # Miss ratio is always between 0 and 1
    
    # 5. Save the plot to the file
    try:
        plt.savefig(filepath)
        print(f"\n[+] Success! Comparison graph saved to: {filepath}")
    except Exception as e:
        print(f"\n[-] Error saving plot: {e}")