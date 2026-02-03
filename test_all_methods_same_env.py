"""
Test All Methods on Same Environments
======================================
This script ensures all methods are tested on IDENTICAL environments
for fair comparison. Each method runs on the same grid configuration.

Methods tested:
1. A* (baseline)
2. D* Lite (dynamic replanning)
3. Double Q-Learning (recent RL method)
4. MR-QLearning (your novel RL method)
5. Hybrid A* + MR-QL (your novel hybrid)
"""

import random
import time
import json
import os
from collections import defaultdict

# Import all classes from testing environment
# Read the file and execute only the class definitions (skip GUI code)
with open('in testing environment.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    # Execute only up to the main execution part
    # Split at the main execution to avoid running GUI
    if 'if __name__ == "__main__":' in content:
        content = content.split('if __name__ == "__main__":')[0]
    exec(content)

class SameEnvironmentTester:
    """
    Tests all methods on identical environments for fair comparison.
    """
    
    def __init__(self, num_trials=20, grid_size=20, obstacle_percent=0.15):
        self.num_trials = num_trials
        self.grid_size = grid_size
        self.obstacle_percent = obstacle_percent
        self.results = defaultdict(lambda: defaultdict(list))
        
    def generate_test_environment(self):
        """Generate a single test environment."""
        env = Environment(self.grid_size)
        env.generate_obstacles()
        return env
    
    def test_method(self, method_name, env, moving_obstacles=False):
        """
        Test a single method on the given environment.
        
        Returns:
            dict with metrics: success, path_length, time, collisions, battery, training_time
        """
        start_time = time.time()
        path = []
        success = False
        collisions = 0
        training_time = 0.0
        
        try:
            if method_name == "astar":
                astar = AStar(env.grid, env.start, env.goal)
                path = astar.search()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "dstar":
                dstar = DStarLite(env.grid, env.start, env.goal)
                path = dstar.search()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "double_q":
                double_q = DoubleQLearning(env.grid, env.start, env.goal, episodes=350)
                train_start = time.time()
                double_q.train()
                training_time = time.time() - train_start
                path = double_q.get_path()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "mr_ql":
                # Your novel MR-QLearning
                mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=350)
                train_start = time.time()
                mr_ql.train()
                training_time = time.time() - train_start
                path = mr_ql.get_path(use_astar_fallback=False)
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "hybrid":
                # Your novel hybrid method: A* for global planning, RL for local replanning
                astar = AStar(env.grid, env.start, env.goal)
                global_path = astar.search()
                if not global_path:
                    return {"success": False, "path_length": 0, "time": 0, 
                           "collisions": 0, "battery": 0, "training_time": 0}
                
                # Simulate hybrid execution with dynamic obstacles
                actual_path = []
                current_pos = global_path[0]
                replanning_events = 0
                
                for i, planned_step in enumerate(global_path):
                    if moving_obstacles and env.grid[planned_step[0]][planned_step[1]] == 1:
                        # Dynamic obstacle detected - use RL locally
                        replanning_events += 1
                        rl = MRQLearning(env.grid, current_pos, env.goal, episodes=250)
                        train_start = time.time()
                        rl.train()
                        training_time += time.time() - train_start
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
                training_time = time.time() - train_start
                path = neural_astar.search()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "enhanced_hybrid":
                # Enhanced Hybrid: Novel enhanced approach with multiple RL innovations
                # Real-time mode: Fast replanning using A* as primary, RL as enhancement
                enhanced = EnhancedHybrid(env.grid, env.start, env.goal, episodes=300, real_time_mode=True)
                train_start = time.time()
                enhanced.train()
                training_time = time.time() - train_start
                # Note: use_predictions=False because obstacles move randomly
                # Prediction only works with consistent movement patterns, not random movement
                initial_path = enhanced.search(use_predictions=False)
                if not initial_path:
                    return {"success": False, "path_length": 0, "time": 0, 
                           "collisions": 0, "battery": 0, "training_time": 0}
                path = enhanced.execute_with_continuous_learning(initial_path, moving_obstacles=moving_obstacles)
                success = len(path) > 0 and path[-1] == env.goal
                
        except Exception as e:
            print(f"Error running {method_name}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "path_length": 0, "time": 0, 
                   "collisions": 0, "battery": 0, "training_time": 0}
        
        computation_time = time.time() - start_time
        path_length = len(path) if path else 0
        
        # Count collisions (check if path goes through obstacles)
        collisions = 0
        for step in path:
            if step != env.goal and step != env.start:
                if 0 <= step[0] < len(env.grid) and 0 <= step[1] < len(env.grid[0]):
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
            "training_time": training_time
        }
    
    def run_comparison(self, moving_obstacles=False):
        """
        Run all methods on the SAME environments.
        This ensures fair comparison.
        """
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        method_names = {
            "astar": "A* (Baseline)",
            "dstar": "D* Lite (2002)",
            "double_q": "Double Q-Learning (2010/2016)",
            "mr_ql": "MR-QLearning (Your Novel)",
            "hybrid": "Hybrid A* + MR-QL (Your Novel)",
            "neural_astar": "Neural A* (Yonetani et al. 2021)",
            "enhanced_hybrid": "Enhanced Hybrid A* + RL (Novel Enhanced)"
        }
        
        print("\n" + "="*80)
        print("TESTING ALL METHODS ON SAME ENVIRONMENTS")
        print("="*80)
        print(f"Number of trials: {self.num_trials}")
        print(f"Grid size: {self.grid_size}x{self.grid_size}")
        print(f"Obstacle percent: {self.obstacle_percent*100}%")
        print(f"Moving obstacles: {moving_obstacles}")
        print("="*80 + "\n")
        
        # Store environments for each trial
        trial_environments = []
        
        for trial in range(self.num_trials):
            print(f"Trial {trial + 1}/{self.num_trials}...", end=" ")
            
            # Generate ONE environment for this trial
            env = self.generate_test_environment()
            trial_environments.append(env)
            
            # Test ALL methods on the SAME environment
            for method in methods:
                metrics = self.test_method(method, env, moving_obstacles)
                
                # Store results
                self.results[method]["success"].append(metrics["success"])
                self.results[method]["path_length"].append(metrics["path_length"])
                self.results[method]["time"].append(metrics["time"])
                self.results[method]["collisions"].append(metrics["collisions"])
                self.results[method]["battery"].append(metrics["battery"])
                self.results[method]["training_time"].append(metrics["training_time"])
            
            print("✓")
        
        # Print summary statistics
        self.print_summary(method_names)
        
        # Save results
        self.save_results(moving_obstacles)
        
        return self.results
    
    def print_summary(self, method_names):
        """Print summary statistics for all methods."""
        print("\n" + "="*80)
        print("RESULTS SUMMARY - ALL METHODS ON SAME ENVIRONMENTS")
        print("="*80)
        
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        
        # Calculate statistics
        stats = {}
        for method in methods:
            results = self.results[method]
            stats[method] = {
                "success_rate": sum(results["success"]) / len(results["success"]) * 100,
                "avg_path_length": sum(results["path_length"]) / len(results["path_length"]),
                "avg_time": sum(results["time"]) / len(results["time"]),
                "avg_collisions": sum(results["collisions"]) / len(results["collisions"]),
                "avg_battery": sum(results["battery"]) / len(results["battery"]),
                "avg_training_time": sum(results["training_time"]) / len(results["training_time"]),
                "std_path_length": self._std_dev(results["path_length"]),
                "std_time": self._std_dev(results["time"])
            }
        
        # Print table
        print(f"\n{'Method':<35} {'Success%':<12} {'Path Len':<12} {'Time(s)':<12} {'Collisions':<12} {'Battery%':<12}")
        print("-" * 80)
        
        for method in methods:
            s = stats[method]
            name = method_names[method]
            print(f"{name:<35} {s['success_rate']:>10.1f}%  {s['avg_path_length']:>10.1f}  "
                  f"{s['avg_time']:>10.3f}  {s['avg_collisions']:>10.1f}  {s['avg_battery']:>10.1f}%")
        
        # Print training times for RL methods
        print("\n" + "-" * 80)
        print("Training Times (RL methods only):")
        print("-" * 80)
        for method in ["double_q", "mr_ql"]:
            s = stats[method]
            name = method_names[method]
            print(f"{name:<35} {s['avg_training_time']:>10.3f}s")
        
        # Best performers
        print("\n" + "-" * 80)
        print("Best Performers:")
        print("-" * 80)
        
        best_success = max(methods, key=lambda m: stats[m]["success_rate"])
        best_path = min([m for m in methods if stats[m]["success_rate"] > 0], 
                      key=lambda m: stats[m]["avg_path_length"], default=None)
        best_time = min(methods, key=lambda m: stats[m]["avg_time"])
        best_battery = min([m for m in methods if stats[m]["success_rate"] > 0],
                          key=lambda m: stats[m]["avg_battery"], default=None)
        
        print(f"Highest Success Rate: {method_names[best_success]} ({stats[best_success]['success_rate']:.1f}%)")
        if best_path:
            print(f"Shortest Path: {method_names[best_path]} ({stats[best_path]['avg_path_length']:.1f} steps)")
        print(f"Fastest Computation: {method_names[best_time]} ({stats[best_time]['avg_time']:.3f}s)")
        if best_battery:
            print(f"Best Battery: {method_names[best_battery]} ({stats[best_battery]['avg_battery']:.1f}%)")
        
        print("\n" + "="*80 + "\n")
    
    def _std_dev(self, values):
        """Calculate standard deviation."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def save_results(self, moving_obstacles=False):
        """Save results to JSON file."""
        output_file = f"same_env_results_{'dynamic' if moving_obstacles else 'static'}.json"
        
        # Convert defaultdict to regular dict
        results_dict = {}
        for method, metrics in self.results.items():
            results_dict[method] = {}
            for metric, values in metrics.items():
                results_dict[method][metric] = values
        
        with open(output_file, 'w') as f:
            json.dump({
                "num_trials": self.num_trials,
                "grid_size": self.grid_size,
                "obstacle_percent": self.obstacle_percent,
                "moving_obstacles": moving_obstacles,
                "results": results_dict
            }, f, indent=2)
        
        print(f"Results saved to: {output_file}")


def main():
    """Main function to run tests."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TESTING: ALL METHODS ON SAME ENVIRONMENTS")
    print("="*80)
    print("\nThis ensures fair comparison by testing all methods")
    print("on IDENTICAL environment instances.\n")
    
    # Create tester
    tester = SameEnvironmentTester(
        num_trials=20,  # Adjust as needed
        grid_size=20,
        obstacle_percent=0.15
    )
    
    # Test with static obstacles
    print("\n>>> Testing with STATIC obstacles...")
    tester.run_comparison(moving_obstacles=False)
    
    # Optionally test with dynamic obstacles
    # Uncomment if you want to test dynamic obstacles too
    # print("\n>>> Testing with DYNAMIC obstacles...")
    # tester_dynamic = SameEnvironmentTester(
    #     num_trials=20,
    #     grid_size=20,
    #     obstacle_percent=0.15
    # )
    # tester_dynamic.run_comparison(moving_obstacles=True)
    
    print("\nTesting complete!")
    print("\nKey Points:")
    print("✓ All methods tested on SAME environments")
    print("✓ Fair comparison ensured")
    print("✓ Results saved to JSON files")
    print("✓ Ready for statistical analysis")


if __name__ == "__main__":
    main()

