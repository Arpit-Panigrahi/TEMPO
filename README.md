<div align="center">

# TEMPO
### Tactical Emergence & Multi-agent Predictive Orchestrator

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Research Track](https://img.shields.io/badge/Research-KDD%20%7C%20MIT%20Sloan%20%7C%20CVPR-purple.svg)]()
[![Hardware: CPU Friendly](https://img.shields.io/badge/Compute-Low--Resource%20CPU%20Ready-brightgreen.svg)]()
[![Documentation](https://img.shields.io/badge/Docs-Authoritative%20Specs%20(3700%2B%20lines)-orange.svg)](docs/TEMPO_Research_Vision_Document.md)

**Detecting Domino Moments, Dynamic Affordance Manifolds, and Causal Roots in Multi-Agent Football Dynamics**

</div>

---

## 📌 Executive Summary

Modern football analytics (xG, EPV, VAEP, possession values) overwhelmingly focus on the **terminal moment of threat** (the shot or the final line-breaking pass). However, football defensive systems collapse **3 to 7 seconds earlier**—triggered when a single defender steps out of shape, overcommits to a decoy run, or hesitates by mere centimeters. 

This initial structural break triggers a catastrophic chain reaction: adjacent defenders hesitate, defensive compact hulls stretch, and passing corridors burst open.

**TEMPO** (**T**actical **E**mergence & **M**ulti-agent **P**redictive **O**rchestrator) is a spatiotemporal causal intelligence platform designed to:
1. **Detect Domino Moments ($\tau_{\text{domino}}$)** seconds before conventional threat metrics register danger.
2. **Isolate the Causal Root Player ($k^*$)** responsible for initiating the structural rupture.
3. **Simulate Counterfactual Interventions**: *"What if the defender had held their zonal anchor instead of biting on the decoy run?"*

---

## 📐 Mathematical Formulation

### 1. Structural Breakdown Index $\mathcal{S}(t)$
At each frame $t$, the defensive structural cohesion is quantified via a composite spatiotemporal manifold:
$$\mathcal{S}(t) = w_1 \cdot \frac{\text{Var}(X_{\text{backline}})}{\sigma_0^2} + w_2 \cdot \frac{\text{Gap}_{\text{aperture}}(t)}{d_0} + w_3 \cdot \frac{\text{Area}_{\text{hull}}(t)}{\text{Area}_{\text{baseline}}} + w_4 \cdot \mathcal{V}_{\text{threat}}(t)$$

### 2. Domino Moment Detection Criterion
The Domino Moment $\tau_{\text{domino}}$ is defined as the temporal supremum of the breakdown acceleration within the predictive lead window preceding terminal threat $t_{\text{threat}}$:
$$\tau_{\text{domino}} = \arg\max_{t \in [t_{\text{threat}} - \Delta t_{\max},\, t_{\text{threat}} - \Delta t_{\min}]} \left[ \frac{\partial \mathcal{S}(t)}{\partial t} \right]$$

### 3. Causal Root-Cause Attribution
The primary causal agent $k^*$ initiating the cascade is extracted via spatiotemporal gradient divergence from their zonal equilibrium anchor:
$$k^* = \arg\max_{i \in \text{Defenders}} \left[ \left\| \mathbf{x}_i(\tau_{\text{domino}}) - \mathbf{x}_i^{\text{anchor}} \right\| \cdot \left( \|\mathbf{v}_i(\tau_{\text{domino}})\| + \epsilon \right) \right]$$

### 4. Counterfactual Conceded Risk Mitigation ($\Delta \mathcal{R}$)
Replacing $k^*$'s empirical path with a counterfactual anchor policy $\mathbf{x}_{k^*}^{\text{CF}}(t)$ reveals the causal impact on structural risk:
$$\Delta \mathcal{R} = \frac{\mathcal{S}_{\text{actual}}(t_{\text{threat}}) - \mathcal{S}_{\text{CF}}(t_{\text{threat}})}{\mathcal{S}_{\text{actual}}(t_{\text{threat}})} \times 100\%$$

---

## 🚀 Quickstart (30-Second Local CPU Reproduction)

TEMPO is designed with **zero bloat**: the core pilot experiment runs 100% locally on any standard consumer laptop CPU in **under 5 seconds** without requiring a GPU.

### 1. Clone & Install
```bash
git clone https://github.com/Arpit-Panigrahi/TEMPO.git
cd TEMPO
pip install -r requirements.txt
```

### 2. Run the Flagship Paper #1 Pilot Experiment
```bash
PYTHONPATH=src python3 experiments/paper1_domino_pilot.py
```

### Output:
```text
======================================================================
  TEMPO: Tactical Emergence & Multi-agent Predictive Orchestrator
  Paper #1 Pilot Experiment: Domino Moment & Causal Root Attribution
======================================================================
[*] Generating 15.0s high-press multi-agent tracking dynamics (FPS=10.0)...
[*] Threat event (line-breaking pass) occurs at frame 120 (t = 12.00s).
[*] Computing Spatiotemporal Structural Breakdown Index S(t)...

[+] RESULTS FOUND:
    - Domino Moment Detected at Frame: 90 (t = 9.00s)
    - Threat Event at Frame:           120 (t = 12.00s)
    - Early Predictive Lead Time:       tau_lead = 3.00 seconds
    - Identified Causal Root Agent:     Defender #2 (LCB / Center-Back)

[*] Simulating Counterfactual Intervention (holding zonal anchor)...
    - Actual Structural Breakdown at Threat:  1.234
    - Counterfactual Breakdown at Threat:     0.433
    - Causal Risk Reduction Achieved:         64.9%

[*] Rendering Publication-Quality Figure 1...
[SUCCESS] Figure saved to: outputs/domino_moment_pilot.png
======================================================================
```

### 3. Run Unit Tests
```bash
PYTHONPATH=src python3 tests/test_domino.py
```

---

## 📊 Flagship Pilot Experiment (Figure 1)

The pilot experiment automatically synthesizes a high-press transition breakdown, executes causal attribution, and generates a publication-ready 2-panel figure in `outputs/domino_moment_pilot.png`:

- **Panel A (Tactical State at $\tau_{\text{domino}}$):** Full 105m $\times$ 68m FIFA pitch visualization illustrating the attacking build-up, the decoy run pulling the center-back out of shape, the golden highlight of causal root Defender #2, the counterfactual anchor ($\mathbf{X}$), and the cascading pressure onto adjacent defenders.
- **Panel B (Temporal Breakdown Dynamics):** Evolution of the Structural Breakdown Index $\mathcal{S}(t)$ vs the Counterfactual trajectory $\mathcal{S}_{\text{CF}}(t)$, highlighting the critical early warning lead time window ($\tau_{\text{lead}} = 3.0\text{s}$).

---

## 🏛️ Repository Architecture

```text
TEMPO/
├── README.md                                          # Executive README & Quickstart
├── requirements.txt                                   # Minimal CPU-friendly dependencies
├── pyproject.toml                                     # Standard Python package build spec
├── .gitignore                                         # Git ignore rules for tracking data
│
├── docs/                                              # Comprehensive Research & Technical Specs
│   ├── TEMPO_Research_Vision_Document.md              # Authoritative 3,700+ line Master Vision
│   ├── TEMPO_Master_Architecture_And_Tactical_Vision.md
│   ├── TEMPO_Low_Resource_Local_To_Cloud_Engineering_Guide.md # Local-to-Cloud engineering manual
│   ├── tactics/                                       # Complete Football Tactics Masterclass
│   │   ├── FCIE_Football_Tactics_Masterclass_Complete.md
│   │   ├── FCIE_Football_Tactics_Masterclass_Part1.md
│   │   └── FCIE_Football_Tactics_Masterclass_Part2.md
│   └── enterprise/                                    # Tier-1 Premier League / Champions League workflows
│       └── FCIE_Tier1_Club_Enterprise_Architecture.md
│
├── src/tempo/                                         # Core Python Package
│   ├── __init__.py
│   ├── geometry/                                      # Pitch metrics, convex hulls, Voronoi fields
│   │   ├── __init__.py
│   │   └── pitch.py
│   ├── causal/                                        # Domino detector & counterfactual engine
│   │   ├── __init__.py
│   │   └── domino.py
│   ├── data/                                          # High-fidelity tracking & Metrica data loaders
│   │   ├── __init__.py
│   │   └── synthetic_transition.py
│   └── viz/                                           # Matplotlib pitch & cascade visualizers
│       ├── __init__.py
│       └── pitch_plotter.py
│
├── experiments/                                       # Academic Experiments & Paper Benchmarks
│   └── paper1_domino_pilot.py                         # Flagship Figure 1 generator
│
├── tests/                                             # Fast, zero-dependency unit tests
│   └── test_domino.py
│
└── outputs/                                           # Generated figures, tables, and artifacts
    └── domino_moment_pilot.png
```

---

## 🔬 Academic Roadmap: The 3-Paper Strategy

TEMPO is developed following a rigorous vertical publication strategy:

1. **Paper #1 (Core Causal Foundation):**  
   *"TEMPO: Detecting Domino Moments and Causal Roots in Multi-Agent Football Dynamics"*  
   - **Focus:** Spatiotemporal graph representation, $\tau_{\text{domino}}$ lead time detection, counterfactual defensive mitigation on open-source Metrica & SkillCorner data.  
   - **Target Venues:** KDD Sports Analytics, MIT Sloan Sports Analytics Conference (SSAC), CVPR CVSports.

2. **Paper #2 (Dynamic Action Manifolds):**  
   *"Affordance Manifolds in Elite Football: Quantifying Counter-Press Resistance Under High Press Systems"*  
   - **Focus:** Micro-affordance zones ($\mathcal{A}_i$), De Zerbi sole-on-ball provocation, Kompany high-line rest-defense.

3. **Paper #3 (Multi-Agent RL & Club Systems):**  
   *"TEMPO-Orchestrator: Generative Counterfactual Simulation for Match Preparation in Tier-1 Clubs"*  
   - **Focus:** Multi-agent PPO/MAPPO tactical simulations, matchday briefings, automated video sync.

---

## 💻 Low-Resource Engineering Philosophy

You do **not** need expensive GPU clusters to reproduce or contribute to TEMPO:
- **Local Stage (Consumer CPU):** DuckDB + Polars for sub-second parquet querying; NumPy and SciPy for Voronoi and convex hulls.
- **Cloud Scaling ($0.35/hour):** Seamless transition to Google Colab, Kaggle, or Modal/RunPod for scaled spatiotemporal GNN training when processing 100+ match seasons.
- Detailed scaling instructions are documented in [docs/TEMPO_Low_Resource_Local_To_Cloud_Engineering_Guide.md](docs/TEMPO_Low_Resource_Local_To_Cloud_Engineering_Guide.md).

---

## 📜 Citation

If you use TEMPO in your research or tactical analysis, please cite:

```bibtex
@article{panigrahi2026tempo,
  title={TEMPO: Detecting Domino Moments and Causal Roots in Multi-Agent Football Dynamics},
  author={Panigrahi, Arpit},
  journal={arXiv preprint},
  year={2026}
}
```

---

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.
