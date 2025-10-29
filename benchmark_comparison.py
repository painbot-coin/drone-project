"""
Comprehensive Benchmarking Script
Compares your novel methods against recent state-of-the-art approaches.

Methods compared:
1. A* (baseline)
2. D* Lite (Koenig & Likhachev, 2002) - Dynamic replanning method
3. Double Q-Learning (van Hasselt, 2010/2016) - Recent RL method addressing overestimation bias
4. MR-QLearning (your novel RL method with experience replay, uncertainty quantification, etc.)
5. Hybrid A* + MR-QLearning (your novel hybrid with confidence-aware fallback)
6. Neural A* (Yonetani et al., 2021) - Learning-based pathfinding benchmark
7. Enhanced Hybrid A* + RL (novel enhanced approach with RL-guided heuristics, continuous learning, etc.)

Metrics collected:
- Success rate
- Path length
- Computation time
- Collisions (static + dynamic)
- Battery consumption
- Number of replanning events (for dynamic methods)
"""

import random
import time
import json
import os
from collections import defaultdict

# Import from your testing environment
from importlib import import_module
import sys

# Add the directory containing in testing environment.txt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import classes (assuming you rename the file or import directly)
# For now, we'll assume the classes are available
try:
    # Try importing if you convert to .py file
    exec(open('in testing environment.txt').read())
except:
    print("Note: Please ensure 'in testing environment.txt' is accessible or converted to .py")

class BenchmarkRunner:
    """
    Systematic benchmarking framework comparing all methods.
    """
    
    def __init__(self, num_trials=50, grid_size=20, obstacle_percent=0.15):
        self.num_trials = num_trials
        self.grid_size = grid_size
        self.obstacle_percent = obstacle_percent
        self.results = defaultdict(lambda: defaultdict(list))
        
    def generate_test_environment(self):
        """Generate a test environment."""
        env = Environment(self.grid_size)
        env.generate_obstacles()
        return env
    
    def run_method(self, method_name, env, moving_obstacles=False):
        """
        Run a single method on an environment and collect metrics.
        
        Returns:
            dict with metrics: success, path_length, time, collisions, battery
        """
        start_time = time.time()
        path = []
        success = False
        collisions = 0
        replanning_events = 0
        
        try:
            if method_name == "astar":
                astar = AStar(env.grid, env.start, env.goal)
                path = astar.search()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "dstar":
                dstar = DStarLite(env.grid, env.start, env.goal)
                path = dstar.search()
                success = len(path) > 0 and path[-1] == env.goal
                # D* Lite handles dynamic obstacles through replanning
                if moving_obstacles:
                    # Simulate dynamic obstacles and count replanning
                    current_pos = env.start
                    actual_path = [current_pos]
                    for step_idx in range(len(path)):
                        if step_idx < len(path):
                            next_pos = path[step_idx]
                            # Check if obstacle appeared
                            if env.grid[next_pos[0]][next_pos[1]] == 1:
                                replanning_events += 1
                                # Replan from current position
                                dstar.start = current_pos
                                dstar.replan([next_pos])
                                path = dstar.get_path()
                                if not path:
                                    break
                            actual_path.append(next_pos)
                            current_pos = next_pos
                    path = actual_path
                
            elif method_name == "rl":
                rl = MRQLearning(env.grid, env.start, env.goal, episodes=350)
                train_start = time.time()
                rl.train()
                train_time = time.time() - train_start
                path = rl.get_path(use_astar_fallback=False)
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "double_q":
                # Double Q-Learning: Recent published method (van Hasselt, 2010/2016)
                double_q = DoubleQLearning(env.grid, env.start, env.goal, episodes=350)
                train_start = time.time()
                double_q.train()
                train_time = time.time() - train_start
                path = double_q.get_path()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "hybrid":
                # Your novel hybrid method
                astar = AStar(env.grid, env.start, env.goal)
                global_path = astar.search()
                if not global_path:
                    return {"success": False, "path_length": 0, "time": 0, 
                           "collisions": 0, "battery": 0, "replanning_events": 0}
                
                # Simulate hybrid execution with dynamic obstacles
                actual_path = []
                current_pos = global_path[0]
                replanning_events = 0
                
                for i, planned_step in enumerate(global_path):
                    if moving_obstacles and env.grid[planned_step[0]][planned_step[1]] == 1:
                        # Dynamic obstacle detected - use RL locally
                        replanning_events += 1
                        rl = MRQLearning(env.grid, current_pos, env.goal, episodes=250)
                        rl.train()
                        local_path = rl.get_path(use_astar_fallback=True)
                        if local_path and local_path[0] == current_pos:
                            actual_path.extend(local_path[1:])
                            current_pos = local_path[-1]
                        else:
                            # Fallback to A*
                            astar = AStar(env.grid, current_pos, env.goal)
                            fallback_path = astar.search()
                            if fallback_path:
                                actual_path.extend(fallback_path[1:])
                                current_pos = fallback_path[-1]
                    else:
                        actual_path.append(planned_step)
                        current_pos = planned_step
                    
                    if current_pos == env.goal:
                        break
                
                path = actual_path
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "neural_astar":
                # Neural A*: Learning-based pathfinding benchmark
                neural_astar = NeuralAStar(env.grid, env.start, env.goal, episodes=200)
                train_start = time.time()
                neural_astar.train()
                train_time = time.time() - train_start
                path = neural_astar.search()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "enhanced_hybrid":
                # Enhanced Hybrid: Novel enhanced approach with multiple RL innovations
                # Real-time mode: Fast replanning using A* as primary, RL as enhancement
                enhanced = EnhancedHybrid(env.grid, env.start, env.goal, episodes=300, real_time_mode=True)
                train_start = time.time()
                enhanced.train()
                train_time = time.time() - train_start
                
                # Get initial path
                # Note: use_predictions=False because obstacles move randomly
                # Prediction only works with consistent movement patterns, not random movement
                initial_path = enhanced.search(use_predictions=False)
                
                if not initial_path:
                    return {"success": False, "path_length": 0, "time": 0, 
                           "collisions": 0, "battery": 0, "replanning_events": 0}
                
                # Execute with continuous learning
                path = enhanced.execute_with_continuous_learning(initial_path, moving_obstacles=moving_obstacles)
                success = len(path) > 0 and path[-1] == env.goal
                replanning_events = 0  # Counted internally in enhanced hybrid
                
        except Exception as e:
            print(f"Error running {method_name}: {e}")
            return {"success": False, "path_length": 0, "time": 0, 
                   "collisions": 0, "battery": 0, "replanning_events": 0}
        
        computation_time = time.time() - start_time
        path_length = len(path) if path else 0
        
        # Count collisions - properly validate bounds and exclude start/goal
        collisions = 0
        for step in path:
            # Exclude start and goal positions from collision counting
            if step == env.goal or step == env.start:
                continue
            # Validate bounds before accessing grid
            if (0 <= step[0] < len(env.grid) and 
                0 <= step[1] < len(env.grid[0])):
                if env.grid[step[0]][step[1]] == 1:
                    collisions += 1
        
        # Battery consumption (0.4% per step)
        battery_used = path_length * 0.4
        
        return {
            "success": success,
            "path_length": path_length,
            "time": computation_time,
            "collisions": collisions,
            "battery": battery_used,
            "replanning_events": replanning_events
        }
    
    def run_benchmark(self, moving_obstacles=False):
        """
        Run full benchmark suite.
        
        Args:
            moving_obstacles: If True, test with dynamic obstacles
        """
        methods = ["astar", "dstar", "double_q", "rl", "hybrid", "neural_astar", "enhanced_hybrid"]
        
        print(f"\n{'='*60}")
        print(f"BENCHMARKING: {self.num_trials} trials")
        print(f"Moving Obstacles: {moving_obstacles}")
        print(f"{'='*60}\n")
        
        for trial in range(self.num_trials):
            if (trial + 1) % 10 == 0:
                print(f"Trial {trial + 1}/{self.num_trials}...")
            
            env = self.generate_test_environment()
            
            for method in methods:
                metrics = self.run_method(method, env, moving_obstacles)
                
                # Store results
                self.results[method]["success"].append(metrics["success"])
                self.results[method]["path_length"].append(metrics["path_length"])
                self.results[method]["time"].append(metrics["time"])
                self.results[method]["collisions"].append(metrics["collisions"])
                self.results[method]["battery"].append(metrics["battery"])
                self.results[method]["replanning_events"].append(metrics["replanning_events"])
        
        self.print_results()
        self.save_results(moving_obstacles)
    
    def print_results(self):
        """Print summary statistics."""
        print(f"\n{'='*80}")
        print("BENCHMARK RESULTS SUMMARY")
        print(f"{'='*80}\n")
        
        methods = ["astar", "dstar", "double_q", "rl", "hybrid", "neural_astar", "enhanced_hybrid"]
        method_names = {
            "astar": "A* (Baseline)",
            "dstar": "D* Lite (Koenig & Likhachev, 2002)",
            "double_q": "Double Q-Learning (van Hasselt, 2010/2016)",
            "rl": "MR-QLearning (Your Novel RL)",
            "hybrid": "Hybrid A* + MR-QL (Your Novel Hybrid)",
            "neural_astar": "Neural A* (Yonetani et al., 2021)",
            "enhanced_hybrid": "Enhanced Hybrid A* + RL (Novel Enhanced)"
        }
        
        for method in methods:
            name = method_names[method]
            results = self.results[method]
            
            success_rate = sum(results["success"]) / len(results["success"]) * 100
            avg_path_length = sum(results["path_length"]) / len(results["path_length"])
            avg_time = sum(results["time"]) / len(results["time"])
            avg_collisions = sum(results["collisions"]) / len(results["collisions"])
            avg_battery = sum(results["battery"]) / len(results["battery"])
            avg_replanning = sum(results["replanning_events"]) / len(results["replanning_events"])
            
            print(f"\n{name}:")
            print(f"  Success Rate: {success_rate:.2f}%")
            print(f"  Avg Path Length: {avg_path_length:.2f} steps")
            print(f"  Avg Computation Time: {avg_time:.4f} seconds")
            print(f"  Avg Collisions: {avg_collisions:.2f}")
            print(f"  Avg Battery Used: {avg_battery:.2f}%")
            if method in ["dstar", "hybrid", "enhanced_hybrid"]:
                print(f"  Avg Replanning Events: {avg_replanning:.2f}")
        
        print(f"\n{'='*80}\n")
    
    def save_results(self, moving_obstacles=False):
        """Save results to JSON file."""
        output_file = f"benchmark_results_{'dynamic' if moving_obstacles else 'static'}.json"
        
        # Convert defaultdict to regular dict for JSON serialization
        results_dict = {}
        for method, metrics in self.results.items():
            results_dict[method] = {}
            for metric, values in metrics.items():
                results_dict[method][metric] = values
        
        with open(output_file, 'w') as f:
            json.dump({
                "num_trials": self.num_trials,
                "moving_obstacles": moving_obstacles,
                "results": results_dict
            }, f, indent=2)
        
        print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPREHENSIVE BENCHMARKING FRAMEWORK")
    print("Comparing All 7 Methods: A*, D* Lite, Double Q-Learning, MR-QLearning, Hybrid, Neural A*, Enhanced Hybrid")
    print("="*80)
    
    # Run benchmarks with all 7 methods
    # Using 30 trials for faster execution (can increase to 50 for final results)
    benchmark = BenchmarkRunner(num_trials=30, grid_size=20, obstacle_percent=0.15)
    
    # Static obstacles
    print("\n>>> Running benchmark with STATIC obstacles (all 7 methods)...")
    benchmark.run_benchmark(moving_obstacles=False)
    
    # Note: Dynamic obstacles can be tested separately if needed
    # print("\n>>> Running benchmark with DYNAMIC obstacles...")
    # benchmark.run_benchmark(moving_obstacles=True)
    
    print("\n✓ Benchmarking complete with all 7 methods!")

