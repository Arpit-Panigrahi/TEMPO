"""
Matplotlib-based tactical pitch visualizer.
Pure matplotlib, zero external UI dependencies.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.spatial import ConvexHull
from tempo.geometry.pitch import PITCH_LENGTH, PITCH_WIDTH


def draw_pitch(ax=None, pitch_color="#1a2421", line_color="#ffffff", line_alpha=0.6):
    """Draw a standard FIFA football pitch (105m x 68m)."""
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


def plot_frame(
    ax,
    att_pos: np.ndarray,
    def_pos: np.ndarray,
    ball_pos: np.ndarray,
    title: str = "TEMPO Tactical State"
):
    """Plot basic frame with team positions, ball, and defensive hull."""
    draw_pitch(ax)

    if len(def_pos) >= 3:
        hull = ConvexHull(def_pos)
        hull_pts = def_pos[hull.vertices]
        hull_pts = np.vstack([hull_pts, hull_pts[0]])
        ax.plot(hull_pts[:, 0], hull_pts[:, 1], color="#ff4d4f", linestyle="--", lw=1.5, alpha=0.7, label="Defensive Block")
        ax.fill(hull_pts[:, 0], hull_pts[:, 1], color="#ff4d4f", alpha=0.12)

    ax.scatter(att_pos[:, 0], att_pos[:, 1], c="#00d2d3", edgecolors="#ffffff", s=160, zorder=5, label="Attacking")
    ax.scatter(def_pos[:, 0], def_pos[:, 1], c="#ff6b6b", edgecolors="#ffffff", s=160, zorder=5, label="Defending")
    ax.scatter([ball_pos[0]], [ball_pos[1]], c="#fffa65", edgecolors="#000000", s=130, marker="o", zorder=6, label="Ball")

    ax.set_title(title, color="#ffffff", fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="lower right", facecolor="#222f3e", edgecolor="#576574", labelcolor="#c8d6e5", fontsize=9)
