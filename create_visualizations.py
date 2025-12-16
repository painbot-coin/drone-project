"""
Create Visualizations (Optional)
=================================
Creates visualizations if matplotlib is available.
Run this separately if you want to generate plots.
"""

import json
import os

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("ERROR: matplotlib is not installed.")
    print("Install it with: pip install matplotlib numpy")
    print("\nVisualizations cannot be created without matplotlib.")
    exit(1)

def create_all_visualizations():
    """Create all visualizations."""
    print("Creating visualizations...")
    
    # Load results
    if not os.path.exists("initial_benchmark_results.json"):
        print("Error: initial_benchmark_results.json not found")
        return
    
    with open("initial_benchmark_results.json", 'r') as f:
        benchmarks = json.load(f)["results"]
    
    methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
    method_names = {
        "astar": "A*",
        "dstar": "D* Lite",
        "double_q": "Double Q-Learning",
        "mr_ql": "MR-QLearning",
        "hybrid": "Hybrid A* + MR-QL",
        "neural_astar": "Neural A*",
        "enhanced_hybrid": "Enhanced Hybrid A* + RL"
    }
    
    os.makedirs("visualizations", exist_ok=True)
    
    # 1. Success Rate Bar Chart
    print("1. Creating success rate bar chart...")
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = []
    values = []
    
    for method in methods:
        if method in benchmarks:
            results = benchmarks[method]
            success_rate = sum(results["success"]) / len(results["success"]) * 100
            labels.append(method_names[method])
            values.append(success_rate)
    
    bars = ax.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Success Rate Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 105])
    ax.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('visualizations/success_rate_bar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: visualizations/success_rate_bar.png")
    
    # 2. Path Length Bar Chart
    print("2. Creating path length bar chart...")
    fig, ax = plt.subplots(figsize=(10, 6))
    means = []
    stds = []
    
    for method in methods:
        if method in benchmarks:
            results = benchmarks[method]
            success_list = results["success"]
            path_list = [p for p, s in zip(results["path_length"], success_list) if s]
            means.append(statistics.mean(path_list) if path_list else 0)
            stds.append(statistics.stdev(path_list) if len(path_list) > 1 else 0)
    
    bars = ax.bar(labels, means, yerr=stds, capsize=5,
                  color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    ax.set_ylabel('Path Length (steps)', fontsize=12)
    ax.set_title('Average Path Length Comparison', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/path_length_bar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: visualizations/path_length_bar.png")
    
    # 3. Box Plot
    print("3. Creating box plot...")
    fig, ax = plt.subplots(figsize=(10, 6))
    path_data = []
    
    for method in methods:
        if method in benchmarks:
            results = benchmarks[method]
            success_list = results["success"]
            path_list = [p for p, s in zip(results["path_length"], success_list) if s]
            path_data.append(path_list)
    
    bp = ax.boxplot(path_data, labels=labels, patch_artist=True)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Path Length (steps)', fontsize=12)
    ax.set_title('Path Length Distribution (Box Plot)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/path_length_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: visualizations/path_length_boxplot.png")
    
    print("\n✓ All visualizations created!")

if __name__ == "__main__":
    import statistics
    create_all_visualizations()

