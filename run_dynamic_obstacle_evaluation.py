"""
Dynamic Obstacle Evaluation Script
==================================
Tests Objective #1: Real-Time Path Planning with Dynamic Obstacle Avoidance

This script evaluates all methods with moving obstacles to properly test
the primary objective of the thesis.
"""

import json
import time
from benchmark_comparison import BenchmarkRunner

def main():
    print("\n" + "="*80)
    print("DYNAMIC OBSTACLE EVALUATION")
    print("Testing Objective #1: Real-Time Path Planning with Dynamic Obstacle Avoidance")
    print("="*80)
    
    # Create benchmark runner
    # Using 30 trials for faster execution (increase to 50 for final results)
    benchmark = BenchmarkRunner(num_trials=30, grid_size=20, obstacle_percent=0.15)
    
    print("\n>>> Running benchmark with DYNAMIC obstacles (all 7 methods)...")
    print("This tests the primary objective: Dynamic Obstacle Avoidance")
    print()
    
    # Run with dynamic obstacles
    benchmark.run_benchmark(moving_obstacles=True)
    
    print("\n" + "="*80)
    print("DYNAMIC OBSTACLE EVALUATION COMPLETE")
    print("="*80)
    print("\nResults saved to: benchmark_results_dynamic.json")
    print("\nNext Steps:")
    print("1. Compare with static obstacle results")
    print("2. Analyze replanning performance")
    print("3. Verify 'instant replanning' requirement (< 0.1s)")
    print("4. Add results to thesis Results section")
    print("5. Update Discussion section with static vs dynamic comparison")
    
    # Load and display summary
    try:
        with open('benchmark_results_dynamic.json', 'r') as f:
            data = json.load(f)
        
        print("\n" + "="*80)
        print("QUICK SUMMARY - Dynamic Obstacles")
        print("="*80)
        
        results = data.get('results', {})
        for method, metrics in results.items():
            if 'success' in metrics and metrics['success']:
                success_count = sum(metrics['success'])
                success_rate = (success_count / len(metrics['success'])) * 100
                avg_time = sum(metrics['time']) / len(metrics['time']) if metrics['time'] else 0
                avg_path = sum(metrics['path_length']) / len(metrics['path_length']) if metrics['path_length'] else 0
                
                print(f"\n{method.upper()}:")
                print(f"  Success Rate: {success_rate:.1f}%")
                print(f"  Avg Path Length: {avg_path:.1f} steps")
                print(f"  Avg Time: {avg_time:.3f}s")
                
                # Check if replanning is "instant" (< 0.1s)
                if avg_time < 0.1:
                    print(f"  [OK] Instant replanning: {avg_time:.3f}s < 0.1s")
                else:
                    print(f"  [WARNING] Replanning time: {avg_time:.3f}s (may exceed instant requirement)")
    except FileNotFoundError:
        print("\n[WARNING] Results file not found. Check if benchmark completed successfully.")
    except Exception as e:
        print(f"\n[ERROR] Error reading results: {e}")


if __name__ == "__main__":
    main()
