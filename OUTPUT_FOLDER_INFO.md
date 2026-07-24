# Output Folder Information

## Current Status

The `outputs/` folder exists but is **empty** because:

1. **Folder is Created**: The folder is created in `in testing environment.txt`:
   ```python
   OUTPUT_DIR = os.path.join(os.getcwd(), 'outputs')
   os.makedirs(OUTPUT_DIR, exist_ok=True)
   ```

2. **Not Actually Used**: Despite being created, **no code actually saves files to this folder**. All output files are saved directly to the project root directory instead.

## Where Files Are Actually Saved

All result files are currently saved to the **root directory** of the project:

### Result JSON Files (in root directory):
- `ablation_study_results.json`
- `comprehensive_experiments_results.json`
- `statistical_analysis_results.json`
- `benchmark_results_static.json`
- `initial_benchmark_results.json`
- `same_env_comprehensive_results.json`

### Visualization Files (in `visualizations/` folder):
- `visualizations/success_rate_bar.png`
- `visualizations/path_length_bar.png`
- `visualizations/path_length_boxplot.png`
- `visualizations/obstacle_density_heatmap.png`

### Thesis Figures (in `thesis_figures/` folder):
- `thesis_figures/Figure_1_System_Architecture.png`
- `thesis_figures/Figure_2_MR_QLearning_Flowchart.png`
- ... (10 figures total)

## Why It's Empty

The `outputs/` folder appears to be:
- **Intended for future use** but never implemented
- **Legacy code** that was planned but not completed
- **Windows-specific** (as noted in the comment: "Windows-specific output directory")

## Recommendation

You have two options:

1. **Delete the empty folder** if it's not needed
2. **Update the code** to actually use it for organizing output files

If you want to use the `outputs/` folder, you would need to update scripts like:
- `statistical_analysis.py` - Change `"statistical_analysis_results.json"` to `os.path.join(OUTPUT_DIR, "statistical_analysis_results.json")`
- `benchmark_comparison.py` - Update file paths
- `ablation_study.py` - Update file paths
- Other scripts that save results

---

**Status**: Folder exists but unused - all outputs go to root directory or specific subdirectories (`visualizations/`, `thesis_figures/`)

