"""
Matplotlib-based football pitch visualizer.
No external visualization dependencies required (100% standard matplotlib).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc
from scipy.spatial import ConvexHull
from tempo.geometry.pitch import PITCH_LENGTH, PITCH_WIDTH


def draw_pitch(ax=None, pitch_color="#1a2421", line_color="#ffffff", line_alpha=0.6):
    """Draw a clean standard football pitch."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))
    else:
        fig = ax.figure

    ax.set_facecolor(pitch_color)
    fig.patch.set_facecolor(pitch_color)

    # Pitch boundary
    ax.plot([0, 0, PITCH_LENGTH, PITCH_LENGTH, 0], [0, PITCH_WIDTH, PITCH_WIDTH, 0, 0], color=line_color, alpha=line_alpha, lw=1.8)
    
    # Halfway line
    ax.plot([PITCH_LENGTH / 2, PITCH_LENGTH / 2], [0, PITCH_WIDTH], color=line_color, alpha=line_alpha, lw=1.8)
    
    # Center circle & spot
    center_circle = plt.Circle((PITCH_LENGTH / 2, PITCH_WIDTH / 2), 9.15, color=line_color, fill=False, alpha=line_alpha, lw=1.8)
    ax.add_patch(center_circle)
    ax.scatter([PITCH_LENGTH / 2], [PITCH_WIDTH / 2], color=line_color, s=20, alpha=line_alpha)

    # Penalty areas (16.5m depth, 40.32m width)
    pen_box_y = (PITCH_WIDTH - 40.32) / 2
    ax.add_patch(Rectangle((0, pen_box_y), 16.5, 40.32, fill=False, edgecolor=line_color, alpha=line_alpha, lw=1.5))
    ax.add_patch(Rectangle((PITCH_LENGTH - 16.5, pen_box_y), 16.5, 40.32, fill=False, edgecolor=line_color, alpha=line_alpha, lw=1.5))

    # 6-yard boxes (5.5m depth, 18.32m width)
    six_box_y = (PITCH_WIDTH - 18.32) / 2
    ax.add_patch(Rectangle((0, six_box_y), 5.5, 18.32, fill=False, edgecolor=line_color, alpha=line_alpha, lw=1.2))
    ax.add_patch(Rectangle((PITCH_LENGTH - 5.5, six_box_y), 5.5, 18.32, fill=False, edgecolor=line_color, alpha=line_alpha, lw=1.2))

    # Penalty spots (11m)
    ax.scatter([11.0, PITCH_LENGTH - 11.0], [PITCH_WIDTH / 2, PITCH_WIDTH / 2], color=line_color, s=18, alpha=line_alpha)

    # Goal frames
    ax.plot([0, -2], [PITCH_WIDTH / 2 - 3.66, PITCH_WIDTH / 2 - 3.66], color=line_color, lw=2, alpha=line_alpha)
    ax.plot([0, -2], [PITCH_WIDTH / 2 + 3.66, PITCH_WIDTH / 2 + 3.66], color=line_color, lw=2, alpha=line_alpha)
    ax.plot([-2, -2], [PITCH_WIDTH / 2 - 3.66, PITCH_WIDTH / 2 + 3.66], color=line_color, lw=2, alpha=line_alpha)
    
    ax.plot([PITCH_LENGTH, PITCH_LENGTH + 2], [PITCH_WIDTH / 2 - 3.66, PITCH_WIDTH / 2 - 3.66], color=line_color, lw=2, alpha=line_alpha)
    ax.plot([PITCH_LENGTH, PITCH_LENGTH + 2], [PITCH_WIDTH / 2 + 3.66, PITCH_WIDTH / 2 + 3.66], color=line_color, lw=2, alpha=line_alpha)
    ax.plot([PITCH_LENGTH + 2, PITCH_LENGTH + 2], [PITCH_WIDTH / 2 - 3.66, PITCH_WIDTH / 2 + 3.66], color=line_color, lw=2, alpha=line_alpha)

    ax.set_xlim(-5, PITCH_LENGTH + 5)
    ax.set_ylim(-5, PITCH_WIDTH + 5)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def plot_domino_frame(
    ax,
    att_pos: np.ndarray,
    def_pos: np.ndarray,
    ball_pos: np.ndarray,
    causal_root_idx: int,
    cascade_indices: list = None,
    cf_root_pos: np.ndarray = None,
    title: str = "TEMPO Domino Moment Detection"
):
    """Plot tactical frame with defensive hull and causal breakdown highlights."""
    draw_pitch(ax)

    # Draw defensive convex hull
    if len(def_pos) >= 3:
        hull = ConvexHull(def_pos)
        hull_pts = def_pos[hull.vertices]
        hull_pts = np.vstack([hull_pts, hull_pts[0]])
        ax.plot(hull_pts[:, 0], hull_pts[:, 1], color="#ff4d4f", linestyle="--", lw=1.5, alpha=0.7, label="Defensive Block Hull")
        ax.fill(hull_pts[:, 0], hull_pts[:, 1], color="#ff4d4f", alpha=0.12)

    # Attackers (Cyan)
    ax.scatter(att_pos[:, 0], att_pos[:, 1], c="#00d2d3", edgecolors="#ffffff", s=180, zorder=5, label="Attacking Team")
    
    # Defenders (Red/Coral)
    ax.scatter(def_pos[:, 0], def_pos[:, 1], c="#ff6b6b", edgecolors="#ffffff", s=180, zorder=5, label="Defending Team")
    
    # Highlight Causal Root Player (Gold pulsing ring)
    root = def_pos[causal_root_idx]
    ax.scatter([root[0]], [root[1]], c="#feca57", edgecolors="#ffffff", s=340, zorder=6, label="Causal Root (Overcommitted)")
    ax.scatter([root[0]], [root[1]], c="none", edgecolors="#feca57", s=650, lw=2.5, linestyle=":", zorder=6)

    # Highlight Counterfactual Position if provided
    if cf_root_pos is not None:
        ax.scatter([cf_root_pos[0]], [cf_root_pos[1]], c="#1dd1a1", edgecolors="#ffffff", s=280, marker="X", zorder=7, label="Counterfactual Zonal Anchor")
        ax.annotate(
            "", xy=(cf_root_pos[0], cf_root_pos[1]), xytext=(root[0], root[1]),
            arrowprops=dict(arrowstyle="->", color="#1dd1a1", lw=2.2, linestyle="--")
        )

    # Draw Cascade lines to adjacent affected defenders
    if cascade_indices:
        for casc_idx in cascade_indices:
            tgt = def_pos[casc_idx]
            ax.annotate(
                "", xy=(tgt[0], tgt[1]), xytext=(root[0], root[1]),
                arrowprops=dict(arrowstyle="->", color="#ff9f43", lw=1.8, linestyle=":")
            )

    # Ball (Bright Yellow)
    ax.scatter([ball_pos[0]], [ball_pos[1]], c="#fffa65", edgecolors="#000000", s=140, marker="o", zorder=8, label="Ball")

    ax.set_title(title, color="#ffffff", fontsize=13, fontweight="bold", pad=12)
    legend = ax.legend(loc="lower right", facecolor="#222f3e", edgecolor="#576574", labelcolor="#c8d6e5", fontsize=9)
