"""
Production-grade Metrica Sports optical tracking and event data ingestion engine.
Standardized to FIFA pitch specifications (105m x 68m).
Supports automatic direction-of-play normalization (Attacking Left -> Right).
"""

import os
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.signal import savgol_filter


PITCH_LENGTH = 105.0
PITCH_WIDTH = 68.0


@dataclass
class TacticalEpisode:
    """Represents an extracted, normalized match sequence."""
    game_id: str
    period: int
    start_frame: int
    end_frame: int
    start_time_sec: float
    end_time_sec: float
    fps: float
    # Arrays of shape (T, N_players, 2) in meters (attacking team attacks towards x=105)
    home_coords: np.ndarray
    home_vels: np.ndarray
    away_coords: np.ndarray
    away_vels: np.ndarray
    # Array of shape (T, 2) in meters
    ball_coords: np.ndarray
    ball_vels: np.ndarray
    home_jerseys: List[str]
    away_jerseys: List[str]
    event_meta: Dict
    attacking_team: str  # "Home" or "Away"


class MetricaLoader:
    """High-performance parser and kinematic filter for Metrica tracking data."""

    def __init__(self, data_dir: str = "data/metrica"):
        self.data_dir = Path(data_dir)

    def load_events(self, filename: str = "Sample_Game_1_RawEventsData.csv") -> List[Dict]:
        """Loads and parses Metrica synchronized match events."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Events file not found at {filepath}")

        events = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append({
                    "team": row["Team"],
                    "type": row["Type"],
                    "subtype": row["Subtype"],
                    "period": int(row["Period"]) if row["Period"] else 1,
                    "start_frame": int(row["Start Frame"]) if row["Start Frame"] else 0,
                    "start_time": float(row["Start Time [s]"]) if row["Start Time [s]"] else 0.0,
                    "end_frame": int(row["End Frame"]) if row["End Frame"] else 0,
                    "end_time": float(row["End Time [s]"]) if row["End Time [s]"] else 0.0,
                    "from_player": row["From"],
                    "to_player": row["To"],
                    "start_x": float(row["Start X"]) if row["Start X"] and row["Start X"] != "NaN" else None,
                    "start_y": float(row["Start Y"]) if row["Start Y"] and row["Start Y"] != "NaN" else None,
                    "end_x": float(row["End X"]) if row["End X"] and row["End X"] != "NaN" else None,
                    "end_y": float(row["End Y"]) if row["End Y"] and row["End Y"] != "NaN" else None,
                })
        return events

    def load_tracking(
        self,
        home_file: str = "Sample_Game_1_RawTrackingData_Home_Team.csv",
        away_file: str = "Sample_Game_1_RawTrackingData_Away_Team.csv",
        frame_start: Optional[int] = None,
        frame_end: Optional[int] = None
    ) -> Dict:
        """
        Parses Metrica Home and Away tracking CSVs for a specific frame window.
        Coordinates are in FIFA meters: [0, 105] x [0, 68].
        """
        home_path = self.data_dir / home_file
        away_path = self.data_dir / away_file

        if not home_path.exists() or not away_path.exists():
            raise FileNotFoundError(f"Tracking files not found in {self.data_dir}")

        home_data = self._parse_single_team(home_path, frame_start, frame_end)
        away_data = self._parse_single_team(away_path, frame_start, frame_end)

        return {
            "frames": home_data["frames"],
            "times": home_data["times"],
            "periods": home_data["periods"],
            "home_coords": home_data["coords"],
            "home_jerseys": home_data["jerseys"],
            "away_coords": away_data["coords"],
            "away_jerseys": away_data["jerseys"],
            "ball_coords": home_data["ball_coords"],
        }

    def _parse_single_team(
        self,
        filepath: Path,
        frame_start: Optional[int],
        frame_end: Optional[int]
    ) -> Dict:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            team_header = next(reader)
            jersey_header = next(reader)
            col_header = next(reader)

            players = []
            for col_idx in range(3, len(jersey_header) - 2, 2):
                jersey = jersey_header[col_idx].strip()
                if jersey:
                    players.append((jersey, col_idx, col_idx + 1))

            ball_x_col = len(col_header) - 2
            ball_y_col = len(col_header) - 1

            frames = []
            times = []
            periods = []
            coords_list = []
            ball_coords_list = []

            for row in reader:
                if not row or len(row) < 3:
                    continue
                try:
                    f_id = int(row[1])
                except (ValueError, IndexError):
                    continue

                if frame_start is not None and f_id < frame_start:
                    continue
                if frame_end is not None and f_id > frame_end:
                    break

                frames.append(f_id)
                periods.append(int(row[0]))
                times.append(float(row[2]))

                p_coords = []
                for _, x_c, y_c in players:
                    try:
                        x_val = float(row[x_c]) if row[x_c] and row[x_c] != "NaN" else np.nan
                        y_val = float(row[y_c]) if row[y_c] and row[y_c] != "NaN" else np.nan
                    except (ValueError, IndexError):
                        x_val, y_val = np.nan, np.nan

                    if not np.isnan(x_val):
                        x_m = x_val * PITCH_LENGTH
                        y_m = (1.0 - y_val) * PITCH_WIDTH
                    else:
                        x_m, y_m = np.nan, np.nan
                    p_coords.append([x_m, y_m])

                coords_list.append(p_coords)

                try:
                    bx = float(row[ball_x_col]) if row[ball_x_col] and row[ball_x_col] != "NaN" else np.nan
                    by = float(row[ball_y_col]) if row[ball_y_col] and row[ball_y_col] != "NaN" else np.nan
                except (ValueError, IndexError):
                    bx, by = np.nan, np.nan

                if not np.isnan(bx):
                    ball_coords_list.append([bx * PITCH_LENGTH, (1.0 - by) * PITCH_WIDTH])
                else:
                    ball_coords_list.append([np.nan, np.nan])

        return {
            "frames": np.array(frames),
            "times": np.array(times),
            "periods": np.array(periods),
            "coords": np.array(coords_list),
            "jerseys": [p[0] for p in players],
            "ball_coords": np.array(ball_coords_list)
        }

    @staticmethod
    def compute_velocities(
        coords: np.ndarray,
        fps: float = 25.0,
        max_speed: float = 11.5
    ) -> np.ndarray:
        T = coords.shape[0]
        vels = np.zeros_like(coords)
        if T < 7:
            dt = 1.0 / fps
            diffs = np.gradient(coords, axis=0) / dt
            speed = np.linalg.norm(diffs, axis=-1, keepdims=True)
            scale = np.where(speed > max_speed, max_speed / (speed + 1e-6), 1.0)
            return diffs * scale

        for i in range(coords.shape[1] if coords.ndim == 3 else 1):
            target = coords[:, i] if coords.ndim == 3 else coords
            valid = ~np.isnan(target[:, 0])
            if np.sum(valid) < 7:
                continue

            indices = np.arange(T)
            clean_x = np.interp(indices, indices[valid], target[valid, 0])
            clean_y = np.interp(indices, indices[valid], target[valid, 1])

            vx = savgol_filter(clean_x, window_length=7, polyorder=2, deriv=1, delta=1.0 / fps)
            vy = savgol_filter(clean_y, window_length=7, polyorder=2, deriv=1, delta=1.0 / fps)

            speed = np.sqrt(vx ** 2 + vy ** 2)
            mask = speed > max_speed
            vx[mask] = (vx[mask] / speed[mask]) * max_speed
            vy[mask] = (vy[mask] / speed[mask]) * max_speed

            if coords.ndim == 3:
                vels[:, i, 0] = vx
                vels[:, i, 1] = vy
            else:
                vels[:, 0] = vx
                vels[:, 1] = vy

        return vels

    def extract_goal_episode(
        self,
        event_index: int = 1,
        pre_event_seconds: float = 10.0,
        post_event_seconds: float = 1.0,
        fps: float = 25.0,
        normalize_attack_direction: bool = True
    ) -> TacticalEpisode:
        """
        Extracts tactical episode and normalizes coordinates so attacking team attacks left-to-right (x -> 105).
        """
        events = self.load_events()
        goal_events = [e for e in events if "GOAL" in (e.get("subtype") or "") and e.get("type") == "SHOT"]
        if not goal_events:
            raise ValueError("No goal events found in events dataset.")

        selected_event = goal_events[min(event_index, len(goal_events) - 1)]
        target_frame = selected_event["start_frame"]
        period = selected_event["period"]
        attacking_team = selected_event["team"]

        frame_start = max(1, target_frame - int(pre_event_seconds * fps))
        frame_end = target_frame + int(post_event_seconds * fps)

        tracking = self.load_tracking(frame_start=frame_start, frame_end=frame_end)

        home_coords = tracking["home_coords"].copy()
        away_coords = tracking["away_coords"].copy()
        ball_coords = tracking["ball_coords"].copy()

        # Check if attacking direction needs 180 degree flip
        # In Period 1, Home attacks towards x=105, Away attacks towards x=0
        # In Period 2, Home attacks towards x=0, Away attacks towards x=105
        flip = False
        if normalize_attack_direction:
            if attacking_team == "Home" and period == 2:
                flip = True
            elif attacking_team == "Away" and period == 1:
                flip = True

        if flip:
            home_coords[:, :, 0] = PITCH_LENGTH - home_coords[:, :, 0]
            home_coords[:, :, 1] = PITCH_WIDTH - home_coords[:, :, 1]
            away_coords[:, :, 0] = PITCH_LENGTH - away_coords[:, :, 0]
            away_coords[:, :, 1] = PITCH_WIDTH - away_coords[:, :, 1]
            ball_coords[:, 0] = PITCH_LENGTH - ball_coords[:, 0]
            ball_coords[:, 1] = PITCH_WIDTH - ball_coords[:, 1]

        home_vels = self.compute_velocities(home_coords, fps=fps)
        away_vels = self.compute_velocities(away_coords, fps=fps)
        ball_vels = self.compute_velocities(ball_coords, fps=fps)

        return TacticalEpisode(
            game_id="Metrica_Game_1",
            period=period,
            start_frame=frame_start,
            end_frame=frame_end,
            start_time_sec=float(tracking["times"][0]),
            end_time_sec=float(tracking["times"][-1]),
            fps=fps,
            home_coords=home_coords,
            home_vels=home_vels,
            away_coords=away_coords,
            away_vels=away_vels,
            ball_coords=ball_coords,
            ball_vels=ball_vels,
            home_jerseys=tracking["home_jerseys"],
            away_jerseys=tracking["away_jerseys"],
            event_meta=selected_event,
            attacking_team=attacking_team
        )
