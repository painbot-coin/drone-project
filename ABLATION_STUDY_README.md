# Ablation Study Script

## Purpose
Tests MR-QLearning with each novel contribution removed to show individual impact.

## Variants Tested
1. **Full MR-QLearning** (All Contributions) - Baseline
2. **Without Experience Replay** - Tests impact of replay buffer
3. **Without Uncertainty Quantification** - Tests impact of variance-based confidence
4. **Without Adaptive Threshold** - Tests impact of threshold learning
5. **Without Transfer Learning** - Tests impact of Q-table reuse

## Usage

### Fast Mode (Recommended):
```bash
python ablation_study.py
```
- 10 trials per variant (50 total runs)
- 100 episodes per training
- ~15-20 seconds execution time

### To Run More Trials:
Edit `ablation_study.py` and change:
```python
study = AblationStudy(num_trials=20, fast_mode=True)  # Increase trials
```

## Output
- Console: Summary table and comparisons
- JSON: `ablation_study_results.json` with all raw data

## What It Shows
- Impact of removing each contribution
- Comparison against full method
- Success rate differences
- Path length differences
- Which contributions matter most

## Note
The study takes time because each variant needs to train. For faster results, use fewer trials or run in background.

