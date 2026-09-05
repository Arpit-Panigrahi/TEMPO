#!/usr/bin/env python3
"""
TEMPO Paper #1 Pilot Experiment:
Detecting Domino Moments and Causal Roots in Multi-Agent Football Dynamics.

This script executes the complete minimal viable pipeline for Paper #1:
1. Simulates/Loads spatiotemporal tracking frames.
2. Identifies the exact Domino Moment (tau_domino) preceding defensive failure.
3. Isolates the causal root-cause agent (defender) using spatiotemporal gradient attribution.
4. Simulates a counterfactual intervention where the agent preserves zonal integrity.
5. Produces Figure 1 of Paper #1 and outputs quantitative metrics.
"""

import sys
import os
from pathlib import Path

# Add src to python path so tempo can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import matplotlib.pyplot as plt
from tempo.data.synthetic_transition import generate_press_break_sequence
from tempo.causal.domino import DominoDetector
from tempo.viz.pitch_plotter import plot_domino_frame


def run_experiment():
    print("=" * 70)
    print("  TEMPO: Tactical Emergence & Multi-agent Predictive Orchestrator")
    print("  Paper #1 Pilot Experiment: Domino Moment & Causal Root Attribution")
    print("=" * 70)

    fps = 10.0
    print(f"[*] Generating 15.0s high-press multi-agent tracking dynamics (FPS={fps})...")
    data = generate_press_break_sequence(num_seconds=15.0, fps=fps, seed=42)
    def_traj = data["def_trajectories"]
    att_traj = data["att_trajectories"]
    ball_traj = data["ball_trajectory"]
    threat_frame = data["threat_frame"]

    print(f"[*] Threat event (line-breaking pass) occurs at frame {threat_frame} (t = {threat_frame / fps:.2f}s).")

    # Initialize Domino Detector
    detector = DominoDetector(fps=fps, baseline_area=620.0, lead_time_min_sec=2.0, lead_time_max_sec=6.5)
    
    # Detect Domino Moment
    print("[*] Computing Spatiotemporal Structural Breakdown Index S(t)...")
    res = detector.detect_domino_moment(def_traj, ball_traj, att_traj, threat_frame)
    
    domino_frame = res["domino_frame"]
    lead_time = res["lead_time_sec"]
    root_idx = res["causal_root_idx"]
    scores = res["structural_scores"]

    print(f"\n[+] RESULTS FOUND:")
    print(f"    - Domino Moment Detected at Frame: {domino_frame} (t = {domino_frame / fps:.2f}s)")
    print(f"    - Threat Event at Frame:           {threat_frame} (t = {threat_frame / fps:.2f}s)")
    print(f"    - Early Predictive Lead Time:       tau_lead = {lead_time:.2f} seconds")
    print(f"    - Identified Causal Root Agent:     Defender #{root_idx} (LCB / Center-Back)")

    # Run Counterfactual Intervention
    print("\n[*] Simulating Counterfactual Intervention (holding zonal anchor)...")
    cf_scores, cf_def_traj = detector.simulate_counterfactual(
        def_traj, ball_traj, att_traj, domino_frame, root_idx, damping_factor=0.70
    )

    actual_collapse_peak = float(scores[threat_frame])
    cf_collapse_peak = float(cf_scores[threat_frame])
    risk_reduction = (actual_collapse_peak - cf_collapse_peak) / actual_collapse_peak * 100.0

    print(f"    - Actual Structural Breakdown at Threat:  {actual_collapse_peak:.3f}")
    print(f"    - Counterfactual Breakdown at Threat:     {cf_collapse_peak:.3f}")
    print(f"    - Causal Risk Reduction Achieved:         {risk_reduction:.1f}%\n")

    # Generate Figure 1 (2-panel academic visualization)
    print("[*] Rendering Publication-Quality Figure 1...")
    fig = plt.figure(figsize=(15, 10), facecolor="#0e1717")

    # Panel A: Tactical Pitch Visualization at tau_domino
    ax1 = fig.add_subplot(2, 1, 1)
    plot_domino_frame(
        ax=ax1,
        att_pos=att_traj[domino_frame],
        def_pos=def_traj[domino_frame],
        ball_pos=ball_traj[domino_frame],
        causal_root_idx=root_idx,
        cascade_indices=[6],  # LCM affected
        cf_root_pos=cf_def_traj[domino_frame, root_idx],
        title=f"(A) Tactical State at Domino Moment tau = {domino_frame / fps:.2f}s (Lead Time: {lead_time:.2f}s before Threat)"
    )

    # Panel B: Time-Series of Structural Breakdown Index
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_facecolor("#1a2421")
    time_axis = np.arange(len(scores)) / fps

    ax2.plot(time_axis, scores, color="#ff4d4f", lw=2.5, label="Actual Observed Trajectory S(t)")
    ax2.plot(time_axis, cf_scores, color="#1dd1a1", lw=2.5, linestyle="--", label="Counterfactual Intervened Trajectory S_cf(t)")

    # Vertical markers
    ax2.axvline(domino_frame / fps, color="#feca57", linestyle=":", lw=2.2, label=f"tau_domino ({domino_frame / fps:.1f}s)")
    ax2.axvline(threat_frame / fps, color="#ff3838", linestyle="-.", lw=2.2, label=f"Penetrating Pass Threat ({threat_frame / fps:.1f}s)")

    # Lead time annotation band
    ax2.axvspan(domino_frame / fps, threat_frame / fps, color="#feca57", alpha=0.10, label=f"Early Lead Window (Delta t = {lead_time:.1f}s)")

    ax2.set_xlim(0, max(time_axis))
    ax2.set_xlabel("Match Sequence Time (seconds)", color="#ffffff", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Defensive Structural Breakdown Index S(t)", color="#ffffff", fontsize=11, fontweight="bold")
    ax2.set_title("(B) Temporal Evolution of Structural Breakdown and Counterfactual Divergence", color="#ffffff", fontsize=12, fontweight="bold", pad=10)
    
    ax2.tick_params(colors="#c8d6e5")
    for spine in ax2.spines.values():
        spine.set_color("#576574")
    ax2.grid(True, linestyle="--", alpha=0.2, color="#ffffff")
    ax2.legend(loc="upper left", facecolor="#222f3e", edgecolor="#576574", labelcolor="#c8d6e5", fontsize=9.5)

    plt.tight_layout()
    output_path = Path(__file__).resolve().parent.parent / "outputs" / "domino_moment_pilot.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    print(f"[SUCCESS] Figure saved to: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
