"""
Generate Detailed Comparison Tables
===================================
Creates formatted comparison tables from actual experimental data.
"""

import json
import statistics
import os

def load_results():
    """Load all result files."""
    results = {}
    
    if os.path.exists("initial_benchmark_results.json"):
        with open("initial_benchmark_results.json", 'r') as f:
            results["benchmarks"] = json.load(f)
    
    if os.path.exists("ablation_study_results.json"):
        with open("ablation_study_results.json", 'r') as f:
            results["ablation"] = json.load(f)
    
    if os.path.exists("comprehensive_experiments_results.json"):
        with open("comprehensive_experiments_results.json", 'r') as f:
            results["experiments"] = json.load(f)
    
    return results

def generate_baseline_table(results):
    """Generate baseline comparison table."""
    if "benchmarks" not in results:
        return None
    
    benchmarks = results["benchmarks"]["results"]
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
    
    print("\n" + "="*100)
    print("TABLE 1: Baseline Performance Comparison")
    print("="*100)
    print("(50 trials, 20×20 grid, 15% obstacle density)")
    print()
    print(f"{'Method':<30} {'Success%':<12} {'Path Length':<15} {'Std Dev':<12} {'Time(s)':<12} {'Battery%':<12} {'Collisions':<12}")
    print("-"*100)
    
    for method in methods:
        if method not in benchmarks:
            continue
        
        results_data = benchmarks[method]
        success_list = results_data["success"]
        path_list = results_data["path_length"]
        time_list = results_data["time"]
        battery_list = results_data["battery"]
        collisions_list = results_data["collisions_static"]
        
        success_rate = sum(success_list) / len(success_list) * 100
        path_success = [p for p, s in zip(path_list, success_list) if s]
        avg_path = statistics.mean(path_success) if path_success else 0
        std_path = statistics.stdev(path_success) if len(path_success) > 1 else 0
        avg_time = statistics.mean(time_list)
        avg_battery = statistics.mean([b for b, s in zip(battery_list, success_list) if s]) if any(success_list) else 0
        avg_collisions = statistics.mean(collisions_list)
        
        name = method_names[method]
        print(f"{name:<30} {success_rate:>10.1f}%  {avg_path:>13.1f}  {std_path:>10.1f}  {avg_time:>10.3f}  {avg_battery:>10.1f}%  {avg_collisions:>10.1f}")
    
    print("="*100)

def generate_ablation_table(results):
    """Generate ablation study comparison table."""
    if "ablation" not in results:
        return None
    
    ablation = results["ablation"]["variants"]
    
    print("\n" + "="*100)
    print("TABLE 2: Ablation Study - Impact of Each Contribution")
    print("="*100)
    print()
    
    # Get full method baseline
    if "full" in ablation:
        full_results = ablation["full"]["results"]
        full_success = sum(full_results["success"]) / len(full_results["success"]) * 100
        full_path_success = [p for p, s in zip(full_results["path_length"], full_results["success"]) if s]
        full_avg_path = statistics.mean(full_path_success) if full_path_success else 0
    else:
        full_success = 0
        full_avg_path = 0
    
    print(f"{'Variant':<50} {'Success%':<12} {'Avg Path':<12} {'vs Full':<15}")
    print("-"*100)
    print(f"{'Full MR-QLearning (Baseline)':<50} {full_success:>10.1f}%  {full_avg_path:>10.1f}  {'-':<15}")
    
    for key, variant in ablation.items():
        if key == "full":
            continue
        
        results_data = variant["results"]
        success_list = results_data["success"]
        path_list = results_data["path_length"]
        
        success_rate = sum(success_list) / len(success_list) * 100
        path_success = [p for p, s in zip(path_list, success_list) if s]
        avg_path = statistics.mean(path_success) if path_success else 0
        
        success_diff = success_rate - full_success
        path_diff = avg_path - full_avg_path
        
        name = variant["name"][:48]
        vs_full = f"{success_diff:+.1f}%, {path_diff:+.1f}"
        
        print(f"{name:<50} {success_rate:>10.1f}%  {avg_path:>10.1f}  {vs_full:<15}")
    
    print("="*100)

def generate_density_table(results):
    """Generate obstacle density comparison table."""
    if "experiments" not in results:
        return None
    
    experiments = results["experiments"]["results"]
    densities = [10, 15, 20, 25]
    methods = ["astar", "hybrid", "mr_ql"]
    method_names = {"astar": "A*", "hybrid": "Hybrid", "mr_ql": "MR-QLearning"}
    
    print("\n" + "="*100)
    print("TABLE 3: Performance Across Obstacle Densities")
    print("="*100)
    print()
    print(f"{'Density':<12} {'A* Success':<15} {'Hybrid Success':<18} {'MR-QL Success':<18} {'Best Method':<15}")
    print("-"*100)
    
    for density in densities:
        key = f"density_{density}"
        if key not in experiments:
            continue
        
        row = [f"{density}%"]
        
        for method in methods:
            if method in experiments[key]:
                results_data = experiments[key][method]
                success_rate = sum(results_data["success"]) / len(results_data["success"]) * 100
                row.append(f"{success_rate:.1f}%")
            else:
                row.append("N/A")
        
        # Determine best
        if "astar" in experiments[key] and "hybrid" in experiments[key]:
            best = "A*, Hybrid" if sum(experiments[key]["astar"]["success"]) / len(experiments[key]["astar"]["success"]) >= 0.95 else "MR-QLearning"
        else:
            best = "N/A"
        row.append(best)
        
        print(f"{row[0]:<12} {row[1]:<15} {row[2]:<18} {row[3]:<18} {row[4]:<15}")
    
    print("="*100)

def generate_grid_size_table(results):
    """Generate grid size comparison table."""
    if "experiments" not in results:
        return None
    
    experiments = results["experiments"]["results"]
    grid_sizes = [15, 20, 25]
    methods = ["astar", "hybrid", "mr_ql"]
    method_names = {"astar": "A*", "hybrid": "Hybrid", "mr_ql": "MR-QLearning"}
    
    print("\n" + "="*100)
    print("TABLE 4: Scalability Analysis (Different Grid Sizes)")
    print("="*100)
    print()
    print(f"{'Grid Size':<12} {'A* Time':<15} {'Hybrid Time':<18} {'MR-QL Time':<18} {'A* Path':<12} {'Hybrid Path':<15}")
    print("-"*100)
    
    for size in grid_sizes:
        key = f"grid_{size}"
        if key not in experiments:
            continue
        
        row = [f"{size}×{size}"]
        
        for method in methods:
            if method in experiments[key]:
                results_data = experiments[key][method]
                time_avg = statistics.mean(results_data["time"])
                row.append(f"{time_avg:.3f}s")
            else:
                row.append("N/A")
        
        # Path lengths
        if "astar" in experiments[key]:
            path_success = [p for p, s in zip(experiments[key]["astar"]["path_length"], 
                                            experiments[key]["astar"]["success"]) if s]
            astar_path = statistics.mean(path_success) if path_success else 0
            row.append(f"{astar_path:.1f}")
        else:
            row.append("N/A")
        
        if "hybrid" in experiments[key]:
            path_success = [p for p, s in zip(experiments[key]["hybrid"]["path_length"], 
                                            experiments[key]["hybrid"]["success"]) if s]
            hybrid_path = statistics.mean(path_success) if path_success else 0
            row.append(f"{hybrid_path:.1f}")
        else:
            row.append("N/A")
        
        print(f"{row[0]:<12} {row[1]:<15} {row[2]:<18} {row[3]:<18} {row[4]:<12} {row[5]:<15}")
    
    print("="*100)

def main():
    """Generate all comparison tables."""
    print("="*100)
    print("GENERATING COMPARISON TABLES")
    print("="*100)
    
    results = load_results()
    
    if not results:
        print("No result files found. Run experiments first.")
        return
    
    generate_baseline_table(results)
    generate_ablation_table(results)
    generate_density_table(results)
    generate_grid_size_table(results)
    
    print("\n" + "="*100)
    print("ALL COMPARISON TABLES GENERATED")
    print("="*100)
    print("\nThese tables can be copied directly into your thesis.")
    print("="*100)

if __name__ == "__main__":
    main()

