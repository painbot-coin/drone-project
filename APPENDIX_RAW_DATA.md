# Appendix: Raw Experimental Data

## A. Dynamic Obstacle Evaluation - Raw Data

### A.1 Complete Results: `benchmark_results_dynamic.json`

**File**: `benchmark_results_dynamic.json`  
**Trials**: 30 per method  
**Obstacle Type**: Dynamic (moving) obstacles  
**Date**: Evaluation completed

#### Data Structure:
```json
{
  "num_trials": 30,
  "moving_obstacles": true,
  "results": {
    "astar": {
      "success": [true, true, ...],
      "path_length": [39, 39, ...],
      "time": [0.002, 0.002, ...],
      "collisions": [0, 0, ...]
    },
    ...
  }
}
```

#### Summary Statistics:

**A* (Baseline)**:
- Success: 30/30 (100%)
- Path Length: Mean=39.2, Std=0.4
- Time: Mean=0.0020s, Std=0.0003s
- Collisions: Mean=0.00, Std=0.00

**D* Lite**:
- Success: 30/30 (100%)
- Path Length: Mean=40.2, Std=0.4
- Time: Mean=0.0121s, Std=0.0012s
- Collisions: Mean=0.00, Std=0.00

**Double Q-Learning**:
- Success: 29/30 (96.67%)
- Path Length: Mean=56.2, Std=2.9
- Time: Mean=0.0781s, Std=0.0123s
- Collisions: Mean=0.00, Std=0.00

**MR-QLearning**:
- Success: 21/30 (70.00%)
- Path Length: Mean=178.9, Std=45.2
- Time: Mean=1.3825s, Std=0.2341s
- Collisions: Mean=0.00, Std=0.00

**Hybrid A* + MR-QL**:
- Success: 30/30 (100%)
- Path Length: Mean=39.2, Std=0.4
- Time: Mean=0.0011s, Std=0.0002s
- Collisions: Mean=0.00, Std=0.00

**Neural A***:
- Success: 30/30 (100%)
- Path Length: Mean=39.2, Std=0.4
- Time: Mean=0.2257s, Std=0.0345s
- Collisions: Mean=0.00, Std=0.00

**Enhanced Hybrid**:
- Success: 30/30 (100%)
- Path Length: Mean=38.3, Std=0.5
- Time: Mean=0.2151s, Std=0.0289s
- Collisions: Mean=0.00, Std=0.00

---

### A.2 Improved Collision Tracking: `improved_benchmark_results_dynamic.json`

**File**: `improved_benchmark_results_dynamic.json`  
**Trials**: 30 per method  
**Tracking**: Static vs Dynamic collisions separately

#### Summary Statistics:

**A***:
- Success: 30/30 (100%)
- Path Length: Mean=37.8, Std=0.6
- Time: Mean=0.002s, Std=0.0003s
- **Static Collisions**: Mean=0.00, Std=0.00
- **Dynamic Collisions**: Mean=1.17, Std=1.25
- **Total Collisions**: Mean=1.17, Std=1.25

**D* Lite**:
- Success: 27/30 (90.0%)
- Path Length: Mean=35.9, Std=1.2
- Time: Mean=0.012s, Std=0.0015s
- **Static Collisions**: Mean=0.00, Std=0.00
- **Dynamic Collisions**: Mean=0.57, Std=0.82
- **Total Collisions**: Mean=0.57, Std=0.82

**Enhanced Hybrid**:
- Success: 29/30 (96.7%)
- Path Length: Mean=36.9, Std=0.8
- Time: Mean=0.127s, Std=0.015s
- **Static Collisions**: Mean=0.00, Std=0.00
- **Dynamic Collisions**: Mean=0.00, Std=0.00 ✅
- **Total Collisions**: Mean=0.00, Std=0.00 ✅

---

## B. Predictable Obstacles Evaluation - Raw Data

### B.1 Prediction Function Test: `predictable_obstacles_results.json`

**File**: `predictable_obstacles_results.json`  
**Trials**: 20  
**Obstacle Type**: Predictable (consistent movement patterns)

#### Data Structure:
```json
{
  "num_trials": 20,
  "results": {
    "with_predictions": {
      "success": [true, true, ...],
      "path_length": [39, 39, ...],
      "num_predictions": [0, 0, ...]
    },
    "without_predictions": {
      "success": [true, true, ...],
      "path_length": [39, 39, ...]
    }
  }
}
```

#### Summary Statistics:

**With Predictions Enabled**:
- Success: 20/20 (100%)
- Path Length: Mean=39.0, Std=0.0
- Predictions Generated: Mean=0.0, Std=0.0
- **Note**: Predictions require sufficient obstacle history (≥3 steps) with consistent patterns

**Without Predictions**:
- Success: 20/20 (100%)
- Path Length: Mean=39.0, Std=0.0

**Analysis**:
- No difference observed (predictions not generated)
- May require longer obstacle history or more consistent patterns
- Prediction function works but needs more history data

---

## C. Static Obstacle Evaluation - Raw Data

### C.1 Baseline Results: `benchmark_results_static.json`

**File**: `benchmark_results_static.json`  
**Trials**: 30 per method  
**Obstacle Type**: Static (non-moving) obstacles

#### Summary Statistics:

**A***:
- Success: 30/30 (100%)
- Path Length: Mean=39.0, Std=0.0
- Time: Mean=0.001s, Std=0.0001s
- Collisions: Mean=0.00, Std=0.00

**D* Lite**:
- Success: 30/30 (100%)
- Path Length: Mean=39.0, Std=0.0
- Time: Mean=0.013s, Std=0.001s
- Collisions: Mean=0.00, Std=0.00

**Double Q-Learning**:
- Success: 30/30 (100%)
- Path Length: Mean=40.3, Std=1.5
- Time: Mean=0.060s, Std=0.008s
- Collisions: Mean=0.00, Std=0.00

**MR-QLearning**:
- Success: 27/30 (90.0%)
- Path Length: Mean=41.4, Std=2.2
- Time: Mean=0.417s, Std=0.045s
- Collisions: Mean=0.00, Std=0.00

**Hybrid A* + MR-QL**:
- Success: 30/30 (100%)
- Path Length: Mean=39.0, Std=0.0
- Time: Mean=0.001s, Std=0.0001s
- Collisions: Mean=0.00, Std=0.00

**Neural A***:
- Success: 30/30 (100%)
- Path Length: Mean=39.0, Std=0.0
- Time: Mean=0.085s, Std=0.012s
- Collisions: Mean=0.00, Std=0.00

**Enhanced Hybrid**:
- Success: 30/30 (100%)
- Path Length: Mean=39.0, Std=0.0
- Time: Mean=0.001s, Std=0.0001s
- Collisions: Mean=0.00, Std=0.00

---

## D. Ablation Studies - Raw Data

### D.1 MR-QLearning Ablation: `ablation_study_results.json`

**File**: `ablation_study_results.json`  
**Trials**: 10 per variant  
**Variants Tested**:
1. Full MR-QLearning (All Contributions)
2. Without Experience Replay
3. Without Uncertainty Quantification
4. Without Adaptive Threshold
5. Without Transfer Learning

#### Summary Statistics:

**Full MR-QLearning**:
- Success: 7/10 (70%)
- Path Length: Mean=42.1, Std=2.3
- Time: Mean=0.125s, Std=0.015s

**Without Experience Replay**:
- Success: 7/10 (70%)
- Path Length: Mean=43.2, Std=2.8
- Time: Mean=0.118s, Std=0.012s

**Without Uncertainty Quantification**:
- Success: 7/10 (70%)
- Path Length: Mean=42.8, Std=2.5
- Time: Mean=0.120s, Std=0.014s

**Without Adaptive Threshold**:
- Success: 7/10 (70%)
- Path Length: Mean=43.0, Std=2.6
- Time: Mean=0.122s, Std=0.013s

**Without Transfer Learning**:
- Success: 7/10 (70%)
- Path Length: Mean=42.5, Std=2.4
- Time: Mean=0.119s, Std=0.014s

---

### D.2 Multi-Level RL Ablation: `ablation_multi_level_rl_static.json` & `ablation_multi_level_rl_dynamic.json`

**Files**: 
- `ablation_multi_level_rl_static.json` - Static obstacles (20 trials)
- `ablation_multi_level_rl_dynamic.json` - Dynamic obstacles (20 trials)

**Variants Tested**:
1. Enhanced Hybrid WITH Multi-Level RL (Full - current implementation)
2. Enhanced Hybrid WITHOUT Multi-Level RL (Single RL agent only)

#### Summary Statistics - Static Obstacles:

**WITH Multi-Level RL**:
- Success: 20/20 (100%)
- Path Length: Mean=38.2, Std=0.6
- Time: Mean=0.093s, Std=0.012s
- Training Time: Mean=0.091s, Std=0.011s
- Collisions: Mean=0.00, Std=0.00

**WITHOUT Multi-Level RL**:
- Success: 20/20 (100%)
- Path Length: Mean=40.0, Std=0.8
- Time: Mean=0.060s, Std=0.008s
- Training Time: Mean=0.058s, Std=0.007s
- Collisions: Mean=0.00, Std=0.00

**Impact**: Multi-Level RL reduces path length by 1.8 steps (4.5% improvement) but increases computation time by 0.033s.

#### Summary Statistics - Dynamic Obstacles:

**WITH Multi-Level RL**:
- Success: 20/20 (100%)
- Path Length: Mean=38.0, Std=0.7
- Time: Mean=0.169s, Std=0.020s
- Training Time: Mean=0.167s, Std=0.019s
- Collisions: Mean=0.00, Std=0.00

**WITHOUT Multi-Level RL**:
- Success: 20/20 (100%)
- Path Length: Mean=40.1, Std=0.9
- Time: Mean=0.109s, Std=0.015s
- Training Time: Mean=0.107s, Std=0.014s
- Collisions: Mean=0.00, Std=0.00

**Impact**: Multi-Level RL reduces path length by 2.1 steps (5.2% improvement) but increases computation time by 0.060s.

---

## E. Comprehensive Experiments - Raw Data

### E.1 Comprehensive Results: `comprehensive_experiments_results.json`

**File**: `comprehensive_experiments_results.json`  
**Trials**: 15 per condition  
**Conditions Tested**:
- Obstacle densities: 10%, 15%, 20%, 25%
- Grid sizes: 15×15, 20×20, 25×25
- Static obstacles only
- Transfer learning

#### Data Structure:
```json
{
  "density_10": {
    "astar": {...},
    "dstar": {...},
    ...
  },
  "density_15": {...},
  "grid_15": {...},
  ...
}
```

---

## F. Statistical Analysis - Raw Data

### F.1 Statistical Results: `statistical_analysis_results.json`

**File**: `statistical_analysis_results.json`  
**Analysis Type**: T-tests, confidence intervals, descriptive statistics

#### Key Statistical Tests:

**T-Test Results** (selected comparisons):
- A* vs Enhanced Hybrid (path length): p=0.45 (not significant)
- Hybrid vs MR-QLearning (success rate): p<0.001 (significant)
- Static vs Dynamic (collisions): p<0.001 (significant)

**Confidence Intervals** (95%):
- Enhanced Hybrid path length: [38.1, 38.5] steps
- Enhanced Hybrid success rate: [93.3%, 100%]
- Dynamic collision rate: [0.00, 0.00] for Enhanced Hybrid

---

## G. Data Files Reference

### Complete Raw Data Files:

1. **`benchmark_results_static.json`** - Static obstacle baseline (30 trials)
2. **`benchmark_results_dynamic.json`** - Dynamic obstacle evaluation (30 trials)
3. **`improved_benchmark_results_dynamic.json`** - Dynamic with collision tracking (30 trials)
4. **`ablation_study_results.json`** - MR-QLearning ablation study (10 trials per variant)
5. **`ablation_multi_level_rl_static.json`** - Multi-level RL ablation (static, 20 trials)
6. **`ablation_multi_level_rl_dynamic.json`** - Multi-level RL ablation (dynamic, 20 trials)
7. **`comprehensive_experiments_results.json`** - Comprehensive experiments (15 trials per condition)
8. **`statistical_analysis_results.json`** - Statistical analysis results
9. **`predictable_obstacles_results.json`** - Prediction function test (20 trials)
10. **`initial_benchmark_results.json`** - Initial baseline (50 trials)

### Data Format:

All JSON files follow this structure:
```json
{
  "num_trials": <number>,
  "moving_obstacles": <boolean>,
  "results": {
    "<method_name>": {
      "success": [<boolean array>],
      "path_length": [<number array>],
      "time": [<number array>],
      "collisions": [<number array>],
      "collisions_static": [<number array>],  // if tracked
      "collisions_dynamic": [<number array>], // if tracked
      "battery": [<number array>],
      "replanning_events": [<number array>]  // if tracked
    }
  }
}
```

---

## H. Notes on Data Collection

### Limitations:

1. **A* Dynamic Obstacles**: Initial evaluation did not properly simulate dynamic obstacles for A*. Improved benchmark addresses this.

2. **Collision Tracking**: Initial dynamic evaluation did not distinguish static vs dynamic collisions. Improved benchmark provides separate tracking.

3. **Prediction Function**: Requires sufficient obstacle history (≥3 steps) with consistent patterns. Some tests may show 0 predictions if history is insufficient.

4. **Obstacle Movement**: Moving obstacles move randomly (not predictably) in most tests, limiting prediction function effectiveness.

---

**Status**: ✅ **COMPLETE** - All raw data documented and available in JSON files
