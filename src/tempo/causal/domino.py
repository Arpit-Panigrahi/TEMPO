"""
TEMPO Causal Engine:
Domino Moment Detection & Counterfactual Root-Cause Attribution.

Implements Paper #1 core methodology:
- Structural Breakdown Index S(t) combining Line Disruption, Channel Opening, and Spatial Entropy
- Domino Moment Identification tau_domino preceding critical penetration
- Agent-Level Causal Attribution identifying the structural rupture trigger
- Counterfactual Perturbation & Conceded Threat Mitigation
"""

import numpy as np
from typing import Dict, List, Tuple
from tempo.geometry.pitch import (
    compute_defensive_hull_metrics,
    compute_spatial_entropy,
    compute_team_centroid
)


class DominoDetector:
    def __init__(
        self,
        fps: float = 10.0,
        baseline_area: float = 620.0,
        lead_time_min_sec: float = 2.5,
        lead_time_max_sec: float = 6.0,
    ):
        self.fps = fps
        self.baseline_area = baseline_area
        self.lead_time_min_frames = int(lead_time_min_sec * fps)
        self.lead_time_max_frames = int(lead_time_max_sec * fps)

    def compute_frame_structural_breakdown(
        self,
        def_positions: np.ndarray,
        ball_pos: np.ndarray,
        att_positions: np.ndarray
    ) -> Dict[str, float]:
        """
        Computes composite structural breakdown index S(t).
        Defenders 0..3 represent the Back Four (RB, RCB, LCB, LB).
        """
        N_def = len(def_positions)
        backline = def_positions[:4]
        
        # 1. Backline Cohesion Breakdown: Variance in x-depth of the 4 defenders
        # A disciplined line has low variance (all step up together). A broken line has high variance.
        line_depth_std = float(np.std(backline[:, 0]))
        line_cohesion_score = line_depth_std / 2.5  # Normalized: >1.0 indicates broken offside/depth line
        
        # 2. Channel Aperture (Gap behind stepped-out defender)
        # Distance between RCB (idx 1) and LB (idx 3) vs LCB (idx 2) position
        rcb_pos = backline[1]
        lcb_pos = backline[2]
        lb_pos = backline[3]
        
        # If LCB steps forward (lower x), channel aperture behind him expands
        channel_gap = max(0.0, float(rcb_pos[0] - lcb_pos[0]))
        aperture_score = channel_gap / 4.0
        
        # 3. Defensive Block Convex Hull & Compactness
        hull_metrics = compute_defensive_hull_metrics(def_positions)
        area_expansion = max(0.0, (hull_metrics["area"] - self.baseline_area) / self.baseline_area)
        compactness_loss = max(0.0, 1.0 - hull_metrics["compactness"])
        
        # 4. Attacking Penetration Vulnerability: Are attackers in space behind stepped defender?
        # Number of attackers behind the deepest non-GK defender
        vulnerability = 0.0
        for att in att_positions:
            if att[0] > lcb_pos[0] and np.abs(att[1] - lcb_pos[1]) < 8.0:
                vulnerability += 0.25

        # Composite Structural Breakdown Score S(t)
        # Scaled smoothly in [0.0, 1.0+]
        s_score = (
            0.35 * line_cohesion_score +
            0.30 * aperture_score +
            0.20 * area_expansion +
            0.15 * vulnerability
        )
        
        return {
            "score": float(s_score),
            "line_depth_std": line_depth_std,
            "aperture_score": aperture_score,
            "area": hull_metrics["area"],
            "compactness": hull_metrics["compactness"],
            "vulnerability": vulnerability
        }

    def detect_domino_moment(
        self,
        def_trajectories: np.ndarray,  # (T, N_def, 2)
        ball_trajectories: np.ndarray, # (T, 2)
        att_trajectories: np.ndarray,  # (T, N_att, 2)
        threat_frame: int
    ) -> Dict:
        """
        Detects the Domino Moment timestamp tau_domino and identifies the causal root agent.
        """
        T = def_trajectories.shape[0]
        scores = []
        
        for t in range(T):
            res = self.compute_frame_structural_breakdown(
                def_trajectories[t], ball_trajectories[t], att_trajectories[t]
            )
            scores.append(res["score"])
            
        scores = np.array(scores)
        grad_s = np.gradient(scores)
        
        search_start = max(0, threat_frame - self.lead_time_max_frames)
        search_end = max(1, threat_frame - self.lead_time_min_frames)
        
        window_grad = grad_s[search_start:search_end]
        if len(window_grad) == 0:
            domino_idx = max(0, threat_frame - int(4.0 * self.fps))
        else:
            domino_idx = search_start + int(np.argmax(window_grad))
            
        lead_time_sec = (threat_frame - domino_idx) / self.fps
        
        # Causal Root Identification:
        # Measure which defender has the highest deviation from their initial line anchor
        # multiplied by forward velocity towards decoy runner
        anchor_positions = def_trajectories[0]
        def_at_domino = def_trajectories[domino_idx]
        
        if domino_idx > 0:
            vels = np.linalg.norm(def_trajectories[domino_idx] - def_trajectories[domino_idx - 1], axis=1) * self.fps
        else:
            vels = np.zeros(len(def_at_domino))
            
        # Displacement along x (breaking the offside / defensive depth plane)
        forward_displacements = np.maximum(0.0, anchor_positions[:, 0] - def_at_domino[:, 0])
        attribution_scores = forward_displacements * (vels + 0.3)
        
        causal_root_idx = int(np.argmax(attribution_scores))
        
        return {
            "threat_frame": threat_frame,
            "domino_frame": domino_idx,
            "lead_time_sec": lead_time_sec,
            "causal_root_idx": causal_root_idx,
            "structural_scores": scores,
            "gradient_scores": grad_s,
        }

    def simulate_counterfactual(
        self,
        def_trajectories: np.ndarray,
        ball_trajectories: np.ndarray,
        att_trajectories: np.ndarray,
        domino_frame: int,
        causal_root_idx: int,
        damping_factor: float = 0.85
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Counterfactual intervention: The identified causal defender maintains zonal discipline
        and anchors to the defensive backline rather than following the decoy runner.
        """
        T, N_def, _ = def_trajectories.shape
        cf_def = def_trajectories.copy()
        
        # Anchor position to the line formed by adjacent defenders (RCB idx 1 and LB idx 3)
        for t in range(domino_frame, T):
            partner_x = (cf_def[t, 1, 0] + cf_def[t, 3, 0]) / 2.0
            partner_y = 42.0  # Assigned LCB corridor
            
            # Counterfactual position blends back into the coherent line
            actual_pos = def_trajectories[t, causal_root_idx]
            ideal_pos = np.array([partner_x, partner_y])
            cf_def[t, causal_root_idx] = (1.0 - damping_factor) * actual_pos + damping_factor * ideal_pos

        cf_scores = []
        for t in range(T):
            res = self.compute_frame_structural_breakdown(
                cf_def[t], ball_trajectories[t], att_trajectories[t]
            )
            cf_scores.append(res["score"])
            
        return np.array(cf_scores), cf_def
