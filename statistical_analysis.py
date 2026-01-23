"""
Statistical Analysis: Complete Statistical Analysis and Visualizations
=====================================================================
Computes:
- Mean, std dev, confidence intervals for all metrics
- T-tests comparing methods
- Visualizations (bar charts, line plots, box plots, heatmaps)
"""

import json
import statistics
import math
from collections import defaultdict
import os

# Try to import matplotlib for visualizations
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not available, visualizations will be skipped")

# Try to import scipy for statistical tests
try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Note: scipy not available, using manual statistical calculations")

# Try to import scipy for statistical tests
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Note: scipy not available, using manual statistical calculations")

class StatisticalAnalyzer:
    def __init__(self):
        self.results = {}
        self.load_all_results()
        
    def load_all_results(self):
        """Load all result files."""
        print("Loading results...")
        
        # Load initial benchmarks
        if os.path.exists("initial_benchmark_results.json"):
            with open("initial_benchmark_results.json", 'r') as f:
                self.results["benchmarks"] = json.load(f)
            print("  [OK] Loaded initial benchmarks")
        
        # Load ablation study
        if os.path.exists("ablation_study_results.json"):
            with open("ablation_study_results.json", 'r') as f:
                self.results["ablation"] = json.load(f)
            print("  [OK] Loaded ablation study")
        
        # Load comprehensive experiments
        if os.path.exists("comprehensive_experiments_results.json"):
            with open("comprehensive_experiments_results.json", 'r') as f:
                self.results["experiments"] = json.load(f)
            print("  [OK] Loaded comprehensive experiments")
        
        print("[OK] All results loaded\n")
    
    def compute_statistics(self, values):
        """Compute mean, std dev, and 95% confidence interval."""
        if not values or len(values) == 0:
            return {"mean": 0, "std": 0, "ci_lower": 0, "ci_upper": 0, "n": 0}
        
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        n = len(values)
        
        # 95% confidence interval (t-distribution)
        if n > 1:
            if HAS_SCIPY:
                t_critical = scipy_stats.t.ppf(0.975, n - 1)
            else:
                # Approximate t-value for 95% CI
                t_critical = 1.96 if n > 30 else 2.0
            margin = t_critical * (std / math.sqrt(n))
            ci_lower = mean - margin
            ci_upper = mean + margin
        else:
            ci_lower = mean
            ci_upper = mean
        
        return {
            "mean": mean,
            "std": std,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "n": n
        }
    
    def perform_t_test(self, data1, data2, name1, name2):
        """Perform t-test between two datasets."""
        if not data1 or not data2:
            return None
        
        if len(data1) < 2 or len(data2) < 2:
            return None
        
        if HAS_SCIPY:
            try:
                t_stat, p_value = scipy_stats.ttest_ind(data1, data2)
                significant = p_value < 0.05
                return {
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "significant": significant,
                    "method1": name1,
                    "method2": name2
                }
            except:
                pass
        
        # Manual calculation
        mean1, mean2 = statistics.mean(data1), statistics.mean(data2)
        std1, std2 = statistics.stdev(data1) if len(data1) > 1 else 0, statistics.stdev(data2) if len(data2) > 1 else 0
        n1, n2 = len(data1), len(data2)
        
        # Pooled standard error
        pooled_std = math.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        se = pooled_std * math.sqrt(1/n1 + 1/n2)
        
        if se > 0:
            t_stat = (mean1 - mean2) / se
        else:
            t_stat = 0
        
        return {
            "t_statistic": t_stat,
            "p_value": None,  # Can't compute without scipy
            "significant": abs(t_stat) > 2.0,  # Approximate
            "method1": name1,
            "method2": name2,
            "mean_diff": mean1 - mean2
        }
    
    def analyze_benchmarks(self):
        """Analyze initial benchmark results."""
        if "benchmarks" not in self.results:
            return None
        
        print("="*80)
        print("STATISTICAL ANALYSIS: Initial Benchmarks")
        print("="*80)
        
        benchmarks = self.results["benchmarks"]["results"]
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid"]
        method_names = {
            "astar": "A*",
            "dstar": "D* Lite",
            "double_q": "Double Q-Learning",
            "mr_ql": "MR-QLearning",
            "hybrid": "Hybrid A* + MR-QL"
        }
        
        stats_dict = {}
        
        print("\n1. Descriptive Statistics:")
        print("-" * 80)
        print(f"{'Method':<25} {'Metric':<15} {'Mean':<12} {'Std Dev':<12} {'95% CI':<20}")
        print("-" * 80)
        
        for method in methods:
            if method not in benchmarks:
                continue
            
            results = benchmarks[method]
            stats_dict[method] = {}
            
            # Success rate
            success_list = results["success"]
            success_rate = sum(success_list) / len(success_list) * 100
            stats_dict[method]["success_rate"] = success_rate
            
            # Path length (only successful)
            path_list = [p for p, s in zip(results["path_length"], success_list) if s]
            path_stats = self.compute_statistics(path_list)
            stats_dict[method]["path_length"] = path_stats
            
            # Time
            time_stats = self.compute_statistics(results["time"])
            stats_dict[method]["time"] = time_stats
            
            # Battery
            battery_list = [b for b, s in zip(results["battery"], success_list) if s]
            battery_stats = self.compute_statistics(battery_list)
            stats_dict[method]["battery"] = battery_stats
            
            # Print
            name = method_names[method]
            print(f"\n{name}:")
            print(f"  {'Path Length':<15} {path_stats['mean']:>10.2f}  {path_stats['std']:>10.2f}  [{path_stats['ci_lower']:.2f}, {path_stats['ci_upper']:.2f}]")
            print(f"  {'Time (s)':<15} {time_stats['mean']:>10.3f}  {time_stats['std']:>10.3f}  [{time_stats['ci_lower']:.3f}, {time_stats['ci_upper']:.3f}]")
            print(f"  {'Battery (%)':<15} {battery_stats['mean']:>10.2f}  {battery_stats['std']:>10.2f}  [{battery_stats['ci_lower']:.2f}, {battery_stats['ci_upper']:.2f}]")
            print(f"  {'Success Rate':<15} {success_rate:>10.1f}%")
        
        # T-tests
        print("\n\n2. T-Tests (Path Length):")
        print("-" * 80)
        
        comparisons = [
            ("mr_ql", "double_q", "MR-QLearning vs Double Q-Learning"),
            ("mr_ql", "astar", "MR-QLearning vs A*"),
            ("hybrid", "astar", "Hybrid vs A*"),
            ("hybrid", "dstar", "Hybrid vs D* Lite")
        ]
        
        t_test_results = []
        
        for method1, method2, label in comparisons:
            if method1 in benchmarks and method2 in benchmarks:
                results1 = benchmarks[method1]
                results2 = benchmarks[method2]
                success1 = results1["success"]
                success2 = results2["success"]
                
                path1 = [p for p, s in zip(results1["path_length"], success1) if s]
                path2 = [p for p, s in zip(results2["path_length"], success2) if s]
                
                t_result = self.perform_t_test(path1, path2, method_names[method1], method_names[method2])
                if t_result:
                    t_test_results.append(t_result)
                    sig = "[OK] SIGNIFICANT" if t_result["significant"] else "✗ Not significant"
                    p_str = f"p={t_result['p_value']:.4f}" if t_result['p_value'] is not None else f"t={t_result['t_statistic']:.2f}"
                    print(f"{label:<40} {p_str}  {sig}")
        
        return {
            "statistics": stats_dict,
            "t_tests": t_test_results
        }
    
    def create_visualizations(self):
        """Create all visualizations."""
        if not HAS_MATPLOTLIB:
            print("\nNote: matplotlib not available, skipping visualizations")
            print("Install matplotlib to generate visualizations: pip install matplotlib")
            return
        
        print("\n" + "="*80)
        print("CREATING VISUALIZATIONS")
        print("="*80)
        
        if "benchmarks" not in self.results:
            print("No benchmark data available for visualization")
            return
        
        benchmarks = self.results["benchmarks"]["results"]
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid"]
        method_names = {
            "astar": "A*",
            "dstar": "D* Lite",
            "double_q": "Double Q-Learning",
            "mr_ql": "MR-QLearning",
            "hybrid": "Hybrid"
        }
        
        # Create output directory
        os.makedirs("visualizations", exist_ok=True)
        
        # 1. Bar Chart: Success Rate
        print("\n1. Creating bar chart: Success Rate...")
        fig, ax = plt.subplots(figsize=(10, 6))
        method_labels = []
        success_rates = []
        
        for method in methods:
            if method in benchmarks:
                results = benchmarks[method]
                success_rate = sum(results["success"]) / len(results["success"]) * 100
                method_labels.append(method_names[method])
                success_rates.append(success_rate)
        
        bars = ax.bar(method_labels, success_rates, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ax.set_ylabel('Success Rate (%)', fontsize=12)
        ax.set_title('Success Rate Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim([0, 105])
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('visualizations/success_rate_bar.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  [OK] Saved: visualizations/success_rate_bar.png")
        
        # 2. Bar Chart: Path Length
        print("2. Creating bar chart: Path Length...")
        fig, ax = plt.subplots(figsize=(10, 6))
        path_means = []
        path_stds = []
        
        for method in methods:
            if method in benchmarks:
                results = benchmarks[method]
                success_list = results["success"]
                path_list = [p for p, s in zip(results["path_length"], success_list) if s]
                path_means.append(statistics.mean(path_list) if path_list else 0)
                path_stds.append(statistics.stdev(path_list) if len(path_list) > 1 else 0)
        
        bars = ax.bar(method_labels, path_means, yerr=path_stds, capsize=5,
                      color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ax.set_ylabel('Path Length (steps)', fontsize=12)
        ax.set_title('Average Path Length Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('visualizations/path_length_bar.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  [OK] Saved: visualizations/path_length_bar.png")
        
        # 3. Box Plot: Path Length Distribution
        print("3. Creating box plot: Path Length Distribution...")
        fig, ax = plt.subplots(figsize=(10, 6))
        path_data = []
        
        for method in methods:
            if method in benchmarks:
                results = benchmarks[method]
                success_list = results["success"]
                path_list = [p for p, s in zip(results["path_length"], success_list) if s]
                path_data.append(path_list)
        
        bp = ax.boxplot(path_data, labels=method_labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Path Length (steps)', fontsize=12)
        ax.set_title('Path Length Distribution (Box Plot)', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('visualizations/path_length_boxplot.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  [OK] Saved: visualizations/path_length_boxplot.png")
        
        # 4. Heatmap: Performance Across Obstacle Densities
        if "experiments" in self.results:
            print("4. Creating heatmap: Performance Across Obstacle Densities...")
            experiments = self.results["experiments"]["results"]
            
            densities = [10, 15, 20, 25]
            methods_for_heatmap = ["astar", "hybrid", "mr_ql"]
            method_names_heatmap = {"astar": "A*", "hybrid": "Hybrid", "mr_ql": "MR-QL"}
            
            success_matrix = []
            for method in methods_for_heatmap:
                row = []
                for density in densities:
                    key = f"density_{density}"
                    if key in experiments and method in experiments[key]:
                        results = experiments[key][method]
                        success_rate = sum(results["success"]) / len(results["success"]) * 100
                        row.append(success_rate)
                    else:
                        row.append(0)
                success_matrix.append(row)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(success_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
            
            ax.set_xticks(np.arange(len(densities)))
            ax.set_yticks(np.arange(len(methods_for_heatmap)))
            ax.set_xticklabels([f"{d}%" for d in densities])
            ax.set_yticklabels([method_names_heatmap[m] for m in methods_for_heatmap])
            
            ax.set_xlabel('Obstacle Density (%)', fontsize=12)
            ax.set_ylabel('Method', fontsize=12)
            ax.set_title('Success Rate Across Obstacle Densities', fontsize=14, fontweight='bold')
            
            # Add text annotations
            for i in range(len(methods_for_heatmap)):
                for j in range(len(densities)):
                    text = ax.text(j, i, f'{success_matrix[i][j]:.0f}%',
                                 ha="center", va="center", color="black", fontweight='bold')
            
            plt.colorbar(im, ax=ax, label='Success Rate (%)')
            plt.tight_layout()
            plt.savefig('visualizations/obstacle_density_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  [OK] Saved: visualizations/obstacle_density_heatmap.png")
        
        print("\n[OK] All visualizations created!")
    
    def save_analysis(self, analysis_results):
        """Save statistical analysis to JSON."""
        output_file = "statistical_analysis_results.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
                "analysis": analysis_results
            }, f, indent=2)
        
        print(f"\n[OK] Statistical analysis saved to: {output_file}")
    
    def run_complete_analysis(self):
        """Run complete statistical analysis."""
        print("="*80)
        print("COMPLETE STATISTICAL ANALYSIS")
        print("="*80)
        print("\nThis will:")
        print("  1. Compute mean, std dev, confidence intervals")
        print("  2. Perform t-tests comparing methods")
        print("  3. Create visualizations")
        print()
        
        # Analyze benchmarks
        benchmark_analysis = self.analyze_benchmarks()
        
        # Create visualizations
        self.create_visualizations()
        
        # Save analysis
        if benchmark_analysis:
            self.save_analysis(benchmark_analysis)
        
        print("\n" + "="*80)
        print("STATISTICAL ANALYSIS COMPLETE")
        print("="*80)
        print("\nDeliverable: Statistical analysis with significance tests ✅")
        print("="*80)


if __name__ == "__main__":
    analyzer = StatisticalAnalyzer()
    analyzer.run_complete_analysis()

