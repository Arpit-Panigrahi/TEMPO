"""
Unit tests for TEMPO Domino Moment detection and geometric metrics.
Uses standard Python assertions for zero-dependency execution.
"""

import numpy as np
from tempo.geometry.pitch import compute_team_centroid, compute_defensive_hull_metrics, compute_spatial_entropy
from tempo.causal.domino import DominoDetector
from tempo.data.synthetic_transition import generate_press_break_sequence


def test_centroid():
    pts = np.array([[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]])
    centroid = compute_team_centroid(pts)
    assert np.isclose(centroid[0], 5.0), f"Expected 5.0, got {centroid[0]}"
    assert np.isclose(centroid[1], 10.0 / 3.0), f"Expected 3.333, got {centroid[1]}"
    print("  [✓] test_centroid passed")


def test_hull_metrics():
    pts = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])
    metrics = compute_defensive_hull_metrics(pts)
    assert np.isclose(metrics["area"], 100.0, atol=1.0), f"Expected area 100.0, got {metrics['area']}"
    assert np.isclose(metrics["perimeter"], 40.0, atol=1.0), f"Expected perimeter 40.0, got {metrics['perimeter']}"
    assert metrics["compactness"] > 0.0
    print("  [✓] test_hull_metrics passed")


def test_domino_detector_end_to_end():
    data = generate_press_break_sequence(num_seconds=15.0, fps=10.0, seed=42)
    detector = DominoDetector(fps=10.0, baseline_area=620.0)
    res = detector.detect_domino_moment(
        data["def_trajectories"],
        data["ball_trajectory"],
        data["att_trajectories"],
        data["threat_frame"]
    )
    assert res["domino_frame"] < data["threat_frame"], "Domino frame must precede threat frame"
    assert res["lead_time_sec"] >= 2.0, f"Expected lead time >= 2.0s, got {res['lead_time_sec']}"
    assert res["causal_root_idx"] == 2, f"Expected LCB (idx 2) as causal root, got {res['causal_root_idx']}"
    
    cf_scores, cf_def = detector.simulate_counterfactual(
        data["def_trajectories"],
        data["ball_trajectory"],
        data["att_trajectories"],
        res["domino_frame"],
        res["causal_root_idx"]
    )
    threat_idx = data["threat_frame"]
    assert cf_scores[threat_idx] < res["structural_scores"][threat_idx], "Counterfactual risk must be lower"
    print("  [✓] test_domino_detector_end_to_end passed")


if __name__ == "__main__":
    print("[*] Running TEMPO test suite...")
    test_centroid()
    test_hull_metrics()
    test_domino_detector_end_to_end()
    print("[PASS] All TEMPO unit tests passed successfully!")
