"""
Test script for the obstacle prediction function in Enhanced Hybrid A* + RL.

This script tests the prediction function with predictable obstacle movement patterns.

Usage:
    python test_prediction_function.py

Note: This script imports from 'in testing environment.txt' by executing it.
      Make sure the file is in the same directory.
"""

import sys
import os

# Execute the main file to import classes
# Note: The file name has spaces, so we need to handle it carefully
main_file = os.path.join(os.path.dirname(__file__), 'in testing environment.txt')

if not os.path.exists(main_file):
    print(f"Error: Could not find '{main_file}'")
    print("Make sure 'in testing environment.txt' is in the same directory as this script.")
    sys.exit(1)

# Read and execute the main file to get the classes
with open(main_file, 'r', encoding='utf-8') as f:
    code = f.read()
    # Execute in a namespace
    namespace = {}
    exec(code, namespace)
    
    # Extract the classes we need
    Environment = namespace.get('Environment')
    EnhancedHybrid = namespace.get('EnhancedHybrid')
    AStar = namespace.get('AStar')
    
    if not all([Environment, EnhancedHybrid, AStar]):
        print("Error: Could not find required classes (Environment, EnhancedHybrid, AStar)")
        print("Make sure 'in testing environment.txt' contains these class definitions.")
        sys.exit(1)


class PredictableObstacleEnvironment:
    """
    Environment with predictable obstacle movement for testing prediction function.
    """
    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.start = (0, 0)
        self.goal = (grid_size - 1, grid_size - 1)
        
        # Create some static obstacles
        self.static_obstacles = set()
        for i in range(5, 10):
            for j in range(5, 10):
                if (i, j) not in (self.start, self.goal):
                    self.grid[i][j] = 1
                    self.static_obstacles.add((i, j))
        
        # Create moving obstacles with predictable patterns
        self.moving_obstacles = []
        self.moving_directions = {}  # obstacle_pos -> (dx, dy) direction
        
        # Obstacle 1: Moves right consistently
        self.moving_obstacles.append((2, 2))
        self.moving_directions[(2, 2)] = (0, 1)  # Right
        self.grid[2][2] = 1
        
        # Obstacle 2: Moves down consistently
        self.moving_obstacles.append((3, 15))
        self.moving_directions[(3, 15)] = (1, 0)  # Down
        self.grid[3][15] = 1
        
        # Obstacle 3: Moves diagonally (down-right)
        self.moving_obstacles.append((10, 10))
        self.moving_directions[(10, 10)] = (1, 1)  # Down-right
        self.grid[10][10] = 1
    
    def move_obstacles_predictable(self):
        """Move obstacles in their assigned directions."""
        new_positions = []
        new_directions = {}
        
        for pos in self.moving_obstacles:
            # Clear old position
            if 0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size:
                self.grid[pos[0]][pos[1]] = 0
            
            # Get direction
            dx, dy = self.moving_directions.get(pos, (0, 0))
            
            # Calculate new position
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            
            # Boundary check - reverse direction if hitting boundary
            if new_x < 0 or new_x >= self.grid_size:
                dx = -dx
                new_x = pos[0] + dx
            if new_y < 0 or new_y >= self.grid_size:
                dy = -dy
                new_y = pos[1] + dy
            
            # Avoid start/goal
            if (new_x, new_y) in (self.start, self.goal):
                new_x, new_y = pos  # Stay in place
            
            new_pos = (new_x, new_y)
            new_positions.append(new_pos)
            new_directions[new_pos] = (dx, dy)
            
            # Set new position
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


def test_prediction_function():
    """Test the obstacle prediction function."""
    print("="*60)
    print("Testing Obstacle Prediction Function")
    print("="*60)
    
    # Create environment with predictable obstacles
    env = PredictableObstacleEnvironment(grid_size=20)
    
    # Create Enhanced Hybrid instance
    enhanced = EnhancedHybrid(
        env.grid, 
        env.start, 
        env.goal, 
        episodes=50,  # Reduced for testing
        real_time_mode=True
    )
    
    # Simulate obstacle movement for a few steps to build history
    print("\n1. Building obstacle movement history...")
    for step in range(5):
        obstacle_positions = env.get_obstacle_positions()
        enhanced.obstacle_history.append(obstacle_positions.copy())
        if len(enhanced.obstacle_history) > 10:
            enhanced.obstacle_history.pop(0)
        
        env.move_obstacles_predictable()
        print(f"   Step {step+1}: {len(obstacle_positions)} obstacles")
    
    # Test prediction
    print("\n2. Testing prediction function...")
    current_pos = (5, 5)
    predicted = enhanced.predict_obstacle_movement(current_pos, lookahead=3)
    
    print(f"   Current position: {current_pos}")
    print(f"   Predicted obstacle positions (lookahead=3): {len(predicted)} positions")
    if predicted:
        print(f"   Predicted positions: {sorted(list(predicted))[:10]}...")  # Show first 10
    else:
        print("   [WARNING] No predictions (this is expected if history is insufficient)")
    
    # Test with more history
    print("\n3. Building more history (10 steps)...")
    for step in range(10):
        obstacle_positions = env.get_obstacle_positions()
        enhanced.obstacle_history.append(obstacle_positions.copy())
        if len(enhanced.obstacle_history) > 10:
            enhanced.obstacle_history.pop(0)
        
        env.move_obstacles_predictable()
    
    # Test prediction again
    predicted = enhanced.predict_obstacle_movement(current_pos, lookahead=3)
    print(f"   Predicted obstacle positions: {len(predicted)} positions")
    if predicted:
        print(f"   [OK] Prediction working! Predicted positions: {sorted(list(predicted))[:10]}...")
    else:
        print("   [WARNING] Still no predictions - check obstacle movement patterns")
    
    # Test path planning with predictions
    print("\n4. Testing path planning with predictions enabled...")
    enhanced.train()  # Minimal training
    
    # Get current obstacle positions
    current_obstacles = env.get_obstacle_positions()
    print(f"   Current obstacles: {len(current_obstacles)}")
    
    # Plan path without predictions
    path_no_pred = enhanced.search(use_predictions=False)
    print(f"   Path without predictions: {len(path_no_pred)} steps")
    
    # Plan path with predictions
    path_with_pred = enhanced.search(use_predictions=True)
    print(f"   Path with predictions: {len(path_with_pred)} steps")
    
    if len(path_with_pred) != len(path_no_pred):
        print(f"   [OK] Predictions affected path planning!")
        print(f"   Difference: {abs(len(path_with_pred) - len(path_no_pred))} steps")
    else:
        print(f"   ℹ️  Predictions did not change path length (may be same optimal path)")
    
    # Verify predictions are being used
    print("\n5. Verification:")
    print(f"   Obstacle history length: {len(enhanced.obstacle_history)}")
    print(f"   Prediction function exists: {hasattr(enhanced, 'predict_obstacle_movement')}")
    
    # Show some predicted positions
    if predicted:
        print(f"\n   Sample predicted positions:")
        for i, pos in enumerate(sorted(list(predicted))[:5]):
            print(f"      {i+1}. {pos}")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    
    return {
        'predictions_working': len(predicted) > 0,
        'num_predictions': len(predicted),
        'path_with_pred_len': len(path_with_pred),
        'path_no_pred_len': len(path_no_pred)
    }


if __name__ == "__main__":
    try:
        results = test_prediction_function()
        print(f"\nResults Summary:")
        print(f"  Predictions working: {results['predictions_working']}")
        print(f"  Number of predictions: {results['num_predictions']}")
        print(f"  Path length (with pred): {results['path_with_pred_len']}")
        print(f"  Path length (no pred): {results['path_no_pred_len']}")
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: Make sure 'in testing environment.txt' is in the same directory")
        print("      and contains the Environment, EnhancedHybrid, and AStar classes.")
        print("      Also ensure the file can be executed (no syntax errors).")

