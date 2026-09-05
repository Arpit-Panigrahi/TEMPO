#!/usr/bin/env python3
"""
TEMPO Tactical Studio Launcher.
Starts the FastAPI application and provides instant access to the interactive studio.
Usage:
    python3 run_studio.py
"""

import sys
from pathlib import Path

# Add src and root to python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "src"))
sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from app.server import app


def main():
    print("=" * 72)
    print("  TEMPO: Tactical Emergence & Multi-Agent Predictive Orchestrator")
    print("  Booting Tactical Studio Web Application...")
    print("=" * 72)
    print("  • Server:       Uvicorn ASGI Engine")
    print("  • Local URL:    http://127.0.0.1:8000")
    print("  • Dataset:      Metrica Sports Game 1 (25 FPS Optical Tracking)")
    print("  • Physics:      William Spearman (2018) Pitch Control Engine")
    print("=" * 72)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
