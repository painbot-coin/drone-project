# Thesis Figures and Flowcharts

This directory contains all figures and flowcharts generated for the thesis document. All figures are saved at 300 DPI for high-quality publication.

## Generated Figures

### 1. Figure_1_System_Architecture.png
**Title:** System Architecture for Autonomous Drone Path Planning

**Description:** 
- Shows the overall system architecture with three main components:
  - MR-QLearning (4 novel contributions)
  - Enhanced Hybrid A* + RL (5 RL innovations)
  - Battery-Aware & Adaptive Navigation
- Illustrates the flow from environment input to path output
- Includes comparison methods section

**Use in Thesis:** Chapter 3 (Methodology), Section 3.1 (System Overview)

---

### 2. Figure_2_MR_QLearning_Flowchart.png
**Title:** MR-QLearning Algorithm Flowchart

**Description:**
- Detailed flowchart of the MR-QLearning training algorithm
- Shows the complete training loop with:
  - Experience replay mechanism
  - Uncertainty quantification
  - Adaptive threshold adjustment
  - Q-value updates
- Highlights all 4 novel contributions

**Use in Thesis:** Chapter 3 (Methodology), Section 3.2 (MR-QLearning Algorithm)

---

### 3. Figure_3_Hybrid_System_Flowchart.png
**Title:** Enhanced Hybrid A* + RL System Flowchart

**Description:**
- Complete workflow of the hybrid system
- Shows:
  - Initialization and training of multiple RL agents
  - A* global planning with RL-guided heuristic
  - Confidence-based switching between RL and A*
  - Obstacle prediction and path refinement
- Illustrates all 5 RL innovations

**Use in Thesis:** Chapter 3 (Methodology), Section 3.3 (Enhanced Hybrid A* + RL)

---

### 4. Figure_4_Confidence_Switching.png
**Title:** Confidence-Aware Hybrid Switching Mechanism

**Description:**
- Detailed diagram of the confidence calculation and switching logic
- Shows:
  - Multi-factor confidence calculation
  - Adaptive threshold comparison
  - Decision flow (High confidence → RL, Low confidence → A*)
- Explains the three confidence factors (visits, variance, magnitude)

**Use in Thesis:** Chapter 3 (Methodology), Section 3.2.3 (Uncertainty Quantification) or 3.3.1 (Hybrid Architecture)

---

### 5. Figure_5_Training_Workflow.png
**Title:** Training Workflow with Experience Replay

**Description:**
- Illustrates the experience replay mechanism
- Shows:
  - Multiple episodes contributing to replay buffer
  - Random batch sampling process
  - Q-value updates from batches
  - Benefits of experience replay

**Use in Thesis:** Chapter 3 (Methodology), Section 3.2.2 (Experience Replay Buffer)

---

### 6. Figure_6_Experimental_Methodology.png
**Title:** Experimental Methodology and Evaluation Framework

**Description:**
- Complete experimental setup diagram
- Shows:
  - Test environments (grid sizes, obstacle densities)
  - Methods under test (A*, D* Lite, Double Q-Learning, MR-QLearning, Hybrid)
  - Evaluation metrics (Success Rate, Path Length, Time, Collisions, Battery)
  - Three experimental phases (Baseline, Ablation, Transfer Learning)
  - Results analysis pipeline

**Use in Thesis:** Chapter 4 (Experiments), Section 4.1 (Experimental Setup)

---

### 7. Figure_7_Uncertainty_Quantification.png
**Title:** Uncertainty Quantification Mechanism

**Description:**
- Detailed breakdown of uncertainty quantification
- Shows:
  - Q-value history tracking
  - Variance calculation
  - Visit count tracking
  - Q-value magnitude
  - Multi-factor confidence score formula
- Includes a small plot showing Q-value evolution over time

**Use in Thesis:** Chapter 3 (Methodology), Section 3.2.3 (Uncertainty Quantification)

---

### 8. Figure_8_Comparison_Framework.png
**Title:** Method Comparison Framework

**Description:**
- Visual comparison framework showing:
  - All methods being compared
  - Evaluation metrics
  - Performance comparison matrix
  - Key features of each method

**Use in Thesis:** Chapter 4 (Experiments), Section 4.2 (Comparison Results)

---

### 9. Figure_9_Ablation_Study.png
**Title:** Ablation Study Design

**Description:**
- Shows the ablation study methodology
- Illustrates:
  - Full system with all contributions
  - Four variants (removing each contribution)
  - Performance impact measurement
- Demonstrates the importance of each novel contribution

**Use in Thesis:** Chapter 4 (Experiments), Section 4.3 (Ablation Study)

---

### 10. Figure_10_Transfer_Learning.png
**Title:** Transfer Learning Framework

**Description:**
- Complete transfer learning workflow
- Shows:
  - Source environment training
  - Q-table export
  - Compatibility check
  - Target environment transfer
  - Fine-tuning process
  - Benefits of transfer learning

**Use in Thesis:** Chapter 3 (Methodology), Section 3.2.5 (Transfer Learning) or Chapter 4 (Experiments), Section 4.4 (Transfer Learning Experiments)

---

## Figure Specifications

- **Resolution:** 300 DPI (suitable for high-quality printing)
- **Format:** PNG (with transparency support)
- **Color Scheme:** Professional color palette with consistent styling
- **Font Size:** Optimized for readability in thesis format

## Usage in LaTeX/Word

### LaTeX:
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.9\textwidth]{thesis_figures/Figure_1_System_Architecture.png}
    \caption{System Architecture for Autonomous Drone Path Planning}
    \label{fig:system_architecture}
\end{figure}
```

### Word:
1. Insert → Pictures → This Device
2. Select the figure file
3. Right-click → Format Picture → Layout → In Line with Text (or Square)
4. Add caption using References → Insert Caption

## Notes

- All figures use consistent color coding:
  - Blue: Primary components (MR-QLearning)
  - Purple: Secondary components (Hybrid system)
  - Orange: Accent/Important elements
  - Green: Success/Output
  - Red: Warnings/Decisions
  - Gray: Neutral/Baseline

- Subscript characters (s₁, s₂, etc.) may show warnings but render correctly in most viewers
- All arrows and connections are clearly labeled
- Text is sized for readability in printed format

## Regenerating Figures

To regenerate all figures, run:
```bash
python generate_thesis_figures.py
```

Make sure matplotlib and numpy are installed:
```bash
pip install matplotlib numpy
```

---

**Generated:** $(Get-Date -Format "yyyy-MM-dd")
**Total Figures:** 10
**Purpose:** Master's Thesis - Real-Time Path Planning for Autonomous Drones
