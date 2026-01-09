"""
Improved Benchmark with Static vs Dynamic Collision Tracking
============================================================
Updates benchmark_comparison.py to properly track static and dynamic collisions.
"""

import random
import time
import json
import os
import sys
from collections import defaultdict

# Import from your testing environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with open('in testing environment.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'if __name__ == "__main__":' in content:
        content = content.split('if __name__ == "__main__":')[0]
    exec(content)

def move_obstacles_simple(env, moving_list):
    """Simple obstacle movement simulation."""
    new_moving_list = []
    for x, y in moving_list:
        # Clear old position
        if 0 <= x < len(env.grid) and 0 <= y < len(env.grid[0]):
            env.grid[x][y] = 0
        
        # Move in random direction
        dx, dy = random.choice([(0,1), (1,0), (-1,0), (0,-1)])
        nx, ny = x + dx, y + dy
        
        # Check bounds and validity
        if (0 <= nx < len(env.grid) and 0 <= ny < len(env.grid[0]) and
            (nx, ny) not in (env.start, env.goal) and env.grid[nx][ny] == 0):
            env.grid[nx][ny] = 1
            new_moving_list.append((nx, ny))
        else:
            # Stay in place
            if 0 <= x < len(env.grid) and 0 <= y < len(env.grid[0]):
                env.grid[x][y] = 1
                new_moving_list.append((x, y))
    
    return new_moving_list

class ImprovedBenchmarkRunner:
    """Benchmark runner with proper static vs dynamic collision tracking."""
    
    def __init__(self, num_trials=30, grid_size=20, obstacle_percent=0.15):
        self.num_trials = num_trials
        self.grid_size = grid_size
        self.obstacle_percent = obstacle_percent
        self.results = defaultdict(lambda: defaultdict(list))
    
    def run_method_with_collision_tracking(self, method_name, env, moving_obstacles=False):
        """Run method with proper static vs dynamic collision tracking."""
        start_time = time.time()
        path = []
        success = False
        collisions_static = 0
        collisions_dynamic = 0
        replanning_events = 0
        
        # Store initial static obstacles
        initial_static_obstacles = set()
        for i in range(len(env.grid)):
            for j in range(len(env.grid[0])):
                if env.grid[i][j] == 1:
                    initial_static_obstacles.add((i, j))
        
        # Create moving obstacles list (10% of static obstacles move)
        moving_list = []
        if moving_obstacles:
            for pos in initial_static_obstacles:
                if random.random() < 0.1:  # 10% of obstacles move
                    moving_list.append(pos)
        
        try:
            if method_name == "astar":
                astar = AStar(env.grid, env.start, env.goal)
                path = astar.search()
                
                # Simulate execution with moving obstacles
                if moving_obstacles and path:
                    actual_path = [path[0]]
                    current_pos = path[0]
                    env_copy = [row[:] for row in env.grid]
                    
                    for planned_step in path[1:]:
                        # Move obstacles
                        moving_list = move_obstacles_simple(env, moving_list)
                        
                        # Check for collision
                        if env.grid[planned_step[0]][planned_step[1]] == 1:
                            if planned_step in initial_static_obstacles:
                                collisions_static += 1
                            else:
                                collisions_dynamic += 1
                            
                            # A* replans from current position
                            astar = AStar(env.grid, current_pos, env.goal)
                            new_path = astar.search()
                            if not new_path:
                                success = False
                                break
                            path = [current_pos] + new_path[1:]
                            continue
                        
                        actual_path.append(planned_step)
                        current_pos = planned_step
                        if current_pos == env.goal:
                            break
                    
                    path = actual_path
                
                success = len(path) > 0 and path[-1] == env.goal
                
            elif method_name == "dstar":
                dstar = DStarLite(env.grid, env.start, env.goal)
                path = dstar.search()
                
                if moving_obstacles and path:
                    actual_path = [path[0]]
                    current_pos = path[0]
                    
                    for planned_step in path[1:]:
                        # Move obstacles
                        moving_list = move_obstacles_simple(env, moving_list)
                        
                        # Check for collision
                        if env.grid[planned_step[0]][planned_step[1]] == 1:
                            if planned_step in initial_static_obstacles:
                                collisions_static += 1
                            else:
                                collisions_dynamic += 1
                            
                            replanning_events += 1
                            dstar.start = current_pos
                            dstar.replan([planned_step])
                            new_path = dstar.get_path()
                            if not new_path:
                                success = False
                                break
                            path = [current_pos] + new_path[1:]
                            continue
                        
                        actual_path.append(planned_step)
                        current_pos = planned_step
                        if current_pos == env.goal:
                            break
                    
                    path = actual_path
                
                success = len(path) > 0 and path[-1] == env.goal
            
            elif method_name == "enhanced_hybrid":
                enhanced = EnhancedHybrid(env.grid, env.start, env.goal, episodes=300, real_time_mode=True)
                train_start = time.time()
                enhanced.train()
                train_time = time.time() - train_start
                
                initial_path = enhanced.search(use_predictions=False)
                
                if not initial_path:
                    return {"success": False, "path_length": 0, "time": 0,
                           "collisions_static": 0, "collisions_dynamic": 0,
                           "battery": 0, "replanning_events": 0}
                
                # Execute with continuous learning
                path = enhanced.execute_with_continuous_learning(initial_path, moving_obstacles=moving_obstacles)
                success = len(path) > 0 and path[-1] == env.goal
                
                # Count collisions during execution
                if moving_obstacles and path:
                    env_copy = [row[:] for row in env.grid]
                    for step in path:
                        if step != env.goal and step != env.start:
                            if (0 <= step[0] < len(env.grid) and 
                                0 <= step[1] < len(env.grid[0])):
                                if env.grid[step[0]][step[1]] == 1:
                                    if step in initial_static_obstacles:
                                collisions_static += 1
                            else:
                                collisions_dynamic += 1
            
        except Exception as e:
            print(f"Error running {method_name}: {e}")
            return {"success": False, "path_length": 0, "time": 0,
                "collisions_static": 0, "collisions_dynamic": 0,
                   "battery": 0, "replanning_events": 0}
        
        computation_time = time.time() - start_time
        path_length = len(path) if path else 0
        battery_used = path_length * 0.4
        
        return {
            "success": success,
            "path_length": path_length,
            "time": computation_time,
            "collisions_static": collisions_static,
            "collisions_dynamic": collisions_dynamic,
            "battery": battery_used,
            "replanning_events": replanning_events
        }

    def run_benchmark(self, moving_obstacles=False):
        """Run full benchmark with collision tracking."""
        methods = ["astar", "dstar", "enhanced_hybrid"]
        
        print(f"\n{'='*60}")
        print(f"IMPROVED BENCHMARK: {self.num_trials} trials")
        print(f"Moving Obstacles: {moving_obstacles}")
        print(f"Tracking: Static vs Dynamic Collisions")
        print(f"{'='*60}\n")
        
        for trial in range(self.num_trials):
            if (trial + 1) % 10 == 0:
                print(f"Trial {trial + 1}/{self.num_trials}...")
            
            env = Environment(grid_size=self.grid_size)
            env.generate_obstacles()
            
            for method in methods:
                metrics = self.run_method_with_collision_tracking(method, env, moving_obstacles)
                
                self.results[method]["success"].append(metrics["success"])
                self.results[method]["path_length"].append(metrics["path_length"])
                self.results[method]["time"].append(metrics["time"])
                self.results[method]["collisions_static"].append(metrics["collisions_static"])
                self.results[method]["collisions_dynamic"].append(metrics["collisions_dynamic"])
                self.results[method]["battery"].append(metrics["battery"])
                self.results[method]["replanning_events"].append(metrics["replanning_events"])
        
        self.save_results(moving_obstacles)
        self.print_results()
    
    def print_results(self):
        """Print summary with collision breakdown."""
        print(f"\n{'='*80}")
        print("IMPROVED BENCHMARK RESULTS - Collision Breakdown")
        print(f"{'='*80}\n")
        
        method_names = {
            "astar": "A*",
            "dstar": "D* Lite",
            "enhanced_hybrid": "Enhanced Hybrid"
        }
        
        for method, name in method_names.items():
            results = self.results[method]
            if not results["success"]:
                continue
            
            success_rate = (sum(results["success"]) / len(results["success"])) * 100
            avg_path = sum(results["path_length"]) / len(results["path_length"])
            avg_time = sum(results["time"]) / len(results["time"])
            avg_collisions_static = sum(results["collisions_static"]) / len(results["collisions_static"])
            avg_collisions_dynamic = sum(results["collisions_dynamic"]) / len(results["collisions_dynamic"])
            total_collisions = avg_collisions_static + avg_collisions_dynamic
            
            print(f"{name}:")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Avg Path Length: {avg_path:.1f} steps")
            print(f"  Avg Time: {avg_time:.3f}s")
            print(f"  Collisions - Static: {avg_collisions_static:.2f}, Dynamic: {avg_collisions_dynamic:.2f}, Total: {total_collisions:.2f}")
            print()
    
    def save_results(self, moving_obstacles=False):
        """Save results to JSON."""
        output_file = f"improved_benchmark_results_{'dynamic' if moving_obstacles else 'static'}.json"
        
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
    benchmark = ImprovedBenchmarkRunner(num_trials=30, grid_size=20, obstacle_percent=0.15)
    benchmark.run_benchmark(moving_obstacles=True)
