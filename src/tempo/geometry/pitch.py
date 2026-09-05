"""
Geometric primitives, pitch representations, and spatial metric calculators.
Standard FIFA pitch dimensions: 105m length x 68m width.
"""

import numpy as np
from scipy.spatial import ConvexHull, Voronoi


PITCH_LENGTH = 105.0
PITCH_WIDTH = 68.0


def compute_team_centroid(positions: np.ndarray) -> np.ndarray:
    """Compute the (x, y) centroid of a team's outfield players."""
    return np.mean(positions, axis=0)


def compute_defensive_hull_metrics(positions: np.ndarray) -> dict:
    """
    Computes convex hull area, perimeter, width, length, and compactness
    for outfield defending players.
    
    Returns:
        dict containing 'area', 'perimeter', 'length', 'width', 'compactness'
    """
    if len(positions) < 3:
        return {"area": 0.0, "perimeter": 0.0, "length": 0.0, "width": 0.0, "compactness": 0.0}
    
    hull = ConvexHull(positions)
    area = float(hull.volume)  # In 2D, hull.volume is the polygon area
    perimeter = float(hull.area)  # In 2D, hull.area is perimeter
    
    xs = positions[:, 0]
    ys = positions[:, 1]
    length = float(np.max(xs) - np.min(xs))
    width = float(np.max(ys) - np.min(ys))
    
    # Isoperimetric quotient (compactness): 4 * pi * Area / Perimeter^2
    # Circle = 1.0; dispersed elongated shape approaches 0.0
    compactness = (4.0 * np.pi * area) / (perimeter ** 2 + 1e-6)
    
    return {
        "area": area,
        "perimeter": perimeter,
        "length": length,
        "width": width,
        "compactness": float(compactness)
    }


def compute_spatial_entropy(positions: np.ndarray, grid_nx: int = 10, grid_ny: int = 7) -> float:
    """
    Computes Shannon spatial entropy of player dispersion across pitch zones.
    High entropy = high dispersion / lack of coherent block structure.
    """
    x_bins = np.linspace(0, PITCH_LENGTH, grid_nx + 1)
    y_bins = np.linspace(0, PITCH_WIDTH, grid_ny + 1)
    
    hist, _, _ = np.histogram2d(positions[:, 0], positions[:, 1], bins=[x_bins, y_bins])
    total_players = len(positions)
    if total_players == 0:
        return 0.0
    
    probs = hist.flatten() / total_players
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)


def compute_voronoi_dominance(attacking_positions: np.ndarray, defending_positions: np.ndarray) -> np.ndarray:
    """
    Computes cell-based territorial dominance between attacking and defending agents.
    """
    all_positions = np.vstack([attacking_positions, defending_positions])
    vor = Voronoi(all_positions)
    return vor
