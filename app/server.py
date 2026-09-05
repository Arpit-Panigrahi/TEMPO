"""
TEMPO Tactical Studio: High-Performance FastAPI Application.
Powers real-time interactive match scrubbing, Domino Moment inspections,
Spearman Pitch Control rendering, and counterfactual simulation playback.
"""

import os
import sys
from pathlib import Path

# Add src to python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from tempo.data.episode_catalog import EpisodeCatalog
from tempo.causal.tactical_llm import GeminiTacticalNarrator


class AIDossierRequest(BaseModel):
    api_key: Optional[str] = None


app = FastAPI(
    title="TEMPO Tactical Studio",
    description="Enterprise Causal Football Intelligence & Domino Moment Orchestrator",
    version="1.0.0"
)

# Initialize in-memory episode catalog & Gemini Narrator
catalog = EpisodeCatalog(str(ROOT_DIR / "data" / "metrica"))
narrator = GeminiTacticalNarrator()

# Disable browser caching for live tactical updates
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Mount static assets
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """Serves the main TEMPO Tactical Studio HTML5 UI."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"status": "TEMPO Tactical Studio API is online. Frontend static assets loading..."})
    return FileResponse(index_file)


@app.get("/api/llm_status")
async def get_llm_status():
    """Returns whether a Gemini API key is configured."""
    return {
        "has_api_key": narrator.has_api_key(),
        "model": narrator.DEFAULT_MODEL
    }


@app.get("/api/status")
async def get_status():
    """System status and data availability check."""
    manifest = catalog.get_manifest()
    return {
        "status": "online",
        "engine": "TEMPO SCM Causal Engine v1.0",
        "dataset": "Metrica Sports Game 1 (25 FPS Optical)",
        "indexed_moments_count": len(manifest),
        "physics_engine": "William Spearman (2018) PPCF"
    }


@app.get("/api/episodes")
async def list_episodes():
    """Returns the catalog manifest of all indexed goals and transition shots."""
    manifest = catalog.get_manifest()
    return {"episodes": manifest}


@app.get("/api/episode/{episode_id}")
async def get_episode(episode_id: str):
    """Returns the complete tactical tracking package and causal intelligence for an episode."""
    try:
        data = catalog.get_episode_data(episode_id)
        if narrator.has_api_key() and data.get("cf_dossier", {}).get("source") != "gemini-ai":
            data["cf_dossier"] = narrator.generate_dossier(data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load episode {episode_id}: {str(e)}")


@app.post("/api/generate_ai_dossier/{episode_id}")
async def generate_ai_dossier(episode_id: str, request: Optional[AIDossierRequest] = None):
    """Generates an AI-powered tactical dossier using Gemini (with fallback)."""
    try:
        ep_data = catalog.get_episode_data(episode_id)
        api_key = request.api_key if request else None
        if api_key:
            narrator.set_api_key(api_key)

        dossier = narrator.generate_dossier(ep_data, api_key=api_key)
        ep_data["cf_dossier"] = dossier
        return {
            "status": "success",
            "source": dossier.get("source", "unknown"),
            "model": dossier.get("model", "unknown"),
            "dossier": dossier
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pitch_control/{episode_id}/{frame_idx}")
async def get_frame_pitch_control(episode_id: str, frame_idx: int, counterfactual: bool = False):
    """Computes and returns the 2D Pitch Control surface for a specific frame."""
    try:
        ep = catalog.get_episode_data(episode_id)
        if frame_idx < 0 or frame_idx >= ep["total_frames"]:
            raise HTTPException(status_code=400, detail=f"Invalid frame index {frame_idx}")

        import numpy as np
        # Convert list coords back to arrays
        h_coords = np.array([[pt[0] if pt else np.nan, pt[1] if pt else np.nan] for pt in ep["home_coords"][frame_idx]])
        a_coords = np.array([[pt[0] if pt else np.nan, pt[1] if pt else np.nan] for pt in ep["away_coords"][frame_idx]])
        
        # Zero velocity proxy for single-frame grid
        h_vels = np.zeros_like(h_coords)
        a_vels = np.zeros_like(a_coords)

        if ep["attacking_team"] == "Home":
            att_c, att_v = h_coords, h_vels
            def_source = ep["cf_def_coords"][frame_idx] if counterfactual else ep["away_coords"][frame_idx]
            def_c = np.array([[pt[0] if pt else np.nan, pt[1] if pt else np.nan] for pt in def_source])
            def_v = a_vels
        else:
            att_c, att_v = a_coords, a_vels
            def_source = ep["cf_def_coords"][frame_idx] if counterfactual else ep["home_coords"][frame_idx]
            def_c = np.array([[pt[0] if pt else np.nan, pt[1] if pt else np.nan] for pt in def_source])
            def_v = h_vels

        res = catalog.pc_engine.compute_frame_pitch_control(att_c, att_v, def_c, def_v)
        
        # Downsample grid for ultra-fast JSON transmission (25 x 16)
        ppcf_raw = res["ppcf"]
        ppcf_downsampled = ppcf_raw[::2, ::2]
        
        return {
            "episode_id": episode_id,
            "frame_idx": frame_idx,
            "is_counterfactual": counterfactual,
            "ppcf": [[round(float(val), 2) for val in row] for row in ppcf_downsampled],
            "att_area_m2": round(res["att_controlled_area"], 1),
            "def_area_m2": round(res["def_controlled_area"], 1),
            "danger_space_m2": round(res["dangerous_space_control"], 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
