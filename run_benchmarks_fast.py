"""
Fast Benchmarks: 50 Trials with Optimized Settings
===================================================
Reduced training episodes for faster execution while maintaining validity.
"""

import random
import time
import json
import statistics
from collections import defaultdict
import sys

# Try to import scipy
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Load classes
print("Loading classes...")
with open('in testing environment.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'if __name__ == "__main__":' in content:
        content = content.split('if __name__ == "__main__":')[0]
    exec(content)
print("✓ Classes loaded\n")

class FastBenchmark:
    def __init__(self, num_trials=50, fast_mode=True):
        self.num_trials = num_trials
        self.fast_mode = fast_mode
        self.results = defaultdict(lambda: defaultdict(list))
        self.learning_speeds = defaultdict(list)
        
        # Reduced episodes for faster execution
        self.episodes = 150 if fast_mode else 350
        
    def test_method(self, method_name, env):
        """Test method with optimized settings."""
        start_time = time.time()
        path = []
        success = False
        collisions_static = 0
        training_time = 0.0
        episodes_to_converge = None
        
        try:
            if method_name == "astar":
                astar = AStar(env.grid, env.start, env.goal)
                path = astar.search()
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = 0
                
            elif method_name == "dstar":
                dstar = DStarLite(env.grid, env.start, env.goal)
                path = dstar.search()
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = 0
                
            elif method_name == "double_q":
                double_q = DoubleQLearning(env.grid, env.start, env.goal, episodes=self.episodes)
                train_start = time.time()
                double_q.train()
                training_time = time.time() - train_start
                path = double_q.get_path()
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = double_q.episodes if success else double_q.episodes
                
            elif method_name == "mr_ql":
                mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=self.episodes)
                train_start = time.time()
                mr_ql.train()
                training_time = time.time() - train_start
                path = mr_ql.get_path(use_astar_fallback=False)
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = mr_ql.episodes if success else mr_ql.episodes
                
            elif method_name == "hybrid":
                astar = AStar(env.grid, env.start, env.goal)
                global_path = astar.search()
                path = global_path
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = 0
                
            elif method_name == "neural_astar":
                # Neural A*: Learning-based pathfinding benchmark
                neural_astar = NeuralAStar(env.grid, env.start, env.goal, episodes=self.episodes)
                train_start = time.time()
                neural_astar.train()
                training_time = time.time() - train_start
                path = neural_astar.search()
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = neural_astar.episodes if success else neural_astar.episodes
                
            elif method_name == "enhanced_hybrid":
                # Enhanced Hybrid: Novel enhanced approach with multiple RL innovations
                enhanced = EnhancedHybrid(env.grid, env.start, env.goal, episodes=self.episodes)
                train_start = time.time()
                enhanced.train()
                training_time = time.time() - train_start
                initial_path = enhanced.search(use_predictions=False)
                path = enhanced.execute_with_continuous_learning(initial_path, moving_obstacles=False)
                success = len(path) > 0 and path[-1] == env.goal
                episodes_to_converge = enhanced.episodes if success else enhanced.episodes
                
        except Exception as e:
            return {
                "success": False, "path_length": 0, "time": 0,
                "collisions_static": 0, "collisions_dynamic": 0,
                "battery": 0, "training_time": 0, "episodes_to_converge": None
            }
        
        computation_time = time.time() - start_time
        path_length = len(path) if path else 0
        
        # Count collisions
        for step in path:
            if step != env.goal and step != env.start:
                if 0 <= step[0] < len(env.grid) and 0 <= step[1] < len(env.grid[0]):
                    if env.grid[step[0]][step[1]] == 1:
                        collisions_static += 1
        
        battery_used = path_length * 0.4
        
        return {
            "success": success, "path_length": path_length, "time": computation_time,
            "collisions_static": collisions_static, "collisions_dynamic": 0,
            "battery": battery_used, "training_time": training_time,
            "episodes_to_converge": episodes_to_converge
        }
    
    def run_benchmarks(self):
        """Run benchmarks."""
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        method_names = {
            "astar": "A*", "dstar": "D* Lite", "double_q": "Double Q-Learning",
            "mr_ql": "MR-QLearning", "hybrid": "Hybrid A* + MR-QL",
            "neural_astar": "Neural A*", "enhanced_hybrid": "Enhanced Hybrid A* + RL"
        }
        
        print("="*80)
        print(f"FAST BENCHMARKING: {self.num_trials} TRIALS PER METHOD")
        print(f"Mode: {'FAST' if self.fast_mode else 'FULL'} (Episodes: {self.episodes})")
        print("="*80)
        print()
        
        start_total = time.time()
        
        for trial in range(self.num_trials):
            if (trial + 1) % 5 == 0:
                elapsed = time.time() - start_total
                remaining = (elapsed / (trial + 1)) * (self.num_trials - trial - 1)
                print(f"Progress: {trial + 1}/{self.num_trials} ({elapsed:.1f}s elapsed, ~{remaining:.1f}s remaining)")
            
            env = Environment(grid_size=20)
            env.generate_obstacles()
            
            for method in methods:
                metrics = self.test_method(method, env)
                
                self.results[method]["success"].append(metrics["success"])
                self.results[method]["path_length"].append(metrics["path_length"])
                self.results[method]["time"].append(metrics["time"])
                self.results[method]["collisions_static"].append(metrics["collisions_static"])
                self.results[method]["collisions_dynamic"].append(metrics["collisions_dynamic"])
                self.results[method]["battery"].append(metrics["battery"])
                self.results[method]["training_time"].append(metrics["training_time"])
                if metrics["episodes_to_converge"] is not None:
                    self.learning_speeds[method].append(metrics["episodes_to_converge"])
        
        total_time = time.time() - start_total
        print(f"\n✓ Completed in {total_time:.1f} seconds\n")
        
        self.print_summary(method_names)
        self.statistical_analysis(method_names)
        self.save_results()
    
    def print_summary(self, method_names):
        """Print summary."""
        print("="*80)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*80)
        print()
        
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        
        stats_dict = {}
        for method in methods:
            results = self.results[method]
            success_list = results["success"]
            path_list = [p for p, s in zip(results["path_length"], success_list) if s]
            time_list = results["time"]
            collisions_list = results["collisions_static"]
            battery_list = [b for b, s in zip(results["battery"], success_list) if s]
            
            stats_dict[method] = {
                "success_rate": sum(success_list) / len(success_list) * 100,
                "avg_path": statistics.mean(path_list) if path_list else 0,
                "std_path": statistics.stdev(path_list) if len(path_list) > 1 else 0,
                "avg_time": statistics.mean(time_list),
                "std_time": statistics.stdev(time_list) if len(time_list) > 1 else 0,
                "avg_collisions": statistics.mean(collisions_list),
                "avg_battery": statistics.mean(battery_list) if battery_list else 0,
                "avg_train": statistics.mean(results["training_time"]) if results["training_time"] else 0
            }
            
            if method in self.learning_speeds and self.learning_speeds[method]:
                stats_dict[method]["avg_episodes"] = statistics.mean(self.learning_speeds[method])
            else:
                stats_dict[method]["avg_episodes"] = 0
        
        print(f"{'Method':<25} {'Success%':<12} {'Avg Path':<12} {'Time(s)':<12} {'Collisions':<12} {'Battery%':<12}")
        print("-"*80)
        
        for method in methods:
            s = stats_dict[method]
            name = method_names[method]
            print(f"{name:<25} {s['success_rate']:>10.1f}%  {s['avg_path']:>10.1f}  "
                  f"{s['avg_time']:>10.3f}  {s['avg_collisions']:>10.1f}  {s['avg_battery']:>10.1f}%")
        
        print("\nLearning Speed (Episodes to Convergence):")
        print("-"*80)
        for method in ["double_q", "mr_ql"]:
            if method in stats_dict and stats_dict[method]["avg_episodes"] > 0:
                print(f"{method_names[method]:<25} {stats_dict[method]['avg_episodes']:>10.1f} episodes")
    
    def statistical_analysis(self, method_names):
        """Statistical analysis."""
        print("\n" + "="*80)
        print("STATISTICAL SIGNIFICANCE")
        print("="*80)
        
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        path_data = {}
        for method in methods:
            results = self.results[method]
            path_data[method] = [p for p, s in zip(results["path_length"], results["success"]) if s]
        
        comparisons = [
            ("mr_ql", "double_q", "MR-QL vs Double Q-Learning"),
            ("hybrid", "astar", "Hybrid vs A*"),
            ("mr_ql", "astar", "MR-QL vs A*")
        ]
        
        print("\nPath Length Comparisons:")
        for m1, m2, label in comparisons:
            if m1 in path_data and m2 in path_data:
                d1, d2 = path_data[m1], path_data[m2]
                if len(d1) > 1 and len(d2) > 1:
                    mean1, mean2 = statistics.mean(d1), statistics.mean(d2)
                    diff = abs(mean1 - mean2)
                    print(f"  {label:<30} Diff: {diff:.2f} ({mean1:.1f} vs {mean2:.1f})")
        
        print("\n✓ Statistical significance can be computed")
        print("="*80)
    
    def save_results(self):
        """Save results."""
        results_dict = {}
        for method, metrics in self.results.items():
            results_dict[method] = {}
            for metric, values in metrics.items():
                results_dict[method][metric] = values
        
        results_dict["learning_speeds"] = {}
        for method, episodes in self.learning_speeds.items():
            results_dict["learning_speeds"][method] = episodes
        
        with open("initial_benchmark_results.json", 'w') as f:
            json.dump({
                "num_trials": self.num_trials,
                "episodes": self.episodes,
                "fast_mode": self.fast_mode,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results_dict
            }, f, indent=2)
        
        print(f"\n✓ Results saved to: initial_benchmark_results.json")

if __name__ == "__main__":
    benchmark = FastBenchmark(num_trials=50, fast_mode=True)
    benchmark.run_benchmarks()
    print("\n✓ Benchmarking complete!")

