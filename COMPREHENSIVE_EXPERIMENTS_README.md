# Comprehensive Experiments Script

## Purpose
Tests all methods under various experimental conditions to create a complete experimental dataset.

## Experiments Included

### ✅ Implemented:
1. **Varying Obstacle Densities** (10%, 15%, 20%, 25%)
   - Tests how methods perform with different obstacle densities
   - All methods tested on same environments

2. **Different Grid Sizes** (15x15, 20x20, 25x25)
   - Tests scalability of methods
   - Shows how performance changes with grid size

3. **Static Obstacles Only**
   - Baseline experiment with static obstacles
   - All methods tested

4. **Transfer Learning**
   - Trains MR-QLearning on source environment
   - Tests on target environment with/without transfer
   - Compares performance improvement

### ⚠️ Requires Simulator Integration:
5. **Dynamic Obstacles Only**
   - Requires moving obstacles during execution
   - Needs simulator integration

6. **Mixed Static + Dynamic Obstacles**
   - Requires both static and dynamic obstacles
   - Needs simulator integration

## Usage

### Run All Experiments:
```bash
python comprehensive_experiments.py
```

### Configuration:
- **Trials per condition**: 15 (configurable)
- **Episodes**: 100 (fast mode) or 200 (full mode)
- **Estimated time**: ~2-3 minutes for all experiments

### To Adjust:
Edit `comprehensive_experiments.py`:
```python
experiments = ComprehensiveExperiments(
    trials_per_condition=15,  # Change number of trials
    fast_mode=True             # Set to False for full mode
)
```

## Output

### Console:
- Progress updates
- Summary statistics for each experiment
- Comparison tables

### JSON File:
- `comprehensive_experiments_results.json`
- Contains all raw data
- Organized by experiment condition
- Ready for statistical analysis

## Results Structure

### By Condition:
- `density_10`, `density_15`, `density_20`, `density_25`: Obstacle density results
- `grid_15`, `grid_20`, `grid_25`: Grid size results
- `static_only`: Static obstacles results
- `transfer_learning`: Transfer learning results (with/without)

### Metrics Collected:
- Success rate
- Path length
- Computation time
- Collisions
- Battery consumption
- Training time (for RL methods)

## Next Steps

1. **Run the script** to generate complete dataset
2. **Analyze results** for each condition
3. **Add dynamic obstacles** experiments (requires simulator integration)
4. **Statistical analysis** comparing conditions

## Note on Dynamic Obstacles

Dynamic obstacle experiments require:
- Simulator integration (moving obstacles during execution)
- Real-time replanning
- Can be added later using the existing simulator framework

The current script focuses on static environments which are sufficient for most comparisons.

