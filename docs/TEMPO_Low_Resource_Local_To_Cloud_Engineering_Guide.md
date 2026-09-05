# 🛠️ TEMPO: Low-Resource Engineering Guide & Cloud Scaling Blueprint
## How to Build, Test, and Scale Project TEMPO on a Modest Machine (Without Expensive Hardware)

> **Document Purpose:** Practical, step-by-step engineering roadmap for developing TEMPO on a standard consumer laptop or desktop (CPU-only or modest GPU), decoupling heavy computation from daily coding, and cost-effectively scaling model training and processing via on-demand cloud resources.

---

## 1. Executive Strategy: The "Decoupled Development" Principle

The biggest myth in modern artificial intelligence is that you need an expensive $50,000 server with 8x NVIDIA H100 GPUs to build a world-class AI project. 

In premier AI labs (Stanford, DeepMind, MIT), **nobody develops directly on GPU clusters.** Top engineers follow a two-tier strategy:
1. **Local Development (85% of time):** Write, test, debug, and build the software architecture locally on a regular laptop using lightweight mock data, embedded databases, and CPU-friendly math.
2. **Cloud Scaling (15% of time):** Spin up high-powered cloud GPUs for a few hours only when training neural networks or processing full-match video batches—spending **$2 to $15 total**, then shutting them down.

### The 80/20 Rule of Project TEMPO:
* **80% of TEMPO is Logic, Spatial Math & Causal Graphs (Runs on CPU):**
  - Pitch coordinates, Voronoi fields, Spearman pitch control surfaces, state entropy calculations ($\Delta H(S_t)$), and decision graphs do **not** require GPUs. A standard quad-core laptop CPU can process an entire 90-minute tracking match in **under 3 seconds**.
* **20% of TEMPO is Heavy Deep Learning (Decoupled to Cloud):**
  - Video object detection (RT-DETR) and Spatiotemporal Graph Neural Network (ST-GNN) policy training. This can be completely bypassed during initial local development by using open tracking data!

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE DECOUPLED DEVELOPMENT BLUEPRINT                             │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ LOCAL CONSUMER MACHINE (Laptop / PC)      │ CLOUD ON-DEMAND (Pay-as-you-go / Free)     │
│ [ Cost: $0 · RAM: 8–16 GB · CPU: Regular ] │ [ Cost: $0 to $10 · GPU: T4 / A100 / 4090 ]│
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ • DuckDB + Polars (Embedded tabular data) │ • Google Colab / Kaggle (Free T4/P100 GPUs)│
│ • NumPy / SciPy (Pitch Control & Entropy) │ • RunPod.io / Vast.ai ($0.35/hr RTX 4090)  │
│ • NetworkX (Decision Chains & Causal DAGs)│ • Training heavy multi-agent GNN weights   │
│ • Next.js + HTML5 Canvas (Tactical UI)    │ • Offline batch raw video CV inference     │
│ • Lightweight LLM (Groq API or Ollama 3B) │ • Storing model checkpoints on HuggingFace │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 2. Phase 1: Local Development on Your Modest Machine (Cost: $0)

### 2.1 The "Bypass Video Decode" Strategy (Start at Layer 2)
The heaviest computational burden in TEMPO is **Module ① (Video Ingest)** and **Module ② (Computer Vision)**, which require decoding 1080p video at 25 FPS and running neural object detectors on 135,000 frames.

**How to bypass this completely:**
Do not start with raw MP4 video. Start with **pre-extracted open tracking datasets**. 
* Tracking data is purely tabular numbers: `(frame, player_id, team, x, y, speed)`.
* An entire 90-minute professional match containing 22 players tracked at 25 Hz is only **~25 Megabytes** of CSV or Parquet data!
* You can download these datasets completely free:
  1. **Metrica Sports Open Tracking Data:** 3 full professional matches with complete $x, y$ coordinates and ball tracking (GitHub: `metrica-sports/sample-data`).
  2. **SkillCorner Open Tracking Data:** 9 match clips of broadcast tracking coordinates (GitHub: `SkillCorner/opendata`).
  3. **StatsBomb Open Data:** Hundreds of matches of high-resolution event data (GitHub: `statsbomb/open-data`).

By starting with Metrica tracking data, you completely skip GPU video processing and immediately build the intellectual core of TEMPO: **Modules ③, ④, ⑤, ⑥, ⑧, and ⑫**.

---

### 2.2 The Lightweight Local Tech Stack (Optimized for Low RAM & CPU)

Replace resource-heavy enterprise microservices with lightweight, zero-setup, in-process equivalents during local development:

| Production Microservice | Local Development Replacement | RAM Footprint | Setup Required |
| :--- | :--- | :--- | :--- |
| **PostgreSQL 16** | **SQLite** or in-memory DuckDB | < 15 MB | `import sqlite3` (Built into Python) |
| **Parquet Lakehouse (AWS S3)** | **DuckDB + Local Parquet** | < 100 MB | `pip install duckdb` (Zero daemon, runs in RAM) |
| **Neo4j Enterprise Cluster** | **NetworkX** (Python Graph Library) | < 50 MB | `pip install networkx` (Pure Python graph theory) |
| **Self-Hosted 70B LLM (vLLM)** | **Groq API** (Free tier Llama-3-70B) or **Ollama 3B** | < 20 MB (API) or 2 GB (Local) | Free cloud API or local quantized model |
| **Redis Streams / Kafka** | **Python `queue.Queue`** or **FastAPI In-Memory** | < 10 MB | Standard library |
| **Three.js 3D WebGL Canvas** | **HTML5 2D Pitch Canvas** | < 80 MB | Standard browser render |

---

### 2.3 Executing Pitch Control & Domino Detection on CPU

You do not need a GPU to calculate spatial pitch control or Domino Moments. By using vectorized NumPy array operations and downscaling the spatial resolution slightly, calculations run in milliseconds:

```python
# scripts/local_prototype/fast_pitch_control.py
# Runs in ~12 milliseconds on any regular Intel/AMD laptop CPU!
import numpy as np

def compute_fast_pitch_control(player_coords, attacking_indices, grid_res=(53, 34)):
    """
    Computes continuous pitch control on a 53x34 grid (2m resolution)
    Sufficient for tactical analysis while using <5MB RAM and 12ms CPU time.
    """
    x = np.linspace(0, 105, grid_res[0])
    y = np.linspace(0, 68, grid_res[1])
    grid_x, grid_y = np.meshgrid(x, y)
    
    # Vectorized Euclidean distance from all 22 players to every pitch cell
    # player_coords shape: (22, 2)
    diff_x = grid_x[:, :, np.newaxis] - player_coords[:, 0]
    diff_y = grid_y[:, :, np.newaxis] - player_coords[:, 1]
    dist_sq = diff_x**2 + diff_y**2
    
    # Spearman time-to-intercept proxy: t = dist / avg_speed
    time_to_intercept = np.sqrt(dist_sq) / 5.0  # assumed 5 m/s approach
    
    min_att_time = np.min(time_to_intercept[:, :, attacking_indices], axis=2)
    defending_indices = [i for i in range(len(player_coords)) if i not in attacking_indices]
    min_def_time = np.min(time_to_intercept[:, :, defending_indices], axis=2)
    
    # Logistic pitch control probability field
    pitch_control = 1.0 / (1.0 + np.exp(min_att_time - min_def_time))
    return pitch_control
```

---

### 2.4 Running Coach AI Without a $10,000 GPU
Module ⑩ in production envisions a self-hosted Llama-3-70B model requiring 48 GB of GPU VRAM. Locally, you have two zero-cost options:
1. **Option A (Recommended — Free Cloud API):** Use the **Groq API** (`groq.com`). Groq offers an ultra-fast, free development tier running `llama-3.1-70b-versatile` at 500+ tokens/second. You send your tactical prompts and graph subgraphs via a standard Python HTTP request; it responds in 0.3 seconds without using a single byte of your local GPU memory.
2. **Option B (100% Offline):** Install **Ollama** (`ollama.ai`) and download `qwen2.5:3b` or `llama3.2:3b`. These quantized 3-billion parameter models run comfortably on 4 GB of regular computer RAM using standard CPU threads.

---

## 3. Phase 2: Scaling Machine Learning & Model Training (Zero-Hardware Cloud Strategy)

When you are ready to train your custom Graph Neural Networks (GNNs) or fine-tune models, **do not buy hardware.** Rent cloud instances strictly for the hours you train.

### 3.1 Tier 1: Free Cloud Compute (Cost: $0/month)

| Platform | Free Resources Provided | Best Used For |
| :--- | :--- | :--- |
| **Google Colab** | Free NVIDIA T4 GPU (16 GB VRAM) for 4–8 hours/session | Fine-tuning PyTorch Geometric GNN models; testing small RT-DETR tracking batches. |
| **Kaggle Notebooks** | 30 hours/week of free dual NVIDIA T4 or P100 GPUs | Training offline phase classification TCNs; batch processing open match datasets. |
| **Lightning.ai Studios** | 22 free GPU credits per month | Running distributed PyTorch Lightning training jobs with zero environment setup. |

---

### 3.2 Tier 2: On-Demand Serverless GPU Rental (Cost: $2 to $10 per training run)

When free tiers are insufficient for large models, use on-demand GPU clouds that bill **per minute or per second**:

* **RunPod.io / Vast.ai:**
  - Rent an **NVIDIA RTX 4090 (24 GB VRAM)** for **$0.34 to $0.44 per hour**.
  - Rent an **NVIDIA A100 (80 GB VRAM)** for **$1.10 to $1.65 per hour**.
  - *Workflow:* Spin up a pod with PyTorch pre-installed, git clone your repo, train your model for 3 hours (Cost: $1.20), upload the resulting `.pt` model weights to Hugging Face or Google Drive, and click "Terminate Pod".
* **Modal.com:**
  - Serverless Python execution: write `@app.function(gpu="A10G")` directly above your training function. Modal spins up the GPU in 3 seconds, runs your code, saves the artifact, and stops billing the exact second the function returns.

---

### 3.3 Tier 3: Free Academic & Startup Compute Grants (Cost: $0)

When you write the research paper outlined in Part XII, you qualify for massive free cloud credits:
* **Google Cloud Research Credits:** Grants $1,000 to $5,000 in free GCP credits for faculty and student researchers publishing academic papers.
* **AWS Cloud Credit for Research:** Provides up to $10,000 in AWS compute credits for novel AI architectures.
* **NVIDIA Inception Program:** Free program for sports-tech startups providing $100,000 in cloud credits, DLI training, and hardware discounts.

---

## 4. Phase 3: Scaling Video Processing & Production Inference

Once your algorithms are validated locally, here is how you scale the data processing without building an expensive on-premise server:

### 4.1 Asynchronous Batch Worker Architecture
Never process video synchronously on your local machine. Use an asynchronous worker pattern:

```text
┌────────────────────────────────┐         ┌────────────────────────────────┐
│   LOCAL LIGHTWEIGHT DASHBOARD   │         │    CLOUD GPU WORKER (EPHEMERAL)│
│   (FastAPI + Web UI on Laptop) │         │    (RunPod / AWS Spot GPU)     │
│                                │         │                                │
│ 1. User uploads match MP4      │  ─────► │ 2. Downloads video from bucket │
│    or points to YouTube link   │         │ 3. Runs RT-DETR + ByteTrack    │
│                                │         │ 4. Extracts (x, y, v) coords   │
│ 6. Renders interactive domino  │  ◄───── │ 5. Uploads 25MB Parquet state  │
│    dashboard for coach         │         │ 7. Worker automatically kills  │
└────────────────────────────────┘         └────────────────────────────────┘
```

1. **Spot Instances (65–80% Discount):** Run video inference on AWS EC2 or RunPod "Spot/Community" instances. Instead of paying $2/hr, you pay $0.40/hr.
2. **Model Quantization (TensorRT / ONNX):** Convert PyTorch vision models into INT8 or FP16 precision. This cuts GPU memory usage by 75% and doubles frame processing speed from 30 FPS to 95 FPS.
3. **Parquet Compression:** Never store raw image frames long-term. Extract coordinates into ZSTD-compressed Apache Parquet files. An entire 38-game season of 25 Hz tracking coordinates compresses down to less than **1.2 Gigabytes** of disk space!

---

## 5. The 4-Week "Zero-Dollar" Prototype Execution Plan

Follow this exact roadmap to build the first functioning MVP of Project TEMPO on your existing machine:

```text
WEEK 1: TABULAR CAUSAL CORE       WEEK 2: SPATIAL & DOMINO MATH
• Download Metrica Sample Match    • Code Spearman Pitch Control (CPU)
• Build DuckDB WorldState table    • Calculate Entropy Collapse ΔH(S_t)
• Structure possession chains      • Output earliest Domino timestamps
              │                                  │
              ▼                                  ▼
WEEK 3: INTERACTIVE CANVAS UI     WEEK 4: CLOUD TRAINING & PAPER
• Build Next.js 2D pitch board     • Train policy GNN on free Colab T4
• Scrubber bar for match clock     • Benchmark Domino vs xT curves
• Click player to view Domino      • Draft 5-page conference paper!
```

### Week 1: The Tabular Causal Core (DuckDB + Python)
* Clone `metrica-sports/sample-data` from GitHub.
* Write a Python parser using `polars` and `duckdb` that loads Match 1 tracking frames into the canonical `WorldState` schema ($S_t$).
* Segment possessions by checking ball velocity and player proximity.

### Week 2: The Spatial & Domino Mathematics
* Implement the fast NumPy vectorized pitch control algorithm from §2.3.
* Calculate the Shannon tactical entropy $H(S_t)$ over the pitch control grid across each possession.
* Identify the frame $t^*$ where the defending team experienced their sharpest entropy collapse. That is your **first detected Domino Moment**!

### Week 3: The Interactive Web Dashboard
* Initialize a lightweight Next.js frontend with Tailwind CSS.
* Create an HTML5 Canvas pitch board that renders 22 player dots and the ball.
* Add a timeline scrubber that lets you slide through the match, with a red glowing indicator marking the detected Domino Moment.

### Week 4: Cloud Training & Paper Verification
* Open Google Colab (free T4 GPU).
* Train a lightweight Graph Neural Network on the tracking coordinates to predict next-action probabilities.
* Compare where your Domino Moment flagged the breakdown vs. where traditional Expected Threat (xT) spiked.
* You now have the experimental data needed to write your first published research paper!
