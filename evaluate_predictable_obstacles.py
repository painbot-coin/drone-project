"""
Evaluate Obstacle Prediction Feature
Tests the 5th RL innovation: RL-Based Obstacle Prediction
"""

import sys
import os
import json
import time
from collections import defaultdict

# Execute the main file to import classes
main_file = os.path.join(os.path.dirname(__file__), 'in testing environment.txt')

if not os.path.exists(main_file):
    print(f"Error: Could not find '{main_file}'")
    sys.exit(1)

with open(main_file, 'r', encoding='utf-8') as f:
    code = f.read()
    if 'if __name__ == "__main__":' in code:
        code = code.split('if __name__ == "__main__":')[0]
    namespace = {}
    exec(code, namespace)
    
    Environment = namespace.get('Environment')
    EnhancedHybrid = namespace.get('EnhancedHybrid')
    AStar = namespace.get('AStar')

class PredictableObstacleEnvironment:
    """Environment with predictable obstacle movement for testing prediction."""
    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.start = (0, 0)
        self.goal = (grid_size - 1, grid_size - 1)
        
        # Create static obstacles
        self.static_obstacles = set()
        for i in range(5, 10):
            for j in range(5, 10):
                if (i, j) not in (self.start, self.goal):
                    self.grid[i][j] = 1
                    self.static_obstacles.add((i, j))
        
        # Create moving obstacles with predictable patterns
        self.moving_obstacles = []
        self.moving_directions = {}
        
        # Obstacle 1: Moves right consistently
        self.moving_obstacles.append((2, 2))
        self.moving_directions[(2, 2)] = (0, 1)
        self.grid[2][2] = 1
        
        # Obstacle 2: Moves down consistently
        self.moving_obstacles.append((3, 15))
        self.moving_directions[(3, 15)] = (1, 0)
        self.grid[3][15] = 1
        
        # Obstacle 3: Moves diagonally
        self.moving_obstacles.append((10, 10))
        self.moving_directions[(10, 10)] = (1, 1)
        self.grid[10][10] = 1
    
    def move_obstacles_predictable(self):
        """Move obstacles in their assigned directions."""
        new_positions = []
        new_directions = {}
        
        for pos in self.moving_obstacles:
            if 0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size:
                self.grid[pos[0]][pos[1]] = 0
            
            dx, dy = self.moving_directions.get(pos, (0, 0))
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            
            if new_x < 0 or new_x >= self.grid_size:
                dx = -dx
                new_x = pos[0] + dx
            if new_y < 0 or new_y >= self.grid_size:
                dy = -dy
                new_y = pos[1] + dy
            
            if (new_x, new_y) in (self.start, self.goal):
                new_x, new_y = pos
            
            new_pos = (new_x, new_y)
            new_positions.append(new_pos)
            new_directions[new_pos] = (dx, dy)
            
            if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                self.grid[new_x][new_y] = 1
        
        self.moving_obstacles = new_positions
        self.moving_directions = new_directions
    
    def get_obstacle_positions(self):
        """Get current obstacle positions as a set."""
        obstacles = set()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 1:
                    obstacles.add((i, j))
        return obstacles

class PredictableObstacleEvaluator:
    """Evaluate obstacle prediction feature."""
    
    def __init__(self, num_trials=20):
        self.num_trials = num_trials
        self.results = defaultdict(lambda: defaultdict(list))
    
    def evaluate_prediction(self):
        """Evaluate prediction function."""
        print("\n" + "="*80)
        print("PREDICTABLE OBSTACLES EVALUATION")
        print("Testing RL-Based Obstacle Prediction (5th RL Innovation)")
        print("="*80)
        
        for trial in range(self.num_trials):
            if (trial + 1) % 5 == 0:
                print(f"Trial {trial + 1}/{self.num_trials}...")
            
            env = PredictableObstacleEnvironment(grid_size=20)
            enhanced = EnhancedHybrid(env.grid, env.start, env.goal, episodes=100, real_time_mode=True)
            enhanced.train()
            
            # Build obstacle history (need at least 3 steps for prediction)
            for step in range(15):  # More steps to build better history
                obstacle_positions = env.get_obstacle_positions()
                enhanced.obstacle_history.append(obstacle_positions.copy())
                if len(enhanced.obstacle_history) > 20:  # Keep more history
                    enhanced.obstacle_history.pop(0)
                env.move_obstacles_predictable()
            
            # Test with predictions
            path_with_pred = enhanced.search(use_predictions=True)
            path_no_pred = enhanced.search(use_predictions=False)
            
            # Get predictions
            predicted = enhanced.predict_obstacle_movement(env.start, lookahead=3)
            
            # Metrics
            success_with = len(path_with_pred) > 0 and path_with_pred[-1] == env.goal
            success_without = len(path_no_pred) > 0 and path_no_pred[-1] == env.goal
            path_len_with = len(path_with_pred) if path_with_pred else 0
            path_len_without = len(path_no_pred) if path_no_pred else 0
            num_predictions = len(predicted)
            
            self.results["with_predictions"]["success"].append(success_with)
            self.results["with_predictions"]["path_length"].append(path_len_with)
            self.results["with_predictions"]["num_predictions"].append(num_predictions)
            
            self.results["without_predictions"]["success"].append(success_without)
            self.results["without_predictions"]["path_length"].append(path_len_without)
        
        self.save_results()
        self.print_results()
    
    def print_results(self):
        """Print evaluation results."""
        print("\n" + "="*80)
        print("PREDICTION EVALUATION RESULTS")
        print("="*80)
        
        with_pred = self.results["with_predictions"]
        without_pred = self.results["without_predictions"]
        
        success_with = (sum(with_pred["success"]) / len(with_pred["success"])) * 100
        success_without = (sum(without_pred["success"]) / len(without_pred["success"])) * 100
        avg_path_with = sum(with_pred["path_length"]) / len(with_pred["path_length"])
        avg_path_without = sum(without_pred["path_length"]) / len(without_pred["path_length"])
        avg_predictions = sum(with_pred["num_predictions"]) / len(with_pred["num_predictions"])
        
        print(f"\nWith Predictions:")
        print(f"  Success Rate: {success_with:.1f}%")
        print(f"  Avg Path Length: {avg_path_with:.1f} steps")
        print(f"  Avg Predictions Generated: {avg_predictions:.1f}")
        
        print(f"\nWithout Predictions:")
        print(f"  Success Rate: {success_without:.1f}%")
        print(f"  Avg Path Length: {avg_path_without:.1f} steps")
        
        print(f"\nImprovement:")
        print(f"  Success Rate: {success_with - success_without:.1f}%")
        print(f"  Path Length: {avg_path_without - avg_path_with:.1f} steps")
    
    def save_results(self):
        """Save results to JSON."""
        output_file = "predictable_obstacles_results.json"
        
        results_dict = {}
        for condition, metrics in self.results.items():
            results_dict[condition] = {}
            for metric, values in metrics.items():
                results_dict[condition][metric] = values
        
        with open(output_file, 'w') as f:
            json.dump({
                "num_trials": self.num_trials,
                "results": results_dict
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    evaluator = PredictableObstacleEvaluator(num_trials=20)
    evaluator.evaluate_prediction()
