"""
TEMPO Gemini AI Tactical Narrator.
Integrates Google Gemini to generate high-fidelity, lucid tactical debriefs,
causal domino explanations, and training ground prescriptions from quantitative tracking metrics.
Includes automated fallback to TEMPO rule-based heuristic engine when offline or unauthenticated.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class GeminiTacticalNarrator:
    """Generates broadcast-grade tactical debriefs and counterfactual analyses using Gemini."""

    DEFAULT_MODEL = "gemini-2.5-flash"
    BACKUP_MODEL = "gemini-1.5-flash"

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def set_api_key(self, api_key: str):
        """Updates the active Gemini API key in memory."""
        if api_key and api_key.strip():
            self._api_key = api_key.strip()

    def has_api_key(self) -> bool:
        """Returns True if a valid API key is configured."""
        return bool(self._api_key and len(self._api_key) > 10)

    def generate_dossier(self, episode_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates an in-depth tactical dossier.
        If Gemini API key is available, calls Gemini LLM.
        Otherwise, falls back to the deterministic TEMPO heuristic dossier.
        """
        active_key = api_key or self._api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        ep_id = episode_data.get("meta", {}).get("id", "episode")

        # Check cache
        cache_key = f"{ep_id}_{bool(active_key)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # If API key available, attempt Gemini generation
        if active_key and len(active_key) > 10:
            try:
                ai_dossier = self._call_gemini(episode_data, active_key)
                if ai_dossier:
                    self._cache[cache_key] = ai_dossier
                    return ai_dossier
            except Exception as e:
                print(f"[TEMPO Gemini AI] API Call failed: {e}. Falling back to rule engine.")

        # Fallback to rule engine
        fallback = self._build_fallback_dossier(episode_data)
        self._cache[cache_key] = fallback
        return fallback

    def _call_gemini(self, ep: Dict[str, Any], api_key: str) -> Optional[Dict[str, Any]]:
        """Calls Google Generative Language API with structured JSON output."""
        meta = ep.get("meta", {})
        jersey = ep.get("causal_defender_jersey", "21")
        lead_time = ep.get("lead_time_sec", 4.28)
        domino_time = ep.get("domino_time_sec", 3595.9)
        threat_time = ep.get("threat_time_sec", 3600.2)
        actual_gap = ep.get("actual_gap_width_m", 7.3)
        cf_gap = ep.get("cf_gap_width_m", 3.2)
        risk_reduction = ep.get("risk_reduction_pct", 29.0)
        error_desc = ep.get("causal_error_desc", "Stepped out of line, opening channel behind")
        is_goal = meta.get("is_goal", True)
        label = meta.get("label", "Match Sequence")
        att_team = ep.get("attacking_team", "Home")

        mins = int(domino_time // 60)
        secs = domino_time % 60
        gap_diff = round(actual_gap - cf_gap, 1)

        prompt = f"""You are an elite UEFA Pro License Tactical Director & Spatial Football Analytics Expert (combining the philosophies of Roberto De Zerbi, Marcelo Bielsa, and William Spearman).

Analyze this quantitative tracking breakdown from Metrica Sports Game 1:
- Episode Context: {label} (Attacking Team: {att_team})
- Domino Rupture Inflection: {mins:02d}:{secs:04.1f} ({lead_time:.2f} seconds before the terminal shot)
- Causal Root Defender: Player #{jersey}
- Quantitative Tracking Error: {error_desc}
- Ruptured Defensive Channel: {actual_gap:.1f}m gap created between center-backs (destroyed offside trap)
- Counterfactual Intervention: What if Defender #{jersey} maintains disciplined 18m zonal depth?
- Spatial Mitigation Impact: Channel width compressed from {actual_gap:.1f}m to {cf_gap:.1f}m ({gap_diff:.1f}m reduction)
- Threat Suppression (Spearman PPCF): -{risk_reduction:.1f}% dangerous space conceded inside the box
- Tactical Consequence: Striker caught offside, through-ball blocked, goal prevented.

Generate a deeply insightful, highly lucid tactical dossier formatted as strict JSON with this exact schema:
{{
  "headline": "Short punchy tactical case study title",
  "executive_summary": "2-3 lucid, professional sentences explaining the causal breakdown and the counterfactual intervention.",
  "actual_reality": {{
    "label": "Actual Match Breakdown",
    "trigger": "Detailed sentence explaining how the opponent's transition or decoy run triggered the defender's mistake.",
    "error_mechanism": "Tactical explanation of Player #{jersey}'s body orientation, jump, or line abandonment.",
    "tactical_cost": "Explanation of the {actual_gap:.1f}m corridor opened and why the offside line broke."
  }},
  "counterfactual_simulation": {{
    "label": "Counterfactual Intervention (What-If)",
    "action": "Precise spatial adjustment Defender #{jersey} must make to preserve the 18m line.",
    "channel_denial": "How compressing the gap by {gap_diff:.1f}m physically closes the line-breaking pass vector.",
    "offside_trap": "How maintaining the line leaves the opponent striker in an illegal offside position.",
    "pitch_control_impact": "How pitch dominance is shifted away from the attack by -{risk_reduction:.1f}%."
  }},
  "coaching_directives": {{
    "player_instruction": "Individual coaching cue for Player #{jersey} (e.g. read front foot, hip orientation, hold plane).",
    "unit_coordination": "Defensive 4-chain directive (e.g. communication trigger, compact spacing, verbal hold call).",
    "training_drill": "Specific high-intensity training drill name and setup to ingrain this zonal habit."
  }}
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.DEFAULT_MODEL}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                body = json.loads(response.read().decode("utf-8"))
                candidates = body.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "")
                        data = json.loads(text)
                        data["source"] = "gemini-ai"
                        data["model"] = self.DEFAULT_MODEL
                        return data

        return None

    def _build_fallback_dossier(self, ep: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic expert heuristic fallback matching elite coaching standards."""
        jersey = ep.get("causal_defender_jersey", "21")
        lead_time = ep.get("lead_time_sec", 4.28)
        domino_time = ep.get("domino_time_sec", 3595.9)
        actual_gap = ep.get("actual_gap_width_m", 7.3)
        cf_gap = ep.get("cf_gap_width_m", 3.2)
        risk_reduction = ep.get("risk_reduction_pct", 29.0)
        error_desc = ep.get("causal_error_desc", "Stepped out of line, opening channel behind")
        gap_diff = round(actual_gap - cf_gap, 1)
        mins = int(domino_time // 60)
        secs = domino_time % 60

        return {
            "headline": f"What-If Tactical Dossier: Defender #{jersey} Zonal Line Discipline",
            "executive_summary": (
                f"At t - {lead_time:.2f}s before the terminal shot ({mins:02d}:{secs:04.1f}), the defensive backline suffered a structural domino inflection. "
                f"By maintaining disciplined zonal positioning along the 18m offside line, Defender #{jersey} constricts the passing channel by {gap_diff:.1f}m "
                f"and denies -{risk_reduction:.1f}% of attacking dangerous space, completely neutralizing the goal-scoring sequence."
            ),
            "actual_reality": {
                "label": "Actual Match Breakdown",
                "trigger": f"Opponent attacking transition creates forward running momentum at {mins:02d}:{secs:04.1f}.",
                "error_mechanism": error_desc,
                "tactical_cost": (
                    f"A {actual_gap:.1f}m vertical passing corridor was ruptured between the center-backs. "
                    f"The offside line collapsed, giving the attacker an unpressured receiving and shooting lane {lead_time:.1f}s later."
                )
            },
            "counterfactual_simulation": {
                "label": "Counterfactual Intervention (What-If)",
                "action": f"Defender #{jersey} resists the decoy run and anchors in lockstep with adjacent center-backs.",
                "channel_denial": f"Passing channel compressed from {actual_gap:.1f}m to {cf_gap:.1f}m ({gap_diff:.1f}m sealed). Line-breaking pass is physically denied.",
                "offside_trap": "The flat 4-man offside wall remains intact; the penetrating striker is caught offside at the moment of pass release.",
                "pitch_control_impact": f"Opponent dangerous space control in the penalty area drops by -{risk_reduction:.1f}%, completely aborting the scoring chance."
            },
            "coaching_directives": {
                "player_instruction": f"Player #{jersey}: Read the passer's hip angle. Never break the backline plane unless a central midfielder drops to cover the vacated space.",
                "unit_coordination": "Defensive 4-Chain: Maintain 6-8m inter-defender spacing. If one center-back is provoked, the adjacent defender must call 'HOLD' to preserve the offside trap.",
                "training_drill": "3-Zone Defensive Elasticity Exercise: 4 defenders vs 5 attackers focusing on offside line preservation against false-9 decoy movements."
            },
            "source": "tempo-rule-engine",
            "model": "SCM Causal Heuristics v1.0"
        }
