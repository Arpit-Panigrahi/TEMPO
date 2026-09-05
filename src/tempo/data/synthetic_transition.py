"""
High-fidelity tactical trajectory generator for reproducible benchmark testing.
Simulates a classic high-press bait & domino collapse scenario:
1. Attacking team plays out from the back (midfield build-up).
2. Attacking #9 executes an undercutting decoy run towards the halfway line.
3. Defending CB #4 overcommits, breaking the defensive line by 6.2 meters.
4. The domino effect cascades to LB #3 and CDM #6 who hesitate and get caught in two minds.
5. 4.2 seconds later (tau_threat), Attacker #10 slips a through-ball into the vacated channel.
"""

import numpy as np
from tempo.geometry.pitch import PITCH_LENGTH, PITCH_WIDTH


def generate_press_break_sequence(num_seconds: float = 15.0, fps: float = 10.0, seed: int = 42):
    np.random.seed(seed)
    num_frames = int(num_seconds * fps)
    threat_frame = int(12.0 * fps)  # The penetrating pass occurs at t = 12.0s
    domino_target_frame = int(7.8 * fps) # CB bites at t = 7.8s (lead time = 4.2s)
    
    # Base positions:
    # Defending team in a 4-4-2 mid-block defending right goal (x ~ 65m)
    # CB4 is index 2 in def_pos
    base_def = np.array([
        [78.0, 14.0],  # RB (0)
        [75.0, 26.0],  # RCB (1)
        [75.0, 42.0],  # LCB - CB4 (2) <- The Causal Root
        [78.0, 54.0],  # LB (3)
        [62.0, 18.0],  # RM (4)
        [60.0, 30.0],  # RCM (5)
        [60.0, 38.0],  # LCM (6) <- Cascade 1
        [62.0, 50.0],  # LM (7)
        [48.0, 28.0],  # RS (8)
        [48.0, 40.0],  # LS (9)
    ])
    N_def = len(base_def)

    # Attacking team in build-up attacking rightwards
    base_att = np.array([
        [32.0, 20.0],  # RCB (0)
        [30.0, 34.0],  # CCB (1)
        [32.0, 48.0],  # LCB (2)
        [42.0, 12.0],  # RWB (3)
        [45.0, 34.0],  # Regista / Ball carrier (4)
        [42.0, 56.0],  # LWB (5)
        [52.0, 25.0],  # R-Interior (6)
        [52.0, 43.0],  # L-Interior - Attacker #10 (7) <- Exploits channel
        [64.0, 16.0],  # RW (8)
        [66.0, 40.0],  # Striker - Attacker #9 (9) <- Decoy runner
        [64.0, 52.0],  # LW (10)
    ])
    N_att = len(base_att)

    def_trajectories = np.zeros((num_frames, N_def, 2))
    att_trajectories = np.zeros((num_frames, N_att, 2))
    ball_trajectory = np.zeros((num_frames, 2))

    for t in range(num_frames):
        alpha = t / num_frames
        noise_def = np.random.normal(0, 0.08, (N_def, 2))
        noise_att = np.random.normal(0, 0.08, (N_att, 2))
        
        # General lateral drift as ball moves
        drift_y = np.sin(t * 0.1) * 1.5
        
        curr_def = base_def.copy()
        curr_def[:, 1] += drift_y
        
        curr_att = base_att.copy()
        curr_att[:, 1] += drift_y
        
        # Scenario Dynamics starting near domino_target_frame:
        if t >= domino_target_frame - int(1.5 * fps):
            # Attacker #9 drops 8 meters into midfield (the bait)
            progress = min(1.0, (t - (domino_target_frame - int(1.5 * fps))) / (3.0 * fps))
            curr_att[9, 0] -= progress * 9.0  # Drops from x=66 to x=57
            curr_att[9, 1] -= progress * 3.0
            
            # Causal Root Defender (CB4, idx 2) takes the bait and steps 6.5m forward!
            cb_progress = min(1.0, max(0.0, (t - domino_target_frame) / (2.5 * fps)))
            curr_def[2, 0] -= cb_progress * 7.5  # Steps from x=75 to x=67.5 (leaving gaping hole behind)
            curr_def[2, 1] -= cb_progress * 2.5
            
            # Cascade: LCM (idx 6) hesitates, trying to cover CB4's vacancy
            lcm_progress = min(1.0, max(0.0, (t - domino_target_frame - 5) / (2.5 * fps)))
            curr_def[6, 1] += lcm_progress * 3.8
            
            # Attacker #10 surges into the vacated channel
            if t >= domino_target_frame:
                run_progress = min(1.0, (t - domino_target_frame) / (num_frames - domino_target_frame))
                curr_att[7, 0] += run_progress * 16.0  # Pierces into penalty box edge
                curr_att[7, 1] -= run_progress * 1.5

        def_trajectories[t] = curr_def + noise_def
        att_trajectories[t] = curr_att + noise_att
        
        # Ball position
        if t < threat_frame - 15:
            # At feet of midfield playmaker
            ball_trajectory[t] = att_trajectories[t, 4] + np.array([0.5, 0.2])
        elif t < threat_frame:
            # Through ball travel to Attacker #10
            ratio = (t - (threat_frame - 15)) / 15.0
            ball_trajectory[t] = (1.0 - ratio) * att_trajectories[t, 4] + ratio * att_trajectories[t, 7]
        else:
            ball_trajectory[t] = att_trajectories[t, 7] + np.array([0.4, 0.0])

    return {
        "def_trajectories": def_trajectories,
        "att_trajectories": att_trajectories,
        "ball_trajectory": ball_trajectory,
        "threat_frame": threat_frame,
        "fps": fps
    }
