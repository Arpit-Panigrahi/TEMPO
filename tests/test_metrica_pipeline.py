"""
Comprehensive test suite for TEMPO Real-Data Ingestion,
Spearman Pitch Control Engine, and SCM Domino Detection.
Uses pure Python standard assertions (zero external test dependencies).
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from tempo.data.metrica_io import MetricaLoader, PITCH_LENGTH, PITCH_WIDTH
from tempo.analytics.pitch_control import PitchControlEngine
from tempo.causal.scm_domino import SCMDominoDetector


def test_metrica_ingestion():
    print("[*] Testing Metrica Data Ingestion & Normalization...")
    loader = MetricaLoader("data/metrica")
    events = loader.load_events()
    assert len(events) > 1000, f"Expected >1000 events, got {len(events)}"
    
    # Extract Goal 2 episode
    ep = loader.extract_goal_episode(event_index=1, pre_event_seconds=5.0, post_event_seconds=1.0)
    assert ep.period == 2, f"Expected Period 2, got {ep.period}"
    assert ep.home_coords.shape[0] > 100, "Expected >100 frames"
    assert ep.home_coords.shape[2] == 2, "Expected 2D coordinates"
    
    # Verify pitch boundaries in meters
    val_x = ep.home_coords[..., 0]
    val_y = ep.home_coords[..., 1]
    valid_mask = ~np.isnan(val_x)
    assert np.all(val_x[valid_mask] >= -5.0) and np.all(val_x[valid_mask] <= PITCH_LENGTH + 5.0)
    assert np.all(val_y[valid_mask] >= -5.0) and np.all(val_y[valid_mask] <= PITCH_WIDTH + 5.0)
    print("  [✓] Metrica Ingestion & FIFA Coordinates Verified.")


def test_pitch_control_engine():
    print("[*] Testing Spearman Physics-Based Pitch Control Engine...")
    pc_engine = PitchControlEngine(grid_nx=40, grid_ny=25)
    
    # Simple 2-player scenario
    att_pos = np.array([[50.0, 34.0]])
    att_vel = np.array([[2.0, 0.0]])
    def_pos = np.array([[70.0, 34.0]])
    def_vel = np.array([[-1.0, 0.0]])
    
    res = pc_engine.compute_frame_pitch_control(att_pos, att_vel, def_pos, def_vel)
    ppcf = res["ppcf"]
    assert ppcf.shape == (25, 40), f"Expected (25, 40), got {ppcf.shape}"
    assert np.all(ppcf >= 0.0) and np.all(ppcf <= 1.0), "PPCF must be in [0, 1]"
    assert res["att_controlled_area"] > 0.0
    assert res["def_controlled_area"] > 0.0
    print("  [✓] Spearman Pitch Control Mathematical Bounds Verified.")


def test_scm_domino_real_goal():
    print("[*] Testing SCM Domino Detector on Real Goal Sequence...")
    loader = MetricaLoader("data/metrica")
    ep = loader.extract_goal_episode(event_index=1, pre_event_seconds=8.0, post_event_seconds=1.0)
    
    pc_engine = PitchControlEngine(grid_nx=40, grid_ny=25)
    detector = SCMDominoDetector(fps=ep.fps, pitch_control_engine=pc_engine)
    
    threat_idx = int(8.0 * ep.fps)
    times = np.linspace(ep.start_time_sec, ep.end_time_sec, len(ep.home_coords))
    
    res = detector.analyze_episode(
        att_coords=ep.home_coords,
        att_vels=ep.home_vels,
        def_coords=ep.away_coords,
        def_vels=ep.away_vels,
        ball_coords=ep.ball_coords,
        times_sec=times,
        def_jerseys=ep.away_jerseys,
        threat_frame_idx=threat_idx
    )
    
    assert res.domino_frame < res.threat_frame, "Domino Moment must precede the threat shot"
    assert res.lead_time_sec >= 2.0, f"Expected lead time >= 2.0s, got {res.lead_time_sec:.2f}s"
    assert len(res.causal_root_jersey) > 0, "Causal root defender must be identified"
    print(f"  [✓] Real Goal Domino Moment Detected: lead time = {res.lead_time_sec:.2f}s, Causal Defender #{res.causal_root_jersey}")


if __name__ == "__main__":
    print("=" * 65)
    print("  RUNNING TEMPO PRODUCTION VALIDATION SUITE")
    print("=" * 65)
    test_metrica_ingestion()
    test_pitch_control_engine()
    test_scm_domino_real_goal()
    print("=" * 65)
    print("  ALL PRODUCTION TESTS PASSED SUCCESSFULLY (100% GREEN)")
    print("=" * 65)
