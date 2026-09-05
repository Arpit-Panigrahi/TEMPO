#!/usr/bin/env python3
"""
TEMPO Enterprise Real-Match Analytics Case Study:
Analysis of Metrica Sports Game 1, Goal 2 (Period 2, t = 3600.2s).

Demonstrates:
1. Ingestion of real stadium optical tracking (25 Hz).
2. Physics-based Pitch Control Field (Spearman 2018 model).
3. Structural Causal Model (SCM) Domino Moment Detection.
4. Identification of the Causal Root Defender.
5. Counterfactual Simulation & Risk Reduction.
"""

import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import matplotlib.pyplot as plt
from tempo.data.metrica_io import MetricaLoader, PITCH_LENGTH, PITCH_WIDTH
from tempo.analytics.pitch_control import PitchControlEngine
from tempo.causal.scm_domino import SCMDominoDetector
from tempo.viz.pitch_plotter import draw_pitch
from scipy.spatial import ConvexHull


def run_real_goal_analysis():
    print("=" * 78)
    print("  TEMPO ENTERPRISE TACTICAL ENGINE: REAL MATCH CAUSAL CASE STUDY")
    print("  Match: Metrica Sports Game 1 | Event: Goal 2 (Period 2, t = 3600.2s)")
    print("=" * 78)

    loader = MetricaLoader("data/metrica")
    print("[*] Loading real match events and optical tracking stream (25 FPS)...")
    
    # Goal 2 occurs at event_index = 1
    # Extract 10.0 seconds before goal to 1.0s after
    ep = loader.extract_goal_episode(event_index=1, pre_event_seconds=10.0, post_event_seconds=1.0)
    print(f"[+] Loaded Tactical Episode:")
    print(f"    - Period: {ep.period} | Frame Window: {ep.start_frame} -> {ep.end_frame} ({len(ep.home_coords)} frames)")
    print(f"    - Scorer: {ep.event_meta['from_player']} | Subtype: {ep.event_meta['subtype']}")
    print(f"    - Match Time: {ep.start_time_sec:.1f}s -> {ep.end_time_sec:.1f}s")

    # In Goal 2, Home is Attacking (scoring) and Away is Defending
    att_coords = ep.home_coords
    att_vels = ep.home_vels
    def_coords = ep.away_coords
    def_vels = ep.away_vels
    ball_coords = ep.ball_coords
    times = np.linspace(ep.start_time_sec, ep.end_time_sec, len(att_coords))

    # Threat event (shot) is located near the end of the window (pre_event_seconds * 25)
    threat_idx = int(10.0 * ep.fps)
    if threat_idx >= len(att_coords):
        threat_idx = len(att_coords) - 1

    print("\n[*] Initializing Spearman Physics-Based Pitch Control Engine...")
    pc_engine = PitchControlEngine(grid_nx=50, grid_ny=32, reaction_time=0.7, max_speed=5.5)

    print("[*] Running Structural Causal Model (SCM) Domino Detection...")
    detector = SCMDominoDetector(fps=ep.fps, pitch_control_engine=pc_engine)
    res = detector.analyze_episode(
        att_coords=att_coords,
        att_vels=att_vels,
        def_coords=def_coords,
        def_vels=def_vels,
        ball_coords=ball_coords,
        times_sec=times,
        def_jerseys=ep.away_jerseys,
        threat_frame_idx=threat_idx
    )

    print("\n" + "=" * 78)
    print("  ANALYTICAL BREAKDOWN & CAUSAL ROOT RESULTS:")
    print("=" * 78)
    print(f"  • Terminal Threat (Shot Taken):     Frame {ep.start_frame + res.threat_frame} (t = {res.threat_time_sec:.2f}s)")
    print(f"  • Causal Domino Moment (tau_domino): Frame {ep.start_frame + res.domino_frame} (t = {res.domino_time_sec:.2f}s)")
    print(f"  • EARLY WARNING LEAD TIME:          tau_lead = {res.lead_time_sec:.2f} SECONDS")
    print(f"  • Primary Causal Root Defender:     Jersey #{res.causal_root_jersey} (Away Defense)")
    print(f"  • Tactical Diagnostic:              {res.causal_root_error_desc}")
    print(f"  • Actual Shot Zone Control (PPCF):  {res.shot_zone_ppcf_actual:.2f} (Attackers Dominant)")
    print(f"  • Counterfactual Shot Zone (PPCF):  {res.shot_zone_ppcf_cf:.2f} (Defenders Recover Space)")
    print(f"  • CONCEDED THREAT MITIGATION:       -{res.risk_reduction_pct:.1f}%")
    print("=" * 78)

    # Render Publication-Grade 3-Panel Figure
    print("\n[*] Rendering Multi-Panel Pitch Control & Causal Figure...")
    fig = plt.figure(figsize=(18, 12), facecolor="#0e1717")

    # Panel 1: Real Tactical Coordinates at tau_domino
    ax1 = fig.add_subplot(2, 2, 1)
    draw_pitch(ax1)
    dom_idx = res.domino_frame

    val_att = ~np.isnan(att_coords[dom_idx, :, 0])
    val_def = ~np.isnan(def_coords[dom_idx, :, 0])
    p_att = att_coords[dom_idx, val_att]
    p_def = def_coords[dom_idx, val_def]
    b_pos = ball_coords[dom_idx]

    if len(p_def) >= 3:
        hull = ConvexHull(p_def)
        hull_pts = p_def[hull.vertices]
        hull_pts = np.vstack([hull_pts, hull_pts[0]])
        ax1.plot(hull_pts[:, 0], hull_pts[:, 1], color="#ff4d4f", linestyle="--", lw=1.8, alpha=0.8, label="Defensive Block")
        ax1.fill(hull_pts[:, 0], hull_pts[:, 1], color="#ff4d4f", alpha=0.12)

    ax1.scatter(p_att[:, 0], p_att[:, 1], c="#00d2d3", edgecolors="#ffffff", s=180, zorder=5, label="Home (Attacking)")
    ax1.scatter(p_def[:, 0], p_def[:, 1], c="#ff6b6b", edgecolors="#ffffff", s=180, zorder=5, label="Away (Defending)")
    ax1.scatter([b_pos[0]], [b_pos[1]], c="#fffa65", edgecolors="#000000", s=140, zorder=7, label="Ball")

    root_pos = def_coords[dom_idx, res.causal_root_idx]
    if not np.isnan(root_pos[0]):
        ax1.scatter([root_pos[0]], [root_pos[1]], c="#feca57", edgecolors="#ffffff", s=360, zorder=8, label=f"Causal Root (#{res.causal_root_jersey})")
        ax1.scatter([root_pos[0]], [root_pos[1]], c="none", edgecolors="#feca57", s=700, lw=2.5, linestyle=":", zorder=8)

    ax1.set_title(f"(A) Tactical Tracking at Domino Moment (t = {res.domino_time_sec:.1f}s | tau_lead = {res.lead_time_sec:.1f}s)", color="#ffffff", fontsize=11, fontweight="bold", pad=8)
    ax1.legend(loc="lower left", facecolor="#222f3e", edgecolor="#576574", labelcolor="#c8d6e5", fontsize=8.5)

    # Panel 2: Spearman Pitch Control Heatmap at tau_domino
    ax2 = fig.add_subplot(2, 2, 2)
    draw_pitch(ax2)
    im = ax2.imshow(
        res.domino_ppcf_grid,
        extent=[0, PITCH_LENGTH, 0, PITCH_WIDTH],
        origin="lower",
        cmap="coolwarm",
        alpha=0.65,
        vmin=0.0,
        vmax=1.0,
        zorder=2
    )
    ax2.scatter(p_att[:, 0], p_att[:, 1], c="#ffffff", edgecolors="#00d2d3", s=110, zorder=5)
    ax2.scatter(p_def[:, 0], p_def[:, 1], c="#ffffff", edgecolors="#ff6b6b", s=110, zorder=5)
    cbar = plt.colorbar(im, ax=ax2, fraction=0.035, pad=0.02)
    cbar.set_label("Pitch Control Prob (PPCF)", color="#ffffff", fontsize=9)
    cbar.ax.tick_params(colors="#c8d6e5")
    ax2.set_title("(B) Spearman Physics-Based Pitch Control Field (PPCF)", color="#ffffff", fontsize=11, fontweight="bold", pad=8)

    # Panel 3: Time Series of Structural Risk & Counterfactual Mitigation
    ax3 = fig.add_subplot(2, 1, 2)
    ax3.set_facecolor("#1a2421")
    t_axis = res.time_series_sec - res.time_series_sec[0]

    ax3.plot(t_axis, res.actual_threat_scores, color="#ff4d4f", lw=2.6, label="Observed Match Dangerous Space Control (m^2)")
    ax3.plot(t_axis, res.cf_threat_scores, color="#1dd1a1", lw=2.6, linestyle="--", label="Counterfactual Trajectory (Defender Anchored)")

    dom_rel_t = res.domino_time_sec - res.time_series_sec[0]
    threat_rel_t = res.threat_time_sec - res.time_series_sec[0]

    ax3.axvline(dom_rel_t, color="#feca57", linestyle=":", lw=2.2, label=f"tau_domino ({dom_rel_t:.1f}s)")
    ax3.axvline(threat_rel_t, color="#ff3838", linestyle="-.", lw=2.2, label=f"Shot / Goal Event ({threat_rel_t:.1f}s)")
    ax3.axvspan(dom_rel_t, threat_rel_t, color="#feca57", alpha=0.12, label=f"Early Lead Window (Delta t = {res.lead_time_sec:.1f}s)")

    ax3.set_xlim(0, max(t_axis))
    ax3.set_xlabel("Episode Time Elapsed (seconds)", color="#ffffff", fontsize=10, fontweight="bold")
    ax3.set_ylabel("Controlled Dangerous Space (m^2)", color="#ffffff", fontsize=10, fontweight="bold")
    ax3.set_title("(C) Temporal Collapse Profile: Empirical Domino Lead Time and Counterfactual Divergence", color="#ffffff", fontsize=11, fontweight="bold", pad=8)
    ax3.tick_params(colors="#c8d6e5")
    for spine in ax3.spines.values():
        spine.set_color("#576574")
    ax3.grid(True, linestyle="--", alpha=0.25, color="#ffffff")
    ax3.legend(loc="upper left", facecolor="#222f3e", edgecolor="#576574", labelcolor="#c8d6e5", fontsize=9)

    plt.tight_layout()
    output_path = Path("outputs") / "real_match_goal2_domino_analysis.png"
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    print(f"\n[SUCCESS] Enterprise Analysis Complete!")
    print(f"[SUCCESS] Multi-Panel Figure Generated: {output_path}")
    print("=" * 78)


if __name__ == "__main__":
    run_real_goal_analysis()
