# 🏆 FCIE Tier-1 Club Enterprise Architecture & Technical Specification
## Engineering Blueprint for Deployments with Elite European Clubs (Arsenal, Bayern Munich, Manchester City)

---

## 1. Executive Context & The Enterprise Value Gap

To sell FCIE to elite Champions League and Premier League organizations, the platform must bridge the gap between academic causal AI and the daily operational reality of football clubs. 

Elite clubs do not replace their workflows for new software; software must integrate seamlessly into their **existing video analysis stack (Hudl Sportscode)**, provide **dead-ball specialism (set-piece coaching)**, incorporate **physical fatigue telemetry (Catapult/STATSports)**, and guarantee **100% sovereign air-gapped data security**.

This document defines the technical architecture, data schemas, mathematical formulations, and interface specifications for the **Seven Enterprise Extension Modules (Modules ㉑–㉗)**.

```
                                  ENTERPRISE EXTENSION SUBSYSTEMS
                                  
   ┌───────────────────────────────────┐       ┌───────────────────────────────────┐
   │ Module ㉑: Set-Piece Causal Engine │       │ Module ㉒: Telemetry & GPS Fusion  │
   │ (Dead-Ball, Aerodynamics, Screens)│       │ (Catapult/STATSports Fatigue Math)│
   └─────────────────┬─────────────────┘       └─────────────────┬─────────────────┘
                     │                                           │
   ┌─────────────────▼─────────────────┐       ┌─────────────────▼─────────────────┐
   │ Module ㉓: Hudl Sportscode Bridge │       │ Module ㉔: Tactile War-Room Canvas│
   │ (Bi-Directional XML & Video Sync) │       │ (WebGPU 60 FPS iPad Sandbox)      │
   └─────────────────┬─────────────────┘       └─────────────────┬─────────────────┘
                     │                                           │
   ┌─────────────────▼─────────────────┐       ┌─────────────────▼─────────────────┐
   │ Module ㉕: Opponent Red-Teaming   │       │ Module ㉖: Player Meeting Briefs  │
   │ (Automated Vulnerability Dossiers)│       │ (15–90s Video Clips + Ghost Trails│
   └─────────────────┬─────────────────┘       └─────────────────┬─────────────────┘
                     │                                           │
                     └─────────────────────┬─────────────────────┘
                                           ▼
             ┌───────────────────────────────────────────────────────────┐
             │ Module ㉗: Sovereign Air-Gapped Club Appliance (Local GPU)│
             └───────────────────────────────────────────────────────────┘
```

---

## 2. Module ㉑: Set-Piece Causal Engine (The "Nicolas Jover" Module)

### 2.1 Theoretical Formulation & Mathematical Physics
Set pieces represent approximately **30%–35% of all goals scored in European elite football**. Unlike open play, set-piece sequences initiate from a static spatial state with high clustering density in the penalty area.

#### 1. Ball Delivery Aerodynamics & The Magnus Effect
The 3D trajectory of an inswinging or outswinging delivery is modeled by integrating gravitational, drag, and Magnus forces:
$$m \frac{d\vec{v}_b}{dt} = m\vec{g} - \frac{1}{2}\rho C_d A \|\vec{v}_b\|\vec{v}_b + \frac{1}{2}\rho C_L A \|\vec{v}_b\|^2 \left(\frac{\vec{\omega} \times \vec{v}_b}{\|\vec{\omega} \times \vec{v}_b\|}\right)$$
Where:
* $\vec{v}_b$: Ball velocity vector $[v_x, v_y, v_z]^T$
* $\vec{\omega}$: Angular spin vector (rad/s) determining curl (inswinger vs outswinger)
* $\rho = 1.225\text{ kg/m}^3$: Air density
* $C_d \approx 0.25$: Aerodynamic drag coefficient
* $C_L$: Lift/Magnus coefficient ($C_L \approx \frac{r\omega}{v_b}$)

#### 2. The 6-Yard Box Screening & Contact Graph
In modern corners (e.g. Arsenal's routines under Nicolas Jover), attacking players execute deliberate blocks (picks) to prevent the goalkeeper or primary zonal defender from reaching the delivery zone.

We construct a directed contact graph $G_{\text{set\_piece}} = (V_{\text{box}}, E_{\text{block}})$ at timestamp $t$:
An edge $(p_{\text{attacker}}, p_{\text{defender}}) \in E_{\text{block}}$ exists if:
$$d(p_{\text{attacker}}, p_{\text{defender}}) < 0.8\text{ m} \quad \text{and} \quad \vec{v}_{\text{defender}} \cdot (\vec{p}_{\text{ball}} - \vec{p}_{\text{defender}}) > 0 \quad \text{and} \quad \vec{v}_{\text{attacker}} \cdot \vec{v}_{\text{defender}} < -0.3$$
Screening efficiency is quantified by the **Separation Generated**:
$$\Delta \text{Separation}(p_{\text{target}}, t_{\text{contact}}) = \min_{d \in \text{Defenders}} \|p_{\text{target}} - p_d\|_{t_{\text{contact}}} - \min_{d \in \text{Defenders}} \|p_{\text{target}} - p_d\|_{t_0}$$

### 2.2 Counterfactual Delivery Rollout Queries
The engine allows the set-piece specialist to simulate:
1. **Trajectory Perturbation:** *"What if the delivery was outswinging to the penalty spot with spin $\omega = -25\text{ rad/s}$ rather than an inswinger to the near post?"*
2. **Blocker Positioning Intervention:** *"What if attacker #4 blocked the zonal center-back 1.5 m higher up the pitch?"*
The engine runs 100 stochastic aerial duel rollouts based on player jump reach and historical header conversion probabilities.

---

## 3. Module ㉒: Biomechanical & Physical Telemetry Fusion Engine

### 3.1 Cognitive-Physical Decision Degradation Modeling
At elite intensity, tactical lapses frequently stem from physiological exhaustion. FCIE fuses optical tracking with **Catapult (OpenField)** and **STATSports (Sonra)** GPS/GNSS data at 10–20 Hz.

#### 1. Instantaneous Physiological State Tuple
$$\Phi_{\text{phys}}(p, t) = \langle \text{HR}(t), \text{HSR}_{\text{acc}}(t), P_{\text{met}}(t), v_{\text{inst}}(t), a_{\text{inst}}(t) \rangle$$
Where:
* $\text{HR}(t)$: Instantaneous heart rate (% of max)
* $\text{HSR}_{\text{acc}}(t)$: Accumulated distance covered at high speed ($>19.8\text{ km/h}$)
* $P_{\text{met}}(t)$: Instantaneous metabolic power (W/kg), calculated via di Prampero's energetic model:
  $$P_{\text{met}} = \left(155.4 \cdot \text{ES}^5 - 30.4 \cdot \text{ES}^4 - 43.3 \cdot \text{ES}^3 + 46.3 \cdot \text{ES}^2 + 19.5 \cdot \text{ES} + 3.6\right) \cdot v \cdot \text{KT}$$
  where $\text{ES}$ is equivalent slope derived from acceleration.

#### 2. Fatigue-Adjusted Decision & Reaction Latency
The baseline reaction time $T_{\text{react}}$ in the Spatial Intelligence Engine is dynamically adjusted:
$$T_{\text{react}}(p, t) = T_{\text{base}}(p) \times \left[ 1 + \kappa_1 \left(\frac{\text{HSR}_{t-5\text{min}}}{\text{HSR}_{\text{threshold}}}\right)^2 + \kappa_2 \left(\frac{\text{HR}(t)}{\text{HR}_{\max}}\right)^3 \right]$$
When $T_{\text{react}}$ increases by $>30\%$, the player's closing speed and pitch control radius shrink exponentially, predicting imminent defensive breakdowns.

#### 3. Real-Time Substitution Risk Radar
The API surfaces an automated substitution metric:
$$\text{BreakdownRisk}(p, t) = \text{FatigueIndex}(p, t) \times \text{TacticalLoad}(p, t)$$
Surfaced directly to the High Performance Director to recommend optimal substitution timing before tactical collapse occurs.

---

## 4. Module ㉓: Hudl Sportscode & Video Integration Bridge

### 4.1 Bi-Directional Workflow Integration
Every tier-1 club relies on **Hudl Sportscode**. FCIE functions as an intelligent coprocessor to Sportscode rather than demanding workflow migration.

```
                   HUDL SPORTSCODE BI-DIRECTIONAL BRIDGE
                   
   ┌──────────────────────┐                     ┌──────────────────────┐
   │ FCIE Causal Core     │                     │ Hudl Sportscode      │
   │ (Domino Moments,     │ ──(XML Exporter)──► │ (Analyst Movie &     │
   │  Tactical Phases)    │                     │  Code Matrix Window) │
   └──────────────────────┘                     └──────────┬───────────┘
              ▲                                            │
              │                                            │
              └────────(Analyst Edit Feedback XML)─────────┘
```

### 4.2 Sportscode Open Exchange XML Specification
FCIE automatically generates compliant XML timelines containing:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<file>
  <ALL_INSTANCES>
    <instance>
      <ID>1042</ID>
      <START>4341.20</START>
      <END>4355.80</END>
      <code text="DOMINO_MOMENT_DEFENSIVE_GAP"/>
      <label>
        <group>Player_Responsible</group>
        <text>Declan_Rice_#41</text>
      </label>
      <label>
        <group>Causal_Influence</group>
        <text>0.82</text>
      </label>
      <label>
        <group>Importance_Rank</group>
        <text>1</text>
      </label>
      <label>
        <group>Counterfactual_Delta</group>
        <text>-0.38_xG_Conceded_Avoided</text>
      </label>
      <label>
        <group>Video_Clip_Timestamp</group>
        <text>72:26</text>
      </label>
    </instance>
  </ALL_INSTANCES>
</file>
```

---

## 5. Module ㉔: Interactive Tactile War-Room Sandbox (iPad WebGPU Canvas)

### 5.1 Real-Time Interactive Canvas Specification
Designed specifically for iPad Pro (M-series silicon) and multi-touch boardroom displays:
* **Render Pipeline:** WebGPU / Metal shaders rendering 22 player nodes, ball vector, and pitch control scalar field at 60+ FPS.
* **Touch Event Gesture Engine:**
  * Single tap on player: Freezes video at timestamp $t$ and highlights current passing lanes $\Lambda_t$.
  * Drag-and-drop gesture: Relocates player $p_i$ from $(x, y)$ to $(x', y')$.
  * On-device WebAssembly pitch control solver: Computes new continuous control contours $p_{\text{team}}(x, y, t)$ within **35 ms** locally on the iPad.
* **Streaming Counterfactual Rollouts:**
  * On touch release, an encrypted WebSocket frame transmits the intervention payload `do(p_i = (x', y'))`.
  * The local GPU cluster executes 50 forward rollouts and streams binary coordinate vectors back to the iPad in **< 1.2 seconds**.
  * The canvas renders translucent, animated **Ghost Trails** illustrating the alternative continuation alongside the observed footage.

---

## 6. Module ㉕: Automated Opponent Vulnerability & Red-Teaming Engine

### 6.1 Opposition Exploitation Profiling
Prior to facing Bayern Munich or Arsenal, FCIE mines the opponent's historical match database over the preceding 12 months to isolate systemic tactical vulnerabilities:

1. **Press-Bypass Trigger Isolation:**
   Detects the exact spatial passing combinations that systematically cause the opponent's pressing trap to disconnect:
   $$\text{BypassSuccessRate}(\text{Trigger}) = \frac{N(\text{First Line Bypassed} \mid \text{Trigger Pattern})}{N(\text{Trigger Pattern Attempts})}$$
2. **Weak-Foot High-Pressure Exploitation:**
   Computes individual player turnover risk under high pressure ($>75\%$ intensity) conditioned on approach angle:
   $$\text{TurnoverRisk}(p_{\text{opponent}}, \theta_{\text{press}}) = P(\text{Ball Loss} \mid \text{Angle}(\vec{v}_{\text{press}}) \text{ forces weak foot})$$
3. **Automated 3-Minute Video Briefing Dossier:**
   Headless FFmpeg worker automatically compiles a broadcast-ready tactical package with graphical arrows, spotlighting the 3 primary spatial zones to overload.

---

## 7. Module ㉖: 90-Second Player Meeting Micro-Clip Generator

### 7.1 Player-Centric Micro-Learning Pipeline
Elite players absorb tactical instructions best through high-impact, short-form visual briefings:
1. **Automated Clip Generation:**
   For each starting player, FCIE isolates the 3 most pivotal Domino Moments involving that player from the weekend fixture.
2. **Visual Spotlight & Ghost Overlay:**
   * Player is spotlighted; background pitch is slightly dimmed.
   * At the decision timestamp, action freezes for 1.5 seconds.
   * A golden **Ghost Trail** animates the counterfactual action (e.g. holding position vs jumping out).
3. **Natural-Language Voice & Text Briefing:**
   Coach AI generates an audio and text prompt strictly grounded in the causal data:
   > *"Minute 68: Hold your reference line here. Stepping out created an 11-meter central passing channel. Holding position denies their counter-attack in 82% of simulated rollouts."*
4. **Distribution:**
   Dispatched automatically to player tablet endpoints via encrypted club mobile portals.

---

## 8. Module ㉗: Sovereign Air-Gapped Club Security Architecture

### 8.1 On-Premises GPU Hardware Topology
To eliminate cloud security and data leak concerns, FCIE provides a turnkey on-premises deployment topology:

```text
               SOVEREIGN ON-PREMISES CLUB ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────┐
│  LOCAL CLUB NETWORK / TRAINING GROUND DATA CENTER                      │
│                                                                        │
│  Dual-GPU Server Appliance (e.g. 2x NVIDIA A6000 / H100 PCIe)          │
│  ├── Local Containerized Stack (MicroK8s / Docker Compose)             │
│  │   ├── Ingestion & RT-DETR/ByteTrack Worker Pool                     │
│  │   ├── Causal Engine & Kinematic Simulator Workers                   │
│  │   ├── PostgreSQL 16 + Apache AGE Graph Extension                    │
│  │   ├── DuckDB + Local Parquet Timeseries Store                       │
│  │   ├── Qdrant Local Vector Engine                                    │
│  │   └── vLLM Local Engine (Qwen-2.5-14B-Instruct / Llama-3.1-8B)      │
│  │                                                                     │
│  ├── Hardware Security Module (HSM / AES-256 Volume Encryption)        │
│  └── Local 10GbE High-Bandwidth Video Ingestion Storage                │
│                                                                        │
│  Client Workstations: Film Room Desktops, Analyst Macs, Staff iPads    │
└────────────────────────────────────────────────────────────────────────┘
            X  (NO EXTERNAL CLOUD TELEMETRY / ZERO LEAK RISK)
```

1. **Air-Gapped Operation:** Zero outbound internet communication required for inference, causal analysis, or LLM explanation.
2. **Model Weight Verification:** Model updates shipped via signed, encrypted offline container images.
3. **Enterprise Authentication:** Local SAML 2.0 / Active Directory / Okta SSO integration with granular role-based access control (RBAC).

---

## 9. Comprehensive Pydantic Data Schemas

```python
# libs/schemas/enterprise_schemas.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class SetPieceType(str, Enum):
    CORNER_INSWING = "CORNER_INSWING"
    CORNER_OUTSWING = "CORNER_OUTSWING"
    CORNER_SHORT = "CORNER_SHORT"
    FREE_KICK_DIRECT = "FREE_KICK_DIRECT"
    FREE_KICK_CROSS = "FREE_KICK_CROSS"
    THROW_IN_LONG = "THROW_IN_LONG"

class ScreeningInteraction(BaseModel):
    blocker_player_id: UUID
    blocked_defender_id: UUID
    contact_timestamp_ms: int
    separation_generated_m: float
    screen_legality_score: float  # [0.0 - 1.0]

class SetPieceEvent(BaseModel):
    event_id: UUID
    match_id: UUID
    timestamp_ms: int
    set_piece_type: SetPieceType
    taker_player_id: UUID
    target_zone: str  # NEAR_POST, CENTRAL_6YD, FAR_POST, EDGE_OF_BOX
    delivery_speed_m_s: float
    delivery_spin_rad_s: float
    trajectory_points_3d: list[list[float]]  # [[x, y, z], ...]
    screening_interactions: list[ScreeningInteraction]
    observed_xg: float
    counterfactual_xg_delta: float
    schema_version: str = "1.2.0"

class GPSTelemetryFrame(BaseModel):
    timestamp_ms: int
    player_id: UUID
    heart_rate_bpm: int | None = None
    metabolic_power_w_kg: float
    cumulative_hsr_distance_m: float
    instantaneous_speed_m_s: float
    instantaneous_accel_m_s2: float
    calculated_reaction_delay_ms: float
    fatigue_index: float = Field(..., ge=0.0, le=1.0)

class SportscodeExportInstance(BaseModel):
    instance_id: int
    start_seconds: float
    end_seconds: float
    code: str
    labels: dict[str, str]

class WarRoomInterventionPayload(BaseModel):
    match_id: UUID
    timestamp_ms: int
    player_id: UUID
    original_coords: list[float]  # [x, y]
    intervened_coords: list[float]  # [x', y']
    num_rollouts: int = 50
    horizon_seconds: float = 4.0

class PlayerMeetingBriefing(BaseModel):
    briefing_id: UUID
    player_id: UUID
    match_id: UUID
    title: str
    timestamp_start_ms: int
    timestamp_end_ms: int
    video_url: str
    domino_moment_id: UUID
    ghost_trail_coords: list[list[float]]  # 2D coordinates over time
    coach_directive_text: str
    audio_voiceover_url: str | None = None
    confidence_score: float
```

---

## 10. Summary: The Tier-1 Enterprise Competitive Advantage

By embedding Modules ㉑–㉗ into the FCIE architecture:
1. **Analyst Friction is Zero:** Analysts export Domino Moments directly to **Sportscode XML** without learning a new user interface.
2. **Dead-Ball Mastery is Unlocked:** Set-piece coaches (like Nicolas Jover) gain a dedicated 3D aerodynamic screening simulator.
3. **Tactical & Physical Data Unite:** GPS load telemetry provides biological justification for tactical breakdowns.
4. **Managers Get a Tactile War-Room:** Arteta, Kompany, and Guardiola can move players on an iPad canvas and observe instant counterfactual simulations.
5. **Data Sovereignty is Absolute:** On-premises air-gapped GPU servers ensure that proprietary tactics and scouting targets never touch a third-party cloud.
