"""
Ablation Study: Multi-Level RL Policies
========================================
Tests Enhanced Hybrid with and without multi-level RL to evaluate the impact
of hierarchical RL policies (4th RL innovation).

Variants:
1. Enhanced Hybrid WITH Multi-Level RL (Full - current implementation)
2. Enhanced Hybrid WITHOUT Multi-Level RL (Single RL agent only)
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

class EnhancedHybridNoMultiLevel:
    """Enhanced Hybrid WITHOUT multi-level RL - uses single RL agent only."""
    
    def __init__(self, grid, start, goal, episodes=300, real_time_mode=True):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.episodes = episodes
        self.real_time_mode = real_time_mode
        
        # Single RL agent (no multi-level)
        rl_episodes = 50 if real_time_mode else episodes
        self.rl_agent = MRQLearning(grid, start, goal, episodes=rl_episodes)
        
        # RL-guided heuristic
        self.rl_guided_heuristic = {}
        
        # Obstacle prediction
        self.obstacle_history = []
        self.obstacle_prediction = {}
        
        # Path refinement buffer
        self.path_refinement_buffer = []
    
    def rl_guided_heuristic_value(self, node, battery_remaining=100.0, terrain_difficulty=0.0):
        """RL-guided heuristic (same as Enhanced Hybrid)."""
        base_h = abs(node[0] - self.goal[0]) + abs(node[1] - self.goal[1])
        
        # RL adjustment
        if node in self.rl_agent.q_table:
            q_values = self.rl_agent.q_table[node]
            if q_values:
                max_q = max(q_values.values())
                h_adjust = -max_q * 0.05
                base_h += h_adjust
        
        # Battery-aware adjustment
        if battery_remaining < 30.0:
            base_h *= 2.0
        elif battery_remaining < 50.0:
            base_h *= 1.3
        
        # Terrain difficulty adjustment
        terrain_factor = 1.0 + terrain_difficulty * 0.5
        base_h *= terrain_factor
        
        return base_h
    
    def astar_with_rl_heuristic(self, start, goal, use_predictions=False,
                                 battery_remaining=100.0, terrain_difficulty_map=None):
        """A* search using RL-guided heuristic."""
        import heapq
        
        open_heap = []
        start_terrain = terrain_difficulty_map.get(start, 0.0) if terrain_difficulty_map else 0.0
        start_h = self.rl_guided_heuristic_value(start, battery_remaining, start_terrain)
        heapq.heappush(open_heap, (start_h, 0, start))
        came_from = {}
        g_score = {start: 0}
        closed_set = set()
        
        # Get predicted obstacles if requested
        predicted_obstacles = set()
        if use_predictions:
            predicted_obstacles = self.predict_obstacle_movement(start)
        
        while open_heap:
            f, g, current = heapq.heappop(open_heap)
            
            if current in closed_set:
                continue
            closed_set.add(current)
            
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            for di, dj in [(0,1), (1,0), (0,-1), (-1,0)]:
                neighbor = (current[0] + di, current[1] + dj)
                
                if (neighbor[0] < 0 or neighbor[0] >= len(self.grid) or
                    neighbor[1] < 0 or neighbor[1] >= len(self.grid[0])):
                    continue
                
                if neighbor in closed_set:
                    continue
                
                if neighbor in predicted_obstacles:
                    continue
                
                if self.grid[neighbor[0]][neighbor[1]] == 1:
                    continue
                
                # Battery-aware cost
                step_cost = 1.0
                if battery_remaining < 30.0:
                    step_cost = 1.5
                elif battery_remaining < 50.0:
                    step_cost = 1.2
                
                neighbor_terrain = terrain_difficulty_map.get(neighbor, 0.0) if terrain_difficulty_map else 0.0
                step_cost += neighbor_terrain * 0.3
                
                tentative_g = g_score[current] + step_cost
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = self.rl_guided_heuristic_value(neighbor, battery_remaining, neighbor_terrain)
                    f_score = tentative_g + h
                    heapq.heappush(open_heap, (f_score, tentative_g, neighbor))
        
        return []
    
    def predict_obstacle_movement(self, current_pos, lookahead=3):
        """Obstacle prediction (same as Enhanced Hybrid)."""
        predicted_obstacles = set()
        
        if len(self.obstacle_history) < 3:
            return predicted_obstacles
        
        obstacle_directions = {}
        
        for i in range(len(self.obstacle_history) - 1):
            current_obs = self.obstacle_history[i + 1]
            prev_obs = self.obstacle_history[i]
            
            for pos in current_obs:
                if pos not in prev_obs:
                    for prev_pos in prev_obs:
                        if prev_pos not in current_obs:
                            dx = pos[0] - prev_pos[0]
                            dy = pos[1] - prev_pos[1]
                            direction = (dx, dy)
                            
                            key = prev_pos
                            if key not in obstacle_directions:
                                obstacle_directions[key] = []
                            obstacle_directions[key].append((direction, pos))
        
        for key, movements in obstacle_directions.items():
            if len(movements) >= 2:
                first_dir = movements[0][0]
                all_same_direction = all(m[0] == first_dir for m in movements)
                
                if all_same_direction:
                    latest_pos = movements[-1][1]
                    dx, dy = first_dir
                    
                    for step in range(1, lookahead + 1):
                        predicted = (latest_pos[0] + dx * step, latest_pos[1] + dy * step)
                        if (0 <= predicted[0] < len(self.grid) and 
                            0 <= predicted[1] < len(self.grid)):
                            predicted_obstacles.add(predicted)
        
        return predicted_obstacles
    
    def search(self, use_predictions=False, battery_remaining=100.0, terrain_difficulty_map=None):
        """Search using RL-guided A* (same as Enhanced Hybrid)."""
        return self.astar_with_rl_heuristic(
            self.start, self.goal,
            use_predictions=use_predictions,
            battery_remaining=battery_remaining,
            terrain_difficulty_map=terrain_difficulty_map
        )
    
    def execute_with_continuous_learning(self, path, moving_obstacles=False):
        """Execute path with continuous learning - WITHOUT multi-level RL."""
        if not path:
            return []
        
        actual_path = []
        current_pos = path[0]
        battery_remaining = 100.0
        
        for i, planned_step in enumerate(path[1:], 1):
            # Check if step is blocked
            if self.grid[planned_step[0]][planned_step[1]] == 1:
                # WITHOUT multi-level RL: Use single RL agent for replanning
                if self.real_time_mode:
                    # Real-time: Use A* directly (fast)
                    ast = AStar(self.grid, current_pos, self.goal)
                    astar_path = ast.search()
                    if astar_path and len(astar_path) > 1:
                        actual_path.extend(astar_path[1:])
                        current_pos = astar_path[-1]
                        i = len(path)
                        continue
                    else:
                        break
                else:
                    # Non-real-time: Use single RL agent (no multi-level)
                    self.rl_agent.start = current_pos
                    self.rl_agent.train()  # Single agent training
                    local_path = self.rl_agent.get_path(max_steps=50, use_astar_fallback=True)
                    
                    if local_path and local_path[0] == current_pos and len(local_path) > 1:
                        actual_path.extend(local_path[1:])
                        current_pos = local_path[-1]
                        i = len(path)
                        continue
                    else:
                        ast = AStar(self.grid, current_pos, self.goal)
                        fallback_path = ast.search()
                        if fallback_path:
                            actual_path.extend(fallback_path[1:])
                            current_pos = fallback_path[-1]
                            i = len(path)
                            continue
                        else:
                            break
            
            actual_path.append(planned_step)
            current_pos = planned_step
            
            # Continuous learning (every 5 steps)
            if i % 5 == 0 and current_pos in self.rl_agent.q_table:
                prev_pos = actual_path[-2] if len(actual_path) >= 2 else path[0]
                reward = self.rl_agent.shaped_reward(prev_pos, current_pos)
                self.rl_agent.update_q(prev_pos, current_pos, reward, current_pos)
            
            if current_pos == self.goal:
                break
        
        return [path[0]] + actual_path
    
    def train(self):
        """Train the single RL agent."""
        self.rl_agent.train()
        
        # Update RL-guided heuristic
        for state in self.rl_agent.q_table:
            q_values = self.rl_agent.q_table[state]
            if q_values:
                max_q = max(q_values.values())
                self.rl_guided_heuristic[state] = -max_q * 0.05

class MultiLevelRLAblationStudy:
    """Ablation study for multi-level RL policies."""
    
    def __init__(self, num_trials=20, grid_size=20, obstacle_percent=0.15):
        self.num_trials = num_trials
        self.grid_size = grid_size
        self.obstacle_percent = obstacle_percent
        self.results = defaultdict(lambda: defaultdict(list))
    
    def test_variant(self, variant_name, use_multi_level=True, moving_obstacles=False):
        """Test a variant of Enhanced Hybrid."""
        env = Environment(grid_size=self.grid_size)
        env.generate_obstacles()
        
        start_time = time.time()
        
        try:
            if use_multi_level:
                # WITH multi-level RL (full Enhanced Hybrid)
                enhanced = EnhancedHybrid(env.grid, env.start, env.goal, episodes=300, real_time_mode=True)
            else:
                # WITHOUT multi-level RL (single RL agent)
                enhanced = EnhancedHybridNoMultiLevel(env.grid, env.start, env.goal, episodes=300, real_time_mode=True)
            
            train_start = time.time()
            enhanced.train()
            training_time = time.time() - train_start
            
            initial_path = enhanced.search(use_predictions=False)
            
            if not initial_path:
                return {
                    "success": False, "path_length": 0, "time": 0,
                    "training_time": 0, "collisions": 0, "battery": 0
                }
            
            # Execute with continuous learning
            path = enhanced.execute_with_continuous_learning(initial_path, moving_obstacles=moving_obstacles)
            success = len(path) > 0 and path[-1] == env.goal
            
            computation_time = time.time() - start_time
            path_length = len(path) if path else 0
            
            # Count collisions
            collisions = 0
            for step in path:
                if step != env.goal and step != env.start:
                    if (0 <= step[0] < len(env.grid) and 
                        0 <= step[1] < len(env.grid[0])):
                        if env.grid[step[0]][step[1]] == 1:
                            collisions += 1
            
            battery_used = path_length * 0.4
            
            return {
                "success": success,
                "path_length": path_length,
                "time": computation_time,
                "training_time": training_time,
                "collisions": collisions,
                "battery": battery_used
            }
            
        except Exception as e:
            print(f"  Error in {variant_name}: {e}")
            return {
                "success": False, "path_length": 0, "time": 0,
                "training_time": 0, "collisions": 0, "battery": 0
            }
    
    def run_ablation_study(self, moving_obstacles=False):
        """Run complete ablation study."""
        print("\n" + "="*80)
        print("ABLATION STUDY: Multi-Level RL Policies")
        print("="*80)
        print(f"\nTesting Enhanced Hybrid WITH and WITHOUT multi-level RL")
        print(f"Trials: {self.num_trials} per variant")
        print(f"Moving Obstacles: {moving_obstacles}\n")
        
        variants = [
            {
                "name": "Enhanced Hybrid WITH Multi-Level RL",
                "use_multi_level": True
            },
            {
                "name": "Enhanced Hybrid WITHOUT Multi-Level RL",
                "use_multi_level": False
            }
        ]
        
        for trial in range(self.num_trials):
            if (trial + 1) % 5 == 0:
                print(f"Trial {trial + 1}/{self.num_trials}...")
            
            for variant in variants:
                metrics = self.test_variant(
                    variant["name"],
                    use_multi_level=variant["use_multi_level"],
                    moving_obstacles=moving_obstacles
                )
                
                key = "with_multi_level" if variant["use_multi_level"] else "without_multi_level"
                self.results[key]["success"].append(metrics["success"])
                self.results[key]["path_length"].append(metrics["path_length"])
                self.results[key]["time"].append(metrics["time"])
                self.results[key]["training_time"].append(metrics["training_time"])
                self.results[key]["collisions"].append(metrics["collisions"])
                self.results[key]["battery"].append(metrics["battery"])
        
        self.print_results()
        self.save_results(moving_obstacles)
    
    def print_results(self):
        """Print ablation study results."""
        print("\n" + "="*80)
        print("ABLATION STUDY RESULTS - Multi-Level RL")
        print("="*80)
        
        with_ml = self.results["with_multi_level"]
        without_ml = self.results["without_multi_level"]
        
        # Calculate statistics
        success_with = (sum(with_ml["success"]) / len(with_ml["success"])) * 100
        success_without = (sum(without_ml["success"]) / len(without_ml["success"])) * 100
        
        avg_path_with = sum(with_ml["path_length"]) / len(with_ml["path_length"])
        avg_path_without = sum(without_ml["path_length"]) / len(without_ml["path_length"])
        
        avg_time_with = sum(with_ml["time"]) / len(with_ml["time"])
        avg_time_without = sum(without_ml["time"]) / len(without_ml["time"])
        
        avg_training_with = sum(with_ml["training_time"]) / len(with_ml["training_time"])
        avg_training_without = sum(without_ml["training_time"]) / len(without_ml["training_time"])
        
        avg_collisions_with = sum(with_ml["collisions"]) / len(with_ml["collisions"])
        avg_collisions_without = sum(without_ml["collisions"]) / len(without_ml["collisions"])
        
        print(f"\n{'Variant':<50} {'Success':<12} {'Path Len':<12} {'Time (s)':<12} {'Train (s)':<12} {'Collisions':<12}")
        print("-" * 100)
        print(f"{'WITH Multi-Level RL':<50} {success_with:>10.1f}%  {avg_path_with:>10.1f}  {avg_time_with:>10.3f}  {avg_training_with:>10.3f}  {avg_collisions_with:>10.2f}")
        print(f"{'WITHOUT Multi-Level RL':<50} {success_without:>10.1f}%  {avg_path_without:>10.1f}  {avg_time_without:>10.3f}  {avg_training_without:>10.3f}  {avg_collisions_without:>10.2f}")
        
        print(f"\n{'Impact of Multi-Level RL':<50} {'':<12} {'':<12} {'':<12} {'':<12} {'':<12}")
        print(f"{'Difference':<50} {success_with-success_without:>10.1f}%  {avg_path_with-avg_path_without:>10.1f}  {avg_time_with-avg_time_without:>10.3f}  {avg_training_with-avg_training_without:>10.3f}  {avg_collisions_with-avg_collisions_without:>10.2f}")
        
        # Analysis
        print("\n" + "="*80)
        print("ANALYSIS")
        print("="*80)
        
        if success_with > success_without:
            print(f"[+] Multi-Level RL improves success rate by {success_with - success_without:.1f}%")
        elif success_with < success_without:
            print(f"[-] Multi-Level RL reduces success rate by {success_without - success_with:.1f}%")
        else:
            print("[=] Multi-Level RL has no impact on success rate")
        
        if avg_path_with < avg_path_without:
            print(f"[+] Multi-Level RL reduces path length by {avg_path_without - avg_path_with:.1f} steps")
        elif avg_path_with > avg_path_without:
            print(f"[-] Multi-Level RL increases path length by {avg_path_with - avg_path_without:.1f} steps")
        else:
            print("[=] Multi-Level RL has no impact on path length")
        
        if avg_time_with < avg_time_without:
            print(f"[+] Multi-Level RL reduces computation time by {avg_time_without - avg_time_with:.3f}s")
        elif avg_time_with > avg_time_without:
            print(f"[-] Multi-Level RL increases computation time by {avg_time_with - avg_time_without:.3f}s")
        else:
            print("[=] Multi-Level RL has no impact on computation time")
        
        if avg_collisions_with < avg_collisions_without:
            print(f"[+] Multi-Level RL reduces collisions by {avg_collisions_without - avg_collisions_with:.2f}")
        elif avg_collisions_with > avg_collisions_without:
            print(f"[-] Multi-Level RL increases collisions by {avg_collisions_with - avg_collisions_without:.2f}")
        else:
            print("[=] Multi-Level RL has no impact on collisions")
    
    def save_results(self, moving_obstacles=False):
        """Save results to JSON."""
        output_file = f"ablation_multi_level_rl_{'dynamic' if moving_obstacles else 'static'}.json"
        
        results_dict = {}
        for variant, metrics in self.results.items():
            results_dict[variant] = {}
            for metric, values in metrics.items():
                results_dict[variant][metric] = values
        
        with open(output_file, 'w') as f:
            json.dump({
                "num_trials": self.num_trials,
                "moving_obstacles": moving_obstacles,
                "variants": {
                    "with_multi_level": "Enhanced Hybrid WITH Multi-Level RL",
                    "without_multi_level": "Enhanced Hybrid WITHOUT Multi-Level RL"
                },
                "results": results_dict
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    # Test with static obstacles
    print("\n>>> Testing with STATIC obstacles...")
    study = MultiLevelRLAblationStudy(num_trials=20, grid_size=20, obstacle_percent=0.15)
    study.run_ablation_study(moving_obstacles=False)
    
    # Test with dynamic obstacles
    print("\n\n>>> Testing with DYNAMIC obstacles...")
    study_dynamic = MultiLevelRLAblationStudy(num_trials=20, grid_size=20, obstacle_percent=0.15)
    study_dynamic.run_ablation_study(moving_obstacles=True)
