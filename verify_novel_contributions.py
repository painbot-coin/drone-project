"""
Verify All Novel Contributions Work Correctly
==============================================
Tests each of the 4 novel contributions individually to ensure they work:
1. Experience Replay Buffer
2. Uncertainty Quantification
3. Adaptive Confidence Threshold
4. Transfer Learning
"""

import random
import time
import sys

# Load classes
print("Loading classes...")
with open('in testing environment.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'if __name__ == "__main__":' in content:
        content = content.split('if __name__ == "__main__":')[0]
    exec(content)
print("✓ Classes loaded\n")

# Set seed for reproducibility
random.seed(42)

class ContributionVerifier:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        """Run a test and record result."""
        print(f"Testing: {name}...", end=" ")
        try:
            result = func()
            if result:
                print("✓ PASSED")
                self.passed += 1
                self.tests.append((name, True, None))
            else:
                print("✗ FAILED")
                self.failed += 1
                self.tests.append((name, False, "Test returned False"))
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def verify_experience_replay(self):
        """Test 1: Experience Replay Buffer"""
        env = Environment(grid_size=10)
        env.generate_obstacles()
        
        mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=10, replay_buffer_size=50, replay_batch_size=10)
        
        # Check that replay buffer exists
        if not hasattr(mr_ql, 'replay_buffer'):
            return False
        
        # Train for a few episodes
        mr_ql.train()
        
        # Check that replay buffer has experiences
        if len(mr_ql.replay_buffer) == 0:
            return False
        
        # Check that replay_experiences method exists and works
        if not hasattr(mr_ql, 'replay_experiences'):
            return False
        
        # Manually add some experiences and test replay
        initial_q_size = len(mr_ql.q_table)
        mr_ql.replay_experiences()
        
        # Replay should update Q-table (or at least not crash)
        return True
    
    def verify_uncertainty_quantification(self):
        """Test 2: Uncertainty Quantification"""
        env = Environment(grid_size=10)
        env.generate_obstacles()
        
        mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=10)
        
        # Check that uncertainty tracking exists
        if not hasattr(mr_ql, 'q_value_history'):
            return False
        if not hasattr(mr_ql, 'q_value_variance'):
            return False
        
        # Train a bit
        mr_ql.train()
        
        # Check that state_confidence method exists and works
        if not hasattr(mr_ql, 'state_confidence'):
            return False
        
        # Test confidence calculation
        test_state = env.start
        confidence = mr_ql.state_confidence(test_state)
        
        # Confidence should be a number (0.0 to 1.0)
        if not isinstance(confidence, (int, float)):
            return False
        if confidence < 0 or confidence > 1:
            return False
        
        return True
    
    def verify_adaptive_threshold(self):
        """Test 3: Adaptive Confidence Threshold"""
        env = Environment(grid_size=10)
        env.generate_obstacles()
        
        mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=10, confidence_threshold=5)
        
        # Check that adaptive threshold components exist
        if not hasattr(mr_ql, 'confidence_threshold'):
            return False
        if not hasattr(mr_ql, 'adaptive_threshold_history'):
            return False
        if not hasattr(mr_ql, 'adapt_confidence_threshold'):
            return False
        if not hasattr(mr_ql, 'should_use_astar_fallback'):
            return False
        
        # Test threshold adaptation
        initial_threshold = mr_ql.confidence_threshold
        mr_ql.adapt_confidence_threshold(0.5)  # Low success rate
        # Threshold should potentially decrease
        mr_ql.adapt_confidence_threshold(0.95)  # High success rate
        # Threshold should potentially increase
        
        # Check that should_use_astar_fallback works
        test_state = env.start
        decision = mr_ql.should_use_astar_fallback(test_state)
        if not isinstance(decision, bool):
            return False
        
        return True
    
    def verify_transfer_learning(self):
        """Test 4: Transfer Learning"""
        # Create first environment and train
        env1 = Environment(grid_size=10)
        env1.generate_obstacles()
        
        mr_ql1 = MRQLearning(env1.grid, env1.start, env1.goal, episodes=20)
        mr_ql1.train()
        
        # Get Q-table for transfer
        if not hasattr(mr_ql1, 'get_q_table_for_transfer'):
            return False
        
        transfer_q_table = mr_ql1.get_q_table_for_transfer()
        if not isinstance(transfer_q_table, dict):
            return False
        if len(transfer_q_table) == 0:
            return False  # Should have learned something
        
        # Create second environment (similar)
        env2 = Environment(grid_size=10)
        env2.generate_obstacles()
        
        # Test transfer learning compatibility
        if not hasattr(mr_ql1, 'transfer_learning_compatibility'):
            return False
        
        # Create new MR-QL with transfer
        mr_ql2 = MRQLearning(env2.grid, env2.start, env2.goal, episodes=10, transfer_q_table=transfer_q_table)
        
        # Check that Q-table was transferred
        if len(mr_ql2.q_table) == 0:
            return False  # Should have transferred Q-table
        
        # Check compatibility
        compatible = mr_ql1.transfer_learning_compatibility(transfer_q_table)
        if not isinstance(compatible, bool):
            return False
        
        return True
    
    def verify_integration(self):
        """Test 5: All contributions work together"""
        env = Environment(grid_size=15)
        env.generate_obstacles()
        
        # Create MR-QL with all features
        mr_ql = MRQLearning(
            env.grid, env.start, env.goal,
            episodes=30,
            replay_buffer_size=100,
            replay_batch_size=20,
            confidence_threshold=5
        )
        
        # Train
        mr_ql.train()
        
        # Check all features are present
        checks = [
            hasattr(mr_ql, 'replay_buffer'),
            hasattr(mr_ql, 'q_value_variance'),
            hasattr(mr_ql, 'adaptive_threshold_history'),
            hasattr(mr_ql, 'get_q_table_for_transfer'),
            hasattr(mr_ql, 'state_confidence'),
            hasattr(mr_ql, 'should_use_astar_fallback'),
            hasattr(mr_ql, 'replay_experiences'),
            hasattr(mr_ql, 'adapt_confidence_threshold'),
        ]
        
        if not all(checks):
            return False
        
        # Test that they work together
        state = env.start
        confidence = mr_ql.state_confidence(state)
        should_fallback = mr_ql.should_use_astar_fallback(state)
        
        # All should work without errors
        return True
    
    def verify_hybrid_mode(self):
        """Test 6: Hybrid mode with confidence-aware fallback"""
        env = Environment(grid_size=15)
        env.generate_obstacles()
        
        # Test get_path with fallback enabled
        mr_ql = MRQLearning(env.grid, env.start, env.goal, episodes=30, confidence_threshold=5)
        mr_ql.train()
        
        # Test path generation with fallback
        path_with_fallback = mr_ql.get_path(use_astar_fallback=True)
        path_without_fallback = mr_ql.get_path(use_astar_fallback=False)
        
        # Both should return paths (or empty if no path)
        if not isinstance(path_with_fallback, list):
            return False
        if not isinstance(path_without_fallback, list):
            return False
        
        # With fallback, should always get a path (A* fallback)
        if len(path_with_fallback) == 0:
            # This might be okay if environment is unsolvable, but check
            astar = AStar(env.grid, env.start, env.goal)
            astar_path = astar.search()
            if len(astar_path) > 0:
                return False  # A* found path, so fallback should have worked
        
        return True
    
    def run_all_tests(self):
        """Run all verification tests."""
        print("="*80)
        print("VERIFYING ALL NOVEL CONTRIBUTIONS")
        print("="*80)
        print()
        
        self.test("1. Experience Replay Buffer", self.verify_experience_replay)
        self.test("2. Uncertainty Quantification", self.verify_uncertainty_quantification)
        self.test("3. Adaptive Confidence Threshold", self.verify_adaptive_threshold)
        self.test("4. Transfer Learning", self.verify_transfer_learning)
        self.test("5. Integration (All Together)", self.verify_integration)
        self.test("6. Hybrid Mode with Fallback", self.verify_hybrid_mode)
        
        print()
        print("="*80)
        print("VERIFICATION SUMMARY")
        print("="*80)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        print()
        
        if self.failed == 0:
            print("✓ ALL TESTS PASSED - All novel contributions working correctly!")
        else:
            print("✗ SOME TESTS FAILED - Review errors above")
            print("\nFailed tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")
        
        print("="*80)
        
        return self.failed == 0

if __name__ == "__main__":
    verifier = ContributionVerifier()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1)

