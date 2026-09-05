"""
Physics-based Pitch Control Engine (William Spearman 2018 Model).
Computes continuous spatial dominance, Time-To-Intercept (TTI),
and dangerous pitch control fields in real-time.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from tempo.geometry.pitch import PITCH_LENGTH, PITCH_WIDTH


class PitchControlEngine:
    def __init__(
        self,
        grid_nx: int = 50,
        grid_ny: int = 32,
        reaction_time: float = 0.7,
        max_speed: float = 5.5,
        time_variance: float = 0.45
    ):
        self.grid_nx = grid_nx
        self.grid_ny = grid_ny
        self.reaction_time = reaction_time
        self.max_speed = max_speed
        self.time_variance = time_variance

        # Construct spatial evaluation grid (centroids of pitch cells)
        x_edges = np.linspace(0, PITCH_LENGTH, grid_nx + 1)
        y_edges = np.linspace(0, PITCH_WIDTH, grid_ny + 1)
        self.cell_area = (PITCH_LENGTH / grid_nx) * (PITCH_WIDTH / grid_ny)

        x_coords = (x_edges[:-1] + x_edges[1:]) / 2.0
        y_coords = (y_edges[:-1] + y_edges[1:]) / 2.0
        self.grid_X, self.grid_Y = np.meshgrid(x_coords, y_coords)  # Shape: (grid_ny, grid_nx)
        self.grid_points = np.stack([self.grid_X, self.grid_Y], axis=-1) # Shape: (grid_ny, grid_nx, 2)

        # Precompute Goal Proximity Weighting (Target Goal at x=105, y=34)
        goal_pos = np.array([PITCH_LENGTH, PITCH_WIDTH / 2.0])
        dist_to_goal = np.linalg.norm(self.grid_points - goal_pos, axis=-1)
        # Danger weighting: highest inside the penalty box / central final third
        self.danger_weights = np.exp(-dist_to_goal / 28.0) * np.clip(self.grid_points[..., 0] / PITCH_LENGTH, 0.0, 1.0) ** 1.5

    def compute_frame_pitch_control(
        self,
        att_positions: np.ndarray,  # Shape: (N_att, 2)
        att_velocities: np.ndarray, # Shape: (N_att, 2)
        def_positions: np.ndarray,  # Shape: (N_def, 2)
        def_velocities: np.ndarray, # Shape: (N_def, 2)
    ) -> Dict:
        """
        Computes the 2D Pitch Control Field PPCF(x, y) for a single frame.
        Handles NaNs (players on bench / off pitch).
        """
        # Filter valid players on pitch
        valid_att = ~np.isnan(att_positions[:, 0])
        valid_def = ~np.isnan(def_positions[:, 0])

        att_p = att_positions[valid_att]
        att_v = att_velocities[valid_att]
        def_p = def_positions[valid_def]
        def_v = def_velocities[valid_def]

        if len(att_p) == 0 or len(def_p) == 0:
            ppcf = np.full((self.grid_ny, self.grid_nx), 0.5)
            return {"ppcf": ppcf, "att_controlled_area": 0.0, "def_controlled_area": 0.0, "dangerous_space_control": 0.0}

        # Vectorized Time-to-Intercept (TTI) for Attackers:
        # grid_points: (Ny, Nx, 2) -> (Ny, Nx, 1, 2)
        # att_p: (N_att, 2) -> (1, 1, N_att, 2)
        pts = self.grid_points[:, :, np.newaxis, :]
        att_react = (att_p + att_v * self.reaction_time)[np.newaxis, np.newaxis, :, :]
        def_react = (def_p + def_v * self.reaction_time)[np.newaxis, np.newaxis, :, :]

        # Distance from reaction position to grid points
        dist_att = np.linalg.norm(pts - att_react, axis=-1) # (Ny, Nx, N_att)
        dist_def = np.linalg.norm(pts - def_react, axis=-1) # (Ny, Nx, N_def)

        tti_att = self.reaction_time + dist_att / self.max_speed
        tti_def = self.reaction_time + dist_def / self.max_speed

        min_tti_att = np.min(tti_att, axis=-1) # (Ny, Nx)
        min_tti_def = np.min(tti_def, axis=-1) # (Ny, Nx)

        # Logistic probability of control
        time_diff = min_tti_def - min_tti_att
        ppcf = 1.0 / (1.0 + np.exp(-time_diff / self.time_variance))

        # Metrics
        att_area = float(np.sum(ppcf) * self.cell_area)
        def_area = float(np.sum(1.0 - ppcf) * self.cell_area)
        danger_control = float(np.sum(ppcf * self.danger_weights) * self.cell_area)

        return {
            "ppcf": ppcf,
            "att_controlled_area": att_area,
            "def_controlled_area": def_area,
            "dangerous_space_control": danger_control,
            "grid_X": self.grid_X,
            "grid_Y": self.grid_Y,
        }
