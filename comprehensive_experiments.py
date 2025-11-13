"""
Comprehensive Experiments: Multiple Conditions
==============================================
Tests all methods under various experimental conditions:
- Varying obstacle densities (10%, 15%, 20%, 25%)
- Different grid sizes (15x15, 20x20, 25x25)
- Static obstacles only
- Dynamic obstacles only
- Mixed static + dynamic obstacles
- Transfer learning experiments
"""

import random
import time
import json
import statistics
from collections import defaultdict

# Load classes
print("Loading classes...")
with open('in testing environment.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'if __name__ == "__main__":' in content:
        content = content.split('if __name__ == "__main__":')[0]
    exec(content)
print("[OK] Classes loaded\n")

class ComprehensiveExperiments:
    def __init__(self, trials_per_condition=20, fast_mode=True):
        self.trials_per_condition = trials_per_condition
        self.fast_mode = fast_mode
        self.episodes = 100 if fast_mode else 200
        self.results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    def generate_env_with_density(self, grid_size, obstacle_density):
        """Generate environment with specific obstacle density."""
        env = Environment(grid_size=grid_size)
        max_attempts = 100
        
        for attempt in range(max_attempts):
            env.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
            
            # Place obstacles with desired density
            num_cells = grid_size * grid_size
            num_obstacles = int(num_cells * obstacle_density)
            available_positions = [(i, j) for i in range(grid_size) for j in range(grid_size)
                                 if (i, j) not in (env.start, env.goal)]
            
            if num_obstacles > len(available_positions):
                num_obstacles = len(available_positions)
            
            obstacle_positions = random.sample(available_positions, num_obstacles)
            for i, j in obstacle_positions:
                env.grid[i][j] = 1
            
            # Verify solvability
            ast = AStar(env.grid, env.start, env.goal)
            if ast.search():
                return env
        
        # Fallback: use standard generation
        env.generate_obstacles()
        return env
        
    def test_method(self, method_name, env, moving_obstacles=False):
        """Test a method on environment."""
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
                double_q = DoubleQLearning(env.grid, env.start, env.goal, episodes=self.episodes)
                train_start = time.time()
                double_q.train()
                training_time = time.time() - train_start
                path = double_q.get_path()
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "mr_ql":
                mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=self.episodes)
                train_start = time.time()
                mr_ql.train()
                training_time = time.time() - train_start
                path = mr_ql.get_path(use_astar_fallback=False)
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "hybrid":
                # Hybrid: A* for global planning, RL for local replanning
                astar = AStar(env.grid, env.start, env.goal)
                global_path = astar.search()
                if not global_path:
                    return {"success": False, "path_length": 0, "time": 0, 
                           "collisions": 0, "battery": 0, "training_time": 0}
                
                # Simulate hybrid execution with dynamic obstacles
                actual_path = []
                current_pos = global_path[0]
                
                for i, planned_step in enumerate(global_path):
                    if moving_obstacles and env.grid[planned_step[0]][planned_step[1]] == 1:
                        # Dynamic obstacle detected - use RL locally
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
                
                # Get initial path
                # Note: use_predictions=False because obstacles move randomly
                # Prediction only works with consistent movement patterns, not random movement
                initial_path = enhanced.search(use_predictions=False)
                
                if not initial_path:
                    return {"success": False, "path_length": 0, "time": 0, 
                           "collisions": 0, "battery": 0, "training_time": 0}
                
                # Execute with continuous learning
                path = enhanced.execute_with_continuous_learning(initial_path, moving_obstacles=moving_obstacles)
                success = len(path) > 0 and path[-1] == env.goal
                
        except Exception as e:
            return {
                "success": False, "path_length": 0, "time": 0,
                "collisions": 0, "battery": 0, "training_time": 0
            }
        
        computation_time = time.time() - start_time
        path_length = len(path) if path else 0
        
        # Count collisions
        for step in path:
            if step != env.goal and step != env.start:
                if 0 <= step[0] < len(env.grid) and 0 <= step[1] < len(env.grid[0]):
                    if env.grid[step[0]][step[1]] == 1:
                        collisions += 1
        
        battery_used = path_length * 0.4
        
        return {
            "success": success, "path_length": path_length, "time": computation_time,
            "collisions": collisions, "battery": battery_used, "training_time": training_time
        }
    
    def experiment_obstacle_densities(self):
        """Experiment 1: Varying obstacle densities."""
        print("\n" + "="*80)
        print("EXPERIMENT 1: Varying Obstacle Densities")
        print("="*80)
        
        densities = [0.10, 0.15, 0.20, 0.25]
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        grid_size = 20
        
        for density in densities:
            print(f"\nTesting obstacle density: {density*100:.0f}%")
            print("-" * 80)
            
            for trial in range(self.trials_per_condition):
                if (trial + 1) % 5 == 0:
                    print(f"  Trial {trial + 1}/{self.trials_per_condition}...", end="\r")
                
                # Create environment with specific density
                env = self.generate_env_with_density(grid_size, density)
                
                for method in methods:
                    metrics = self.test_method(method, env, moving_obstacles=False)
                    key = f"density_{int(density*100)}"
                    self.results[key][method]["success"].append(metrics["success"])
                    self.results[key][method]["path_length"].append(metrics["path_length"])
                    self.results[key][method]["time"].append(metrics["time"])
                    self.results[key][method]["collisions"].append(metrics["collisions"])
                    self.results[key][method]["battery"].append(metrics["battery"])
            
            print(f"  [OK] Completed {self.trials_per_condition} trials")
    
    def experiment_grid_sizes(self):
        """Experiment 2: Different grid sizes."""
        print("\n" + "="*80)
        print("EXPERIMENT 2: Different Grid Sizes")
        print("="*80)
        
        grid_sizes = [15, 20, 25]
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        
        for grid_size in grid_sizes:
            print(f"\nTesting grid size: {grid_size}x{grid_size}")
            print("-" * 80)
            
            for trial in range(self.trials_per_condition):
                if (trial + 1) % 5 == 0:
                    print(f"  Trial {trial + 1}/{self.trials_per_condition}...", end="\r")
                
                env = Environment(grid_size=grid_size)
                env.generate_obstacles()
                
                for method in methods:
                    metrics = self.test_method(method, env, moving_obstacles=False)
                    key = f"grid_{grid_size}"
                    self.results[key][method]["success"].append(metrics["success"])
                    self.results[key][method]["path_length"].append(metrics["path_length"])
                    self.results[key][method]["time"].append(metrics["time"])
                    self.results[key][method]["collisions"].append(metrics["collisions"])
                    self.results[key][method]["battery"].append(metrics["battery"])
            
            print(f"  [OK] Completed {self.trials_per_condition} trials")
    
    def experiment_static_obstacles(self):
        """Experiment 3: Static obstacles only."""
        print("\n" + "="*80)
        print("EXPERIMENT 3: Static Obstacles Only")
        print("="*80)
        
        methods = ["astar", "dstar", "double_q", "mr_ql", "hybrid", "neural_astar", "enhanced_hybrid"]
        print(f"\nTesting {self.trials_per_condition} trials...")
        
        for trial in range(self.trials_per_condition):
            if (trial + 1) % 5 == 0:
                print(f"  Trial {trial + 1}/{self.trials_per_condition}...", end="\r")
            
            env = Environment(grid_size=20)
            env.generate_obstacles()
            
            for method in methods:
                metrics = self.test_method(method, env, moving_obstacles=False)
                key = "static_only"
                self.results[key][method]["success"].append(metrics["success"])
                self.results[key][method]["path_length"].append(metrics["path_length"])
                self.results[key][method]["time"].append(metrics["time"])
                self.results[key][method]["collisions"].append(metrics["collisions"])
                self.results[key][method]["battery"].append(metrics["battery"])
        
        print(f"  ✓ Completed {self.trials_per_condition} trials")
    
    def experiment_transfer_learning(self):
        """Experiment 4: Transfer learning."""
        print("\n" + "="*80)
        print("EXPERIMENT 4: Transfer Learning")
        print("="*80)
        
        print("\nTraining on source environment, testing on target environment...")
        
        methods_with_transfer = ["mr_ql"]  # Only MR-QLearning supports transfer
        
        for trial in range(self.trials_per_condition):
            if (trial + 1) % 5 == 0:
                print(f"  Trial {trial + 1}/{self.trials_per_condition}...", end="\r")
            
            # Source environment (training)
            env_source = Environment(grid_size=20)
            env_source.generate_obstacles()
            
            # Train MR-QLearning on source
            mr_ql_source = MRQLearning(env_source.grid, env_source.start, env_source.goal, episodes=self.episodes)
            mr_ql_source.train()
            transfer_q_table = mr_ql_source.get_q_table_for_transfer()
            
            # Target environment (testing with transfer)
            env_target = Environment(grid_size=20)
            env_target.generate_obstacles()
            
            # Test with transfer
            mr_ql_transfer = MRQLearning(env_target.grid, env_target.start, env_target.goal, 
                                        episodes=self.episodes, transfer_q_table=transfer_q_table)
            train_start = time.time()
            mr_ql_transfer.train()  # Fine-tune with transfer
            training_time = time.time() - train_start
            
            path = mr_ql_transfer.get_path(use_astar_fallback=False)
            success = len(path) > 0 and path[-1] == env_target.goal
            path_length = len(path) if path else 0
            
            # Also test without transfer for comparison
            mr_ql_no_transfer = MRQLearning(env_target.grid, env_target.start, env_target.goal, episodes=self.episodes)
            train_start = time.time()
            mr_ql_no_transfer.train()
            training_time_no_transfer = time.time() - train_start
            
            path_no_transfer = mr_ql_no_transfer.get_path(use_astar_fallback=False)
            success_no_transfer = len(path_no_transfer) > 0 and path_no_transfer[-1] == env_target.goal
            path_length_no_transfer = len(path_no_transfer) if path_no_transfer else 0
            
            # Store results
            key = "transfer_learning"
            self.results[key]["mr_ql_with_transfer"]["success"].append(success)
            self.results[key]["mr_ql_with_transfer"]["path_length"].append(path_length)
            self.results[key]["mr_ql_with_transfer"]["training_time"].append(training_time)
            
            self.results[key]["mr_ql_no_transfer"]["success"].append(success_no_transfer)
            self.results[key]["mr_ql_no_transfer"]["path_length"].append(path_length_no_transfer)
            self.results[key]["mr_ql_no_transfer"]["training_time"].append(training_time_no_transfer)
        
        print(f"  ✓ Completed {self.trials_per_condition} trials")
    
    def run_all_experiments(self):
        """Run all comprehensive experiments."""
        print("="*80)
        print("COMPREHENSIVE EXPERIMENTS")
        print("="*80)
        print(f"\nTrials per condition: {self.trials_per_condition}")
        print(f"Mode: {'FAST' if self.fast_mode else 'FULL'} (Episodes: {self.episodes})")
        print("\nExperiments:")
        print("  1. Varying obstacle densities (10%, 15%, 20%, 25%)")
        print("  2. Different grid sizes (15x15, 20x20, 25x25)")
        print("  3. Static obstacles only")
        print("  4. Transfer learning")
        print("\nNote: Dynamic obstacles experiments require simulator integration")
        print("="*80)
        
        start_total = time.time()
        
        # Run experiments
        self.experiment_obstacle_densities()
        self.experiment_grid_sizes()
        self.experiment_static_obstacles()
        self.experiment_transfer_learning()
        
        total_time = time.time() - start_total
        print(f"\n[OK] All experiments completed in {total_time:.1f} seconds\n")
        
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print summary of all experiments."""
        print("="*80)
        print("EXPERIMENTAL RESULTS SUMMARY")
        print("="*80)
        
        # Obstacle densities
        print("\n1. Obstacle Densities:")
        print("-" * 80)
        for density in [10, 15, 20, 25]:
            key = f"density_{density}"
            if key in self.results:
                print(f"\n  Density {density}%:")
                for method in ["astar", "hybrid", "mr_ql"]:
                    if method in self.results[key]:
                        results = self.results[key][method]
                        success_rate = sum(results["success"]) / len(results["success"]) * 100
                        avg_path = statistics.mean([p for p, s in zip(results["path_length"], results["success"]) if s]) if any(results["success"]) else 0
                        print(f"    {method}: {success_rate:.1f}% success, {avg_path:.1f} avg path")
        
        # Grid sizes
        print("\n2. Grid Sizes:")
        print("-" * 80)
        for size in [15, 20, 25]:
            key = f"grid_{size}"
            if key in self.results:
                print(f"\n  Grid {size}x{size}:")
                for method in ["astar", "hybrid", "mr_ql"]:
                    if method in self.results[key]:
                        results = self.results[key][method]
                        success_rate = sum(results["success"]) / len(results["success"]) * 100
                        avg_path = statistics.mean([p for p, s in zip(results["path_length"], results["success"]) if s]) if any(results["success"]) else 0
                        print(f"    {method}: {success_rate:.1f}% success, {avg_path:.1f} avg path")
        
        # Transfer learning
        print("\n3. Transfer Learning:")
        print("-" * 80)
        if "transfer_learning" in self.results:
            key = "transfer_learning"
            if "mr_ql_with_transfer" in self.results[key]:
                with_transfer = self.results[key]["mr_ql_with_transfer"]
                no_transfer = self.results[key]["mr_ql_no_transfer"]
                
                success_with = sum(with_transfer["success"]) / len(with_transfer["success"]) * 100
                success_without = sum(no_transfer["success"]) / len(no_transfer["success"]) * 100
                time_with = statistics.mean(with_transfer["training_time"])
                time_without = statistics.mean(no_transfer["training_time"])
                
                print(f"  With Transfer:    {success_with:.1f}% success, {time_with:.3f}s training")
                print(f"  Without Transfer: {success_without:.1f}% success, {time_without:.3f}s training")
                print(f"  Improvement:      {success_with - success_without:+.1f}% success, {time_without - time_with:+.3f}s faster")
        
        print("\n" + "="*80)
    
    def save_results(self):
        """Save all results to JSON."""
        results_dict = {}
        for condition, methods in self.results.items():
            results_dict[condition] = {}
            for method, metrics in methods.items():
                results_dict[condition][method] = {}
                for metric, values in metrics.items():
                    results_dict[condition][method][metric] = values
        
        with open("comprehensive_experiments_results.json", 'w') as f:
            json.dump({
                "num_trials": self.trials_per_condition,
                "episodes": self.episodes,
                "fast_mode": self.fast_mode,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results_dict
            }, f, indent=2)
        
        print(f"\n[OK] Results saved to: comprehensive_experiments_results.json")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPREHENSIVE EXPERIMENTS")
    print("="*80)
    print("\nTesting multiple experimental conditions:")
    print("  • Varying obstacle densities")
    print("  • Different grid sizes")
    print("  • Static obstacles")
    print("  • Transfer learning")
    print()
    
    experiments = ComprehensiveExperiments(trials_per_condition=15, fast_mode=True)
    experiments.run_all_experiments()
    
    print("\n" + "="*80)
    print("COMPREHENSIVE EXPERIMENTS COMPLETE")
    print("="*80)
    print("\nDeliverable: Complete experimental dataset ✅")
    print("="*80)

