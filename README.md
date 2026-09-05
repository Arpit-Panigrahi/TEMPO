<div align="center">

# TEMPO
### Tactical Emergence & Multi-agent Predictive Orchestrator

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Optical Tracking](https://img.shields.io/badge/Data-Metrica%20Sports%20(25%20FPS)-purple.svg)]()
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

## 🚀 Quickstart: Launching the TEMPO Tactical Studio

TEMPO includes a full-stack, interactive **Tactical Studio Web Application** designed for match analysts and coaching staffs:

### 1. Launch the Studio
```bash
python3 run_studio.py
```
Open your browser at **[http://localhost:8000](http://localhost:8000)**.

### Features in the Studio:
- **60 FPS Interactive Pitch Canvas:** 22 players with numbers, velocity trails, ball physics, and real-time defensive convex hull.
- **Dynamic Domino Threat Gauge:** Real-time structural collapse meter updating frame-by-frame.
- **Causal Root Inspector:** Pinpoints the exact defender who broke the line (e.g. Defender #21) with quantitative diagnostic.
- **🔀 Counterfactual "What-If" Switch:** One click switches the replay to a simulated counterfactual where the defense stays disciplined and shuts down the goal!
- **📋 What-If Tactical Dossier & Drills:** Step-by-step causal cascade breakdown, mathematical proof grid, and pitch-side corrective training drills.
- **✨ Gemini AI Tactical Narrator:** On-demand lucid debrief generation powered by Google Gemini (`gemini-2.5-flash`) with seamless zero-dependency REST integration and automated heuristic fallback.
- **Match Episode Navigator:** Dropdown selector to inspect all indexed goals and transition shots from Metrica Game 1.


---

## 🧪 Real Match Case Study & Testing

### Run the Real-Match Analysis
Analyzes Metrica Sports Game 1, Goal 2 (Period 2, 60:00 counter-press transition):
```bash
PYTHONPATH=src python3 scripts/analyze_real_goal.py
```
- **Output:** Identifies Domino Moment at $t = 3595.9\text{s}$ (**4.28s lead time** before shot), isolates Away Defender #21, and generates multi-panel figure in `outputs/real_match_goal2_domino_analysis.png`.

### Run Verification Test Suite
```bash
PYTHONPATH=src python3 tests/test_metrica_pipeline.py
```

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

## 🏛️ Repository Architecture

```text
TEMPO/
├── run_studio.py                                      # One-command Studio launcher (FastAPI + Uvicorn)
├── README.md                                          # Executive documentation & specs
├── requirements.txt                                   # Clean scientific dependencies
├── pyproject.toml                                     # Standard Python package build spec
├── .gitignore                                         # Git ignore rules for tracking data
│
├── app/                                               # Full-Stack Tactical Studio Web App
│   ├── server.py                                      # FastAPI REST API & static server
│   └── static/                                        # Frontend UI assets
│       ├── index.html                                 # Studio dashboard layout
│       ├── studio.css                                 # Dark-mode tactical styling
│       └── studio.js                                  # 60 FPS HTML5 Canvas engine
│
├── docs/                                              # Comprehensive Research & Technical Specs
│   ├── TEMPO_Research_Vision_Document.md              # Authoritative 3,700+ line Master Vision
│   ├── TEMPO_Master_Architecture_And_Tactical_Vision.md
│   ├── TEMPO_Low_Resource_Local_To_Cloud_Engineering_Guide.md # Local-to-Cloud engineering manual
│   ├── tactics/                                       # Football Tactics Masterclass
│   └── enterprise/                                    # Tier-1 Premier League / Champions League workflows
│
├── src/tempo/                                         # Core Analytics & Intelligence Package
│   ├── __init__.py
│   ├── data/                                          # Real-match optical tracking & cataloging
│   │   ├── metrica_io.py                              # 25 FPS tracking parser & kinematic filter
│   │   └── episode_catalog.py                         # Match episode indexer & JSON packager
│   ├── analytics/                                     # Spatial & physics-based models
│   │   ├── __init__.py
│   │   └── pitch_control.py                           # William Spearman (2018) PPCF Engine
│   ├── causal/                                        # Causal inference engine
│   │   ├── __init__.py
│   │   └── scm_domino.py                              # Structural Causal Model & Counterfactuals
│   ├── geometry/                                      # Pitch dimensions, convex hulls, Voronoi
│   │   └── pitch.py
│   └── viz/                                           # FIFA pitch visualizers
│       └── pitch_plotter.py
│
├── scripts/                                           # Analytical Scripts & Case Studies
│   └── analyze_real_goal.py                           # Metrica Game 1 Goal 2 SCM case study
│
├── tests/                                             # Automated Test Suites
│   └── test_metrica_pipeline.py                       # 100% green verification tests
│
└── outputs/                                           # Generated figures, tables, and artifacts
    └── real_match_goal2_domino_analysis.png           # 3-panel publication visual
```

---

## 💻 Low-Resource Engineering Philosophy

TEMPO runs 100% locally on standard consumer CPUs without requiring an expensive GPU:
- **Pitch Control Engine:** Computes full 2D spatial dominance grid in **2.5 ms/frame**.
- **Interactive UI:** Smooth 60 FPS canvas rendering directly in any modern web browser.
- **In-Memory Caching:** Episode catalog queries return in **< 5 ms**.

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
