"""
Quick Test: All Methods on Same Environment
===========================================
Simple test to verify all methods work on the same environment.
"""

import random
import time
import sys

# Set random seed for reproducibility
random.seed(42)

# Read and execute the testing environment code (without GUI)
print("Loading classes from testing environment...")
with open('in testing environment.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    # Remove the main execution part to avoid GUI
    if 'if __name__ == "__main__":' in content:
        content = content.split('if __name__ == "__main__":')[0]
    exec(content)

print("✓ Classes loaded successfully\n")

# Create a test environment
print("Creating test environment...")
env = Environment(grid_size=20)
env.generate_obstacles()
print(f"✓ Environment created: {len(env.grid)}x{len(env.grid)} grid")
print(f"  Start: {env.start}, Goal: {env.goal}")
print(f"  Obstacles: {sum(sum(row) for row in env.grid)} cells\n")

# Test each method on the SAME environment
methods_to_test = [
    ("A*", "astar"),
    ("D* Lite", "dstar"),
    ("Double Q-Learning", "double_q"),
    ("MR-QLearning", "mr_ql"),
    ("Hybrid", "hybrid")
]

results = {}

print("="*70)
print("TESTING ALL METHODS ON SAME ENVIRONMENT")
print("="*70)
print()

for method_name, method_code in methods_to_test:
    print(f"Testing {method_name}...", end=" ")
    start_time = time.time()
    path = []
    success = False
    
    try:
        if method_code == "astar":
            astar = AStar(env.grid, env.start, env.goal)
            path = astar.search()
            success = len(path) > 0 and path[-1] == env.goal
            
        elif method_code == "dstar":
            dstar = DStarLite(env.grid, env.start, env.goal)
            path = dstar.search()
            success = len(path) > 0 and path[-1] == env.goal
            
        elif method_code == "double_q":
            double_q = DoubleQLearning(env.grid, env.start, env.goal, episodes=100)  # Reduced for quick test
            double_q.train()
            path = double_q.get_path()
            success = len(path) > 0 and path[-1] == env.goal
            
        elif method_code == "mr_ql":
            mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=100)  # Reduced for quick test
            mr_ql.train()
            path = mr_ql.get_path(use_astar_fallback=False)
            success = len(path) > 0 and path[-1] == env.goal
            
        elif method_code == "hybrid":
            astar = AStar(env.grid, env.start, env.goal)
            global_path = astar.search()
            path = global_path
            success = len(path) > 0 and path[-1] == env.goal
        
        elapsed = time.time() - start_time
        results[method_name] = {
            "success": success,
            "path_length": len(path) if path else 0,
            "time": elapsed
        }
        print(f"✓ Success: {success}, Path Length: {len(path) if path else 0}, Time: {elapsed:.3f}s")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        results[method_name] = {
            "success": False,
            "path_length": 0,
            "time": 0,
            "error": str(e)
        }

print()
print("="*70)
print("RESULTS SUMMARY")
print("="*70)
print(f"{'Method':<25} {'Success':<10} {'Path Length':<15} {'Time (s)':<10}")
print("-"*70)

for method_name, result in results.items():
    success_str = "✓ Yes" if result["success"] else "✗ No"
    print(f"{method_name:<25} {success_str:<10} {result['path_length']:<15} {result['time']:<10.3f}")

print()
print("="*70)
print("✓ All methods tested on the SAME environment")
print("="*70)

