"""
Ablation Study: Test Impact of Each Novel Contribution
=======================================================
Tests MR-QLearning with each contribution removed to show their individual impact.

Ablations:
1. MR-QLearning WITHOUT experience replay
2. MR-QLearning WITHOUT uncertainty quantification
3. MR-QLearning WITHOUT adaptive threshold
4. MR-QLearning WITHOUT transfer learning
5. Full MR-QLearning (all contributions)

Compares each ablation against the full method.
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

class AblationMRQLearning(MRQLearning):
    """Modified MR-QLearning with specific contributions disabled."""
    
    def __init__(self, grid, start, goal, episodes=300, alpha=0.7, gamma=0.9,
                 epsilon=0.25, epsilon_decay=0.995, min_epsilon=0.05,
                 progress_weight=5.0, collision_penalty=-50,
                 confidence_threshold=5, replay_buffer_size=1000, 
                 replay_batch_size=32, transfer_q_table=None,
                 disable_replay=False, disable_uncertainty=False,
                 disable_adaptive=False, disable_transfer=False):
        
        # Call parent init but disable specific features
        self.disable_replay = disable_replay
        self.disable_uncertainty = disable_uncertainty
        self.disable_adaptive = disable_adaptive
        self.disable_transfer = disable_transfer
        
        # Initialize parent
        super().__init__(grid, start, goal, episodes, alpha, gamma, epsilon,
                        epsilon_decay, min_epsilon, progress_weight, collision_penalty,
                        confidence_threshold, replay_buffer_size, replay_batch_size,
                        None if disable_transfer else transfer_q_table)
        
        # Disable features as needed
        if disable_replay:
            self.replay_buffer = []
            self.replay_buffer_size = 0
        
        if disable_uncertainty:
            self.q_value_history = {}
            self.q_value_variance = {}
    
    def replay_experiences(self):
        """Override to disable if needed."""
        if self.disable_replay:
            return
        super().replay_experiences()
    
    def state_confidence(self, state):
        """Override to disable uncertainty quantification if needed."""
        if self.disable_uncertainty:
            # Fallback to simple visit count only
            q_values = self.q_table.get(state, {})
            if not q_values:
                return 0.0
            best_action = max(q_values, key=q_values.get)
            key = (state, best_action)
            visits = self.visit_counts.get(key, 0)
            return min(visits / 10.0, 1.0)  # Simple visit-based confidence
        return super().state_confidence(state)
    
    def adapt_confidence_threshold(self, success_rate):
        """Override to disable adaptive threshold if needed."""
        if self.disable_adaptive:
            return  # Don't adapt threshold
        super().adapt_confidence_threshold(success_rate)
    
    def train(self, early_stop_window=30, early_stop_threshold=0.9):
        """Override train to conditionally disable features."""
        success_history = []
        for ep in range(self.episodes):
            state = self.start
            steps = 0
            max_steps = len(self.grid) * len(self.grid) * 2
            success = False

            while steps < max_steps:
                action = self.choose_action(state)
                reward = self.shaped_reward(state, action)
                self.update_q(state, action, reward, action)
                state = action
                steps += 1
                if state == self.goal:
                    success = True
                    break

            # Experience replay (if enabled)
            if not self.disable_replay and (ep + 1) % 5 == 0:
                self.replay_experiences()

            # Epsilon decay
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            success_history.append(1 if success else 0)

            # Adaptive threshold (if enabled)
            if not self.disable_adaptive and (ep + 1) % 10 == 0 and len(success_history) >= 10:
                recent_success_rate = sum(success_history[-10:]) / 10.0
                self.adapt_confidence_threshold(recent_success_rate)

            # Early stop
            if len(success_history) >= early_stop_window:
                window = success_history[-early_stop_window:]
                if sum(window) / early_stop_window >= early_stop_threshold:
                    break

        self.success_count = sum(success_history)


class AblationStudy:
    def __init__(self, num_trials=20, fast_mode=True):
        self.num_trials = num_trials
        self.fast_mode = fast_mode
        self.episodes = 100 if fast_mode else 200
        self.results = defaultdict(lambda: defaultdict(list))
        
        # Define ablation variants
        self.variants = {
            "full": {
                "name": "Full MR-QLearning (All Contributions)",
                "disable_replay": False,
                "disable_uncertainty": False,
                "disable_adaptive": False,
                "disable_transfer": False
            },
            "no_replay": {
                "name": "MR-QLearning WITHOUT Experience Replay",
                "disable_replay": True,
                "disable_uncertainty": False,
                "disable_adaptive": False,
                "disable_transfer": False
            },
            "no_uncertainty": {
                "name": "MR-QLearning WITHOUT Uncertainty Quantification",
                "disable_replay": False,
                "disable_uncertainty": True,
                "disable_adaptive": False,
                "disable_transfer": False
            },
            "no_adaptive": {
                "name": "MR-QLearning WITHOUT Adaptive Threshold",
                "disable_replay": False,
                "disable_uncertainty": False,
                "disable_adaptive": True,
                "disable_transfer": False
            },
            "no_transfer": {
                "name": "MR-QLearning WITHOUT Transfer Learning",
                "disable_replay": False,
                "disable_uncertainty": False,
                "disable_adaptive": False,
                "disable_transfer": True
            }
        }
    
    def test_variant(self, variant_key, env):
        """Test a specific variant."""
        variant = self.variants[variant_key]
        
        start_time = time.time()
        path = []
        success = False
        collisions = 0
        training_time = 0.0
        
        try:
            mr_ql = AblationMRQLearning(
                env.grid, env.start, env.goal,
                episodes=self.episodes,
                disable_replay=variant["disable_replay"],
                disable_uncertainty=variant["disable_uncertainty"],
                disable_adaptive=variant["disable_adaptive"],
                disable_transfer=variant["disable_transfer"]
            )
            
            train_start = time.time()
            mr_ql.train()
            training_time = time.time() - train_start
            
            path = mr_ql.get_path(use_astar_fallback=False)
            success = len(path) > 0 and path[-1] == env.goal
            
        except Exception as e:
            print(f"  Error in {variant['name']}: {e}")
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
            "success": success,
            "path_length": path_length,
            "time": computation_time,
            "collisions": collisions,
            "battery": battery_used,
            "training_time": training_time
        }
    
    def run_study(self):
        """Run complete ablation study."""
        print("="*80)
        print("ABLATION STUDY: Impact of Each Novel Contribution")
        print("="*80)
        print(f"\nTesting {self.num_trials} trials per variant")
        print(f"Mode: {'FAST' if self.fast_mode else 'FULL'} (Episodes: {self.episodes})")
        print("\nVariants:")
        for key, variant in self.variants.items():
            print(f"  - {variant['name']}")
        print()
        
        start_total = time.time()
        
        for trial in range(self.num_trials):
            if (trial + 1) % 5 == 0:
                elapsed = time.time() - start_total
                remaining = (elapsed / (trial + 1)) * (self.num_trials - trial - 1)
                print(f"Progress: {trial + 1}/{self.num_trials} ({elapsed:.1f}s elapsed, ~{remaining:.1f}s remaining)")
            
            # Create ONE environment for this trial (all variants use same)
            env = Environment(grid_size=20)
            env.generate_obstacles()
            
            # Test ALL variants on the SAME environment
            for variant_key in self.variants.keys():
                metrics = self.test_variant(variant_key, env)
                
                # Store results
                self.results[variant_key]["success"].append(metrics["success"])
                self.results[variant_key]["path_length"].append(metrics["path_length"])
                self.results[variant_key]["time"].append(metrics["time"])
                self.results[variant_key]["collisions"].append(metrics["collisions"])
                self.results[variant_key]["battery"].append(metrics["battery"])
                self.results[variant_key]["training_time"].append(metrics["training_time"])
        
        total_time = time.time() - start_total
        print(f"\n[OK] Completed in {total_time:.1f} seconds\n")
        
        self.print_results()
        self.compare_against_full()
        self.save_results()
    
    def print_results(self):
        """Print ablation study results."""
        print("="*80)
        print("ABLATION STUDY RESULTS")
        print("="*80)
        print()
        
        print(f"{'Variant':<50} {'Success%':<12} {'Avg Path':<12} {'Time(s)':<12} {'Collisions':<12}")
        print("-"*80)
        
        for variant_key, variant in self.variants.items():
            results = self.results[variant_key]
            success_list = results["success"]
            path_list = [p for p, s in zip(results["path_length"], success_list) if s]
            time_list = results["time"]
            collisions_list = results["collisions"]
            
            success_rate = sum(success_list) / len(success_list) * 100
            avg_path = statistics.mean(path_list) if path_list else 0
            avg_time = statistics.mean(time_list)
            avg_collisions = statistics.mean(collisions_list)
            
            name = variant["name"][:48]  # Truncate if too long
            print(f"{name:<50} {success_rate:>10.1f}%  {avg_path:>10.1f}  {avg_time:>10.3f}  {avg_collisions:>10.1f}")
        
        print("\n" + "="*80)
    
    def compare_against_full(self):
        """Compare each ablation against full method."""
        print("\n" + "="*80)
        print("COMPARISON: Each Ablation vs Full Method")
        print("="*80)
        print()
        
        full_results = self.results["full"]
        full_success_list = full_results["success"]
        full_path_list = [p for p, s in zip(full_results["path_length"], full_success_list) if s]
        full_success_rate = sum(full_success_list) / len(full_success_list) * 100
        full_avg_path = statistics.mean(full_path_list) if full_path_list else 0
        
        print(f"Baseline (Full Method):")
        print(f"  Success Rate: {full_success_rate:.1f}%")
        print(f"  Avg Path Length: {full_avg_path:.1f} steps")
        print()
        
        print("Impact of Removing Each Contribution:")
        print("-"*80)
        
        for variant_key, variant in self.variants.items():
            if variant_key == "full":
                continue
            
            results = self.results[variant_key]
            success_list = results["success"]
            path_list = [p for p, s in zip(results["path_length"], success_list) if s]
            
            success_rate = sum(success_list) / len(success_list) * 100
            avg_path = statistics.mean(path_list) if path_list else 0
            
            success_diff = success_rate - full_success_rate
            path_diff = avg_path - full_avg_path
            
            # Determine impact
            if abs(success_diff) < 2 and abs(path_diff) < 1:
                impact = "Minimal"
            elif success_diff < -5 or path_diff > 5:
                impact = "⚠️ NEGATIVE (worse)"
            elif success_diff > 5 or path_diff < -5:
                impact = "[OK] POSITIVE (better)"
            else:
                impact = "Moderate"
            
            contribution_name = variant["name"].replace("MR-QLearning WITHOUT ", "").replace("MR-QLearning ", "")
            print(f"\n{contribution_name}:")
            print(f"  Success Rate: {success_rate:.1f}% (diff: {success_diff:+.1f}%)")
            print(f"  Avg Path: {avg_path:.1f} steps (diff: {path_diff:+.1f})")
            print(f"  Impact: {impact}")
        
        print("\n" + "="*80)
    
    def save_results(self):
        """Save results to JSON."""
        results_dict = {}
        for variant_key, variant in self.variants.items():
            results_dict[variant_key] = {
                "name": variant["name"],
                "results": {}
            }
            for metric, values in self.results[variant_key].items():
                results_dict[variant_key]["results"][metric] = values
        
        with open("ablation_study_results.json", 'w') as f:
            json.dump({
                "num_trials": self.num_trials,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "variants": results_dict
            }, f, indent=2)
        
        print(f"\n[OK] Results saved to: ablation_study_results.json")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ABLATION STUDY: Testing Impact of Each Novel Contribution")
    print("="*80)
    print("\nThis study tests MR-QLearning with each contribution removed")
    print("to show the individual impact of each novel feature.\n")
    
    study = AblationStudy(num_trials=10, fast_mode=True)  # Reduced for faster execution
    study.run_study()
    
    print("\n" + "="*80)
    print("ABLATION STUDY COMPLETE")
    print("="*80)
    print("\nDeliverable: Ablation study results showing impact of each contribution ✅")
    print("="*80)

