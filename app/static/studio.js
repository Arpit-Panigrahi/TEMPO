/**
 * TEMPO Tactical Studio: Broadcast-Quality Tactical Canvas Engine.
 * Features:
 * - Spotlight Focus: Dims non-involved players to 25% opacity so attention snaps to the breakdown
 * - Clean Geometry: Minimalist backline & channel gap dimensions (no giant noisy polygons)
 * - Clear Counterfactuals: Emerald anchor dot + subtle ghost circle of actual mistake
 * - 0.5x Half-Speed Default: Smooth playback speed allowing human perception of player motion
 * - Dedicated HTML Narrative Banner: Clear context without canvas obstruction
 * - Deep What-If Tactical Dossier & Modal: Lucid textual analysis, SCM cascade & coaching drills
 * - Gemini AI Integration: Dynamic on-demand tactical debriefs powered by Google Gemini 2.5 Flash
 */

// Global Studio State
const state = {
  episode: null,
  currentFrame: 0,
  isPlaying: false,
  playbackSpeed: 0.5, // Half-speed default
  mode: "actual", // "actual" | "cf" | "compare"
  focusMode: true, // Spotlight mode active by default
  isLoopingRupture: false,
  showHull: false,
  showHeatmap: false,
  lastTimestamp: 0,
  frameAccumulator: 0,
  pulsePhase: 0,
  ballTrail: []
};

// Canvas & Scaling
const canvas = document.getElementById("pitchCanvas");
const ctx = canvas.getContext("2d");
const PITCH_SCALE = 10.0; // 105m -> 1050px, 68m -> 680px

// DOM Elements - Header
const matchSelect = document.getElementById("matchSelect");
const episodeSelect = document.getElementById("episodeSelect");
const speedSelect = document.getElementById("speedSelect");
const geminiConfigBtn = document.getElementById("geminiConfigBtn");

// DOM Elements - Pitch Floating Bar
const modeActualBtn = document.getElementById("modeActualBtn");
const modeCFBtn = document.getElementById("modeCFBtn");
const modeCompareBtn = document.getElementById("modeCompareBtn");
const jumpDominoBtn = document.getElementById("jumpDominoBtn");
const jumpThreatBtn = document.getElementById("jumpThreatBtn");
const toggleFocusBtn = document.getElementById("toggleFocusBtn");
const toggleHullBtn = document.getElementById("toggleHullBtn");
const toggleHeatmapBtn = document.getElementById("toggleHeatmapBtn");

// DOM Elements - Tactical Narrative Banner
const tacticalBanner = document.getElementById("tacticalBanner");
const bannerIcon = document.getElementById("bannerIcon");
const bannerText = document.getElementById("bannerText");

// DOM Elements - Sidebar Cards
const threatBadge = document.getElementById("threatBadge");
const gaugeBar = document.getElementById("gaugeBar");
const threatScoreVal = document.getElementById("threatScoreVal");
const metricLineVar = document.getElementById("metricLineVar");
const metricMaxGap = document.getElementById("metricMaxGap");
const metricDangerCtrl = document.getElementById("metricDangerCtrl");
const metricLeadTime = document.getElementById("metricLeadTime");
const causalRootName = document.getElementById("causalRootName");
const causalRootDesc = document.getElementById("causalRootDesc");
const coachDirectiveText = document.getElementById("coachDirectiveText");
const coachDrillText = document.getElementById("coachDrillText");

// DOM Elements - Counterfactual Engine Card
const cfModeBadge = document.getElementById("cfModeBadge");
const cfToggleBtn = document.getElementById("cfToggleBtn");
const loopRuptureBtn = document.getElementById("loopRuptureBtn");
const jumpInspectBtn = document.getElementById("jumpInspectBtn");
const openDossierBtn = document.getElementById("openDossierBtn");
const genAiBtn = document.getElementById("genAiBtn");
const tdActualGap = document.getElementById("tdActualGap");
const tdCfGap = document.getElementById("tdCfGap");
const tdActualDanger = document.getElementById("tdActualDanger");
const tdCfDanger = document.getElementById("tdCfDanger");
const tdActualLine = document.getElementById("tdActualLine");
const tdCfLine = document.getElementById("tdCfLine");
const tdActualAtt = document.getElementById("tdActualAtt");
const tdCfAtt = document.getElementById("tdCfAtt");

// DOM Elements - Lucid What-If Section
const whatifBadge = document.getElementById("whatifBadge");
const whatifSummary = document.getElementById("whatifSummary");
const whatifActual = document.getElementById("whatifActual");
const whatifCF = document.getElementById("whatifCF");

// DOM Elements - Dossier Modal
const dossierModal = document.getElementById("dossierModal");
const closeDossierBtn = document.getElementById("closeDossierBtn");
const dossierModalTitle = document.getElementById("dossierModalTitle");
const dossierModalSub = document.getElementById("dossierModalSub");
const modalExecSummary = document.getElementById("modalExecSummary");
const modalCascade1 = document.getElementById("modalCascade1");
const modalCascade2 = document.getElementById("modalCascade2");
const modalCascade3 = document.getElementById("modalCascade3");
const modalCascade4 = document.getElementById("modalCascade4");
const modalProofAction = document.getElementById("modalProofAction");
const modalProofChannel = document.getElementById("modalProofChannel");
const modalProofOffside = document.getElementById("modalProofOffside");
const modalProofThreat = document.getElementById("modalProofThreat");
const modalProofExplanation = document.getElementById("modalProofExplanation");
const modalCoachPlayer = document.getElementById("modalCoachPlayer");
const modalCoachUnit = document.getElementById("modalCoachUnit");
const modalCoachDrill = document.getElementById("modalCoachDrill");

// DOM Elements - Gemini Modal
const geminiModal = document.getElementById("geminiModal");
const closeGeminiModalBtn = document.getElementById("closeGeminiModalBtn");
const geminiApiKeyInput = document.getElementById("geminiApiKeyInput");
const geminiStatusMsg = document.getElementById("geminiStatusMsg");
const saveGeminiKeyBtn = document.getElementById("saveGeminiKeyBtn");
const clearGeminiKeyBtn = document.getElementById("clearGeminiKeyBtn");

// DOM Elements - Timeline Footer
const playBtn = document.getElementById("playBtn");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const frameSlider = document.getElementById("frameSlider");
const timeDisplay = document.getElementById("timeDisplay");
const dominoPin = document.getElementById("dominoPin");
const threatPin = document.getElementById("threatPin");

function toCanvasCoords(x, y) {
  return {
    px: x * PITCH_SCALE,
    py: (68.0 - y) * PITCH_SCALE
  };
}

// Initialize Application
async function init() {
  await loadEpisodesList();
  setupEventListeners();
  setupGeminiAuth();
  requestAnimationFrame(renderLoop);
}

// Check & Setup Gemini Key
function setupGeminiAuth() {
  const storedKey = localStorage.getItem("tempo_gemini_api_key");
  if (storedKey && storedKey.length > 10) {
    if (geminiConfigBtn) {
      geminiConfigBtn.classList.add("gemini-active");
      geminiConfigBtn.innerHTML = "✨ Gemini Active";
    }
    if (genAiBtn) {
      genAiBtn.innerHTML = "✨ AI Debrief";
    }
  } else {
    if (geminiConfigBtn) {
      geminiConfigBtn.classList.remove("gemini-active");
      geminiConfigBtn.innerHTML = "✨ Gemini AI";
    }
  }
}

// Fetch Catalog Manifest
async function loadEpisodesList() {
  try {
    const res = await fetch("/api/episodes");
    const data = await res.json();
    episodeSelect.innerHTML = "";
    data.episodes.forEach(ep => {
      const opt = document.createElement("option");
      opt.value = ep.id;
      opt.textContent = ep.label;
      episodeSelect.appendChild(opt);
    });

    if (data.episodes.length > 0) {
      const defaultEp = data.episodes.find(e => e.id.includes("ep_07")) || data.episodes[0];
      episodeSelect.value = defaultEp.id;
      await loadEpisode(defaultEp.id);
    }
  } catch (err) {
    console.error("Failed to load episodes manifest:", err);
  }
}

// Load Full Tracking Episode Package
async function loadEpisode(episodeId) {
  try {
    state.isPlaying = false;
    playBtn.textContent = "▶";
    const res = await fetch(`/api/episode/${episodeId}`);
    state.episode = await res.json();
    state.currentFrame = 0;
    state.ballTrail = [];
    setMode("actual", false);

    frameSlider.max = state.episode.total_frames - 1;
    frameSlider.value = 0;

    const dominoPct = (state.episode.domino_frame_idx / (state.episode.total_frames - 1)) * 100;
    const threatPct = (state.episode.threat_frame_idx / (state.episode.total_frames - 1)) * 100;

    dominoPin.style.display = "block";
    dominoPin.style.left = `${dominoPct}%`;
    threatPin.style.display = "block";
    threatPin.style.left = `${threatPct}%`;

    metricLeadTime.textContent = `${state.episode.lead_time_sec} s`;
    populateModalData();
    updateUI();
  } catch (err) {
    console.error("Failed to load episode:", err);
  }
}

// Populate Modal with Rich Tactical Dossier
function populateModalData() {
  if (!state.episode || !state.episode.cf_dossier) return;
  const ep = state.episode;
  const dos = ep.cf_dossier;

  if (dossierModalTitle) dossierModalTitle.textContent = dos.headline;
  const sourceLabel = (dos.source === "gemini-ai") ? " [✨ Powered by Google Gemini 2.5 Flash]" : "";
  if (dossierModalSub) dossierModalSub.textContent = `Match Sequence: ${ep.meta.label} | Causal Lead Window: ${ep.lead_time_sec}s${sourceLabel}`;
  if (modalExecSummary) modalExecSummary.textContent = dos.executive_summary;

  if (modalCascade1) modalCascade1.textContent = dos.actual_reality.trigger;
  if (modalCascade2) modalCascade2.textContent = dos.actual_reality.error_mechanism;
  if (modalCascade3) modalCascade3.textContent = `${ep.actual_gap_width_m}m corridor opened; offside trap broken.`;
  if (modalCascade4) modalCascade4.textContent = ep.meta.is_goal ? "Line-breaking pass converted into terminal goal." : "Shot conceded inside penalty area.";

  if (modalProofAction) modalProofAction.textContent = dos.counterfactual_simulation.action;
  const gapDiff = (ep.actual_gap_width_m - ep.cf_gap_width_m).toFixed(1);
  if (modalProofChannel) modalProofChannel.textContent = `${ep.actual_gap_width_m}m → ${ep.cf_gap_width_m}m (-${gapDiff}m)`;
  if (modalProofOffside) modalProofOffside.textContent = "Striker caught offside (Goal Prevented)";
  if (modalProofThreat) modalProofThreat.textContent = `-${ep.risk_reduction_pct}% Dangerous Space`;
  if (modalProofExplanation) modalProofExplanation.textContent = `${dos.counterfactual_simulation.channel_denial} ${dos.counterfactual_simulation.offside_trap} ${dos.counterfactual_simulation.pitch_control_impact}`;

  if (modalCoachPlayer) modalCoachPlayer.textContent = dos.coaching_directives.player_instruction;
  if (modalCoachUnit) modalCoachUnit.textContent = dos.coaching_directives.unit_coordination;
  if (modalCoachDrill) modalCoachDrill.textContent = dos.coaching_directives.training_drill;
}

// View Mode Switching
function setMode(newMode, autoJump = true) {
  state.mode = newMode;

  if (modeActualBtn) modeActualBtn.className = "mode-btn";
  if (modeCFBtn) modeCFBtn.className = "mode-btn";
  if (modeCompareBtn) modeCompareBtn.className = "mode-btn";

  if (newMode === "actual") {
    if (modeActualBtn) modeActualBtn.classList.add("active-actual");
    if (cfModeBadge) {
      cfModeBadge.textContent = "REALITY";
      cfModeBadge.style.background = "rgba(255, 71, 87, 0.2)";
      cfModeBadge.style.color = "#ff4757";
    }
    cfToggleBtn.innerHTML = "<span>🔀 Simulate Counterfactual (What-If)</span>";
    cfToggleBtn.classList.remove("active");
  } else if (newMode === "cf") {
    if (modeCFBtn) modeCFBtn.classList.add("active-cf");
    if (cfModeBadge) {
      cfModeBadge.textContent = "WHAT-IF ANCHOR";
      cfModeBadge.style.background = "rgba(29, 209, 161, 0.2)";
      cfModeBadge.style.color = "#1dd1a1";
    }
    cfToggleBtn.innerHTML = "<span>↺ Switch Back to Reality</span>";
    cfToggleBtn.classList.add("active");

    if (autoJump && state.episode) {
      if (state.currentFrame < state.episode.domino_frame_idx || state.currentFrame > state.episode.threat_frame_idx + 10) {
        state.currentFrame = state.episode.domino_frame_idx;
        frameSlider.value = state.currentFrame;
      }
    }
  } else if (newMode === "compare") {
    if (modeCompareBtn) modeCompareBtn.classList.add("active-compare");
    if (cfModeBadge) {
      cfModeBadge.textContent = "DUAL COMPARE";
      cfModeBadge.style.background = "rgba(254, 202, 87, 0.2)";
      cfModeBadge.style.color = "#feca57";
    }
    cfToggleBtn.innerHTML = "<span>⚡ Dual Compare Active</span>";

    if (autoJump && state.episode) {
      if (state.currentFrame < state.episode.domino_frame_idx || state.currentFrame > state.episode.threat_frame_idx + 10) {
        state.currentFrame = state.episode.domino_frame_idx;
        frameSlider.value = state.currentFrame;
      }
    }
  }

  updateUI();
}

// Setup Event Listeners
function setupEventListeners() {
  episodeSelect.addEventListener("change", (e) => loadEpisode(e.target.value));
  speedSelect.addEventListener("change", (e) => state.playbackSpeed = parseFloat(e.target.value));

  playBtn.addEventListener("click", togglePlay);
  prevBtn.addEventListener("click", () => stepFrame(-1));
  nextBtn.addEventListener("click", () => stepFrame(1));

  frameSlider.addEventListener("input", (e) => {
    state.currentFrame = parseInt(e.target.value);
    state.ballTrail = [];
    updateUI();
  });

  dominoPin.addEventListener("click", () => jumpToDomino());
  threatPin.addEventListener("click", () => jumpToThreat());

  if (jumpDominoBtn) jumpDominoBtn.addEventListener("click", () => jumpToDomino());
  if (jumpThreatBtn) jumpThreatBtn.addEventListener("click", () => jumpToThreat());
  if (jumpInspectBtn) jumpInspectBtn.addEventListener("click", () => jumpToDomino());

  // Full Dossier Modal Handlers
  if (openDossierBtn) {
    openDossierBtn.addEventListener("click", () => {
      if (dossierModal) {
        populateModalData();
        dossierModal.style.display = "flex";
      }
    });
  }

  if (closeDossierBtn) {
    closeDossierBtn.addEventListener("click", () => {
      if (dossierModal) dossierModal.style.display = "none";
    });
  }

  if (dossierModal) {
    dossierModal.addEventListener("click", (e) => {
      if (e.target === dossierModal) dossierModal.style.display = "none";
    });
  }

  // Gemini AI Modal Handlers
  if (geminiConfigBtn) {
    geminiConfigBtn.addEventListener("click", () => {
      if (geminiModal) {
        const storedKey = localStorage.getItem("tempo_gemini_api_key") || "";
        geminiApiKeyInput.value = storedKey;
        geminiStatusMsg.textContent = storedKey ? "Active API Key Configured" : "No API key currently set. Enter your key to activate Gemini.";
        geminiStatusMsg.style.color = storedKey ? "#1dd1a1" : "var(--text-muted)";
        geminiModal.style.display = "flex";
      }
    });
  }

  if (closeGeminiModalBtn) {
    closeGeminiModalBtn.addEventListener("click", () => {
      if (geminiModal) geminiModal.style.display = "none";
    });
  }

  if (geminiModal) {
    geminiModal.addEventListener("click", (e) => {
      if (e.target === geminiModal) geminiModal.style.display = "none";
    });
  }

  if (saveGeminiKeyBtn) {
    saveGeminiKeyBtn.addEventListener("click", async () => {
      const key = geminiApiKeyInput.value.trim();
      if (key) {
        localStorage.setItem("tempo_gemini_api_key", key);
        setupGeminiAuth();
        geminiStatusMsg.textContent = "API Key Saved! Generating tactical briefing with Gemini...";
        geminiStatusMsg.style.color = "#1dd1a1";
        await triggerGeminiGeneration(key);
        setTimeout(() => {
          if (geminiModal) geminiModal.style.display = "none";
        }, 1000);
      }
    });
  }

  if (clearGeminiKeyBtn) {
    clearGeminiKeyBtn.addEventListener("click", () => {
      localStorage.removeItem("tempo_gemini_api_key");
      geminiApiKeyInput.value = "";
      setupGeminiAuth();
      geminiStatusMsg.textContent = "API key cleared. Engine reverted to default rule heuristics.";
      geminiStatusMsg.style.color = "#ff6b6b";
    });
  }

  // Trigger Gemini AI Debrief
  if (genAiBtn) {
    genAiBtn.addEventListener("click", async () => {
      const storedKey = localStorage.getItem("tempo_gemini_api_key");
      if (!storedKey || storedKey.length < 10) {
        if (geminiModal) {
          geminiApiKeyInput.value = "";
          geminiStatusMsg.textContent = "Please enter your Gemini API Key to activate AI debriefs.";
          geminiStatusMsg.style.color = "#feca57";
          geminiModal.style.display = "flex";
        }
      } else {
        await triggerGeminiGeneration(storedKey);
      }
    });
  }

  if (loopRuptureBtn) {
    loopRuptureBtn.addEventListener("click", () => {
      state.isLoopingRupture = !state.isLoopingRupture;
      loopRuptureBtn.classList.toggle("loop-active", state.isLoopingRupture);
      if (state.isLoopingRupture) {
        state.currentFrame = state.episode ? state.episode.domino_frame_idx : 0;
        frameSlider.value = state.currentFrame;
        state.isPlaying = true;
        playBtn.textContent = "⏸";
      }
    });
  }

  if (modeActualBtn) modeActualBtn.addEventListener("click", () => setMode("actual"));
  if (modeCFBtn) modeCFBtn.addEventListener("click", () => setMode("cf"));
  if (modeCompareBtn) modeCompareBtn.addEventListener("click", () => setMode("compare"));

  cfToggleBtn.addEventListener("click", () => {
    if (state.mode === "actual") {
      setMode("cf");
    } else {
      setMode("actual");
    }
  });

  if (toggleFocusBtn) {
    toggleFocusBtn.addEventListener("click", () => {
      state.focusMode = !state.focusMode;
      toggleFocusBtn.classList.toggle("active", state.focusMode);
    });
  }

  toggleHullBtn.addEventListener("click", () => {
    state.showHull = !state.showHull;
    toggleHullBtn.classList.toggle("active", state.showHull);
  });

  toggleHeatmapBtn.addEventListener("click", () => {
    state.showHeatmap = !state.showHeatmap;
    toggleHeatmapBtn.classList.toggle("active", state.showHeatmap);
  });

  window.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
      e.preventDefault();
      togglePlay();
    } else if (e.code === "ArrowLeft") {
      stepFrame(-1);
    } else if (e.code === "ArrowRight") {
      stepFrame(1);
    } else if (e.code === "KeyC") {
      setMode(state.mode === "actual" ? "cf" : "actual");
    } else if (e.code === "KeyF") {
      state.focusMode = !state.focusMode;
      if (toggleFocusBtn) toggleFocusBtn.classList.toggle("active", state.focusMode);
    } else if (e.code === "Escape") {
      if (dossierModal) dossierModal.style.display = "none";
      if (geminiModal) geminiModal.style.display = "none";
    }
  });
}

// Trigger Gemini AI Generation via Backend
async function triggerGeminiGeneration(apiKey) {
  if (!state.episode) return;
  const originalText = genAiBtn ? genAiBtn.innerHTML : "";
  if (genAiBtn) genAiBtn.innerHTML = "⏳ Generating...";

  try {
    const res = await fetch(`/api/generate_ai_dossier/${state.episode.meta.id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey })
    });
    const data = await res.json();
    if (data.status === "success" && data.dossier) {
      state.episode.cf_dossier = data.dossier;
      populateModalData();
      updateUI();
      if (genAiBtn) {
        genAiBtn.innerHTML = (data.source === "gemini-ai") ? "✨ AI Generated!" : "✨ Heuristic Active";
        setTimeout(() => { if (genAiBtn) genAiBtn.innerHTML = "✨ AI Debrief"; }, 3000);
      }
    }
  } catch (err) {
    console.error("Gemini generation failed:", err);
    if (genAiBtn) genAiBtn.innerHTML = "❌ Generation Error";
    setTimeout(() => { if (genAiBtn) genAiBtn.innerHTML = originalText; }, 2500);
  }
}

function jumpToDomino() {
  if (!state.episode) return;
  state.currentFrame = state.episode.domino_frame_idx;
  frameSlider.value = state.currentFrame;
  state.ballTrail = [];
  updateUI();
}

function jumpToThreat() {
  if (!state.episode) return;
  state.currentFrame = state.episode.threat_frame_idx;
  frameSlider.value = state.currentFrame;
  state.ballTrail = [];
  updateUI();
}

function togglePlay() {
  state.isPlaying = !state.isPlaying;
  playBtn.textContent = state.isPlaying ? "⏸" : "▶";
}

function stepFrame(delta) {
  if (!state.episode) return;
  state.currentFrame = Math.max(0, Math.min(state.episode.total_frames - 1, state.currentFrame + delta));
  frameSlider.value = state.currentFrame;
  updateUI();
}

// 60 FPS Animation Render Loop
function renderLoop(timestamp) {
  if (!state.lastTimestamp) state.lastTimestamp = timestamp;
  const dt = (timestamp - state.lastTimestamp) / 1000.0;
  state.lastTimestamp = timestamp;

  state.pulsePhase += dt * 3.5;

  if (state.isPlaying && state.episode) {
    state.frameAccumulator += dt * state.episode.fps * state.playbackSpeed;
    if (state.frameAccumulator >= 1.0) {
      const framesToAdvance = Math.floor(state.frameAccumulator);
      state.frameAccumulator -= framesToAdvance;
      state.currentFrame += framesToAdvance;

      if (state.isLoopingRupture) {
        const loopEnd = Math.min(state.episode.total_frames - 1, state.episode.threat_frame_idx + 6);
        if (state.currentFrame >= loopEnd) {
          state.currentFrame = state.episode.domino_frame_idx;
          state.ballTrail = [];
        }
      } else {
        if (state.currentFrame >= state.episode.total_frames - 1) {
          state.currentFrame = state.episode.total_frames - 1;
          state.isPlaying = false;
          playBtn.textContent = "▶";
        }
      }

      frameSlider.value = state.currentFrame;
      updateUI();
    }
  }

  drawScene();
  requestAnimationFrame(renderLoop);
}

// Clean Tactical Pitch Drawing Engine
function drawScene() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Pitch Grass
  ctx.fillStyle = "#111f18";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Pitch Grass Subtle Alternating Stripes
  ctx.fillStyle = "rgba(255, 255, 255, 0.015)";
  const stripeWidth = canvas.width / 10;
  for (let i = 0; i < 10; i += 2) {
    ctx.fillRect(i * stripeWidth, 0, stripeWidth, canvas.height);
  }

  drawPitchMarkings();

  if (!state.episode) return;

  const f = state.currentFrame;
  const ep = state.episode;

  const isHomeAtt = (ep.attacking_team === "Home");
  const attCoords = isHomeAtt ? ep.home_coords[f] : ep.away_coords[f];
  const attJerseys = isHomeAtt ? ep.home_jerseys : ep.away_jerseys;
  const defCoordsActual = isHomeAtt ? ep.away_coords[f] : ep.home_coords[f];
  const defCoordsCF = ep.cf_def_coords[f];
  const defJerseys = isHomeAtt ? ep.away_jerseys : ep.home_jerseys;

  const isRuptureActive = (f >= ep.domino_frame_idx);
  const activeDefCoords = (state.mode === "cf") ? defCoordsCF : defCoordsActual;

  // Track Ball Trail
  if (ep.ball_coords[f]) {
    const b = ep.ball_coords[f];
    if (b && !isNaN(b[0])) {
      state.ballTrail.push(toCanvasCoords(b[0], b[1]));
      if (state.ballTrail.length > 7) state.ballTrail.shift();
    }
  }

  // 1. Optional Pitch Control Heatmap
  if (state.showHeatmap) {
    drawSubtlePPCF(attCoords, activeDefCoords, state.mode === "cf");
  }

  // 2. Optional Convex Hull
  if (state.showHull && activeDefCoords) {
    drawSubtleHull(activeDefCoords, state.mode === "cf");
  }

  // 3. Identify Key Actors for Spotlight Focus
  const causalIdx = ep.causal_defender_idx;
  const backlineSet = new Set(ep.backline_indices || []);
  
  let keyAttIdx = -1;
  if (attCoords && defCoordsActual[causalIdx]) {
    const cPt = defCoordsActual[causalIdx];
    let minDist = 999.0;
    attCoords.forEach((pt, i) => {
      if (pt) {
        const d = Math.hypot(pt[0] - cPt[0], pt[1] - cPt[1]);
        if (d < minDist) {
          minDist = d;
          keyAttIdx = i;
        }
      }
    });
  }

  // 4. Draw Backline Structure & Gap Dimension
  if (ep.backline_indices && defCoordsActual && defCoordsCF) {
    drawCleanBackline(defCoordsActual, defCoordsCF, ep.backline_indices, causalIdx, isRuptureActive);
  }

  // 5. Draw Attacking Players
  if (attCoords) {
    attCoords.forEach((pt, i) => {
      if (pt) {
        const isKey = (i === keyAttIdx);
        const opacity = state.focusMode ? (isKey ? 1.0 : 0.28) : 1.0;
        const radius = isKey ? 10 : 7;
        const color = isKey ? "#00f0ff" : `rgba(0, 210, 211, ${opacity})`;
        const showLabel = isKey || !state.focusMode;
        drawCleanPlayer(pt[0], pt[1], attJerseys[i] || `${i + 1}`, color, "#000", radius, opacity, showLabel);
      }
    });
  }

  // 6. Draw Defending Players
  if (activeDefCoords) {
    activeDefCoords.forEach((pt, i) => {
      if (pt) {
        const isCausal = (i === causalIdx);
        const isBackline = backlineSet.has(i);
        const isKey = isCausal || isBackline;

        const opacity = state.focusMode ? (isKey ? 1.0 : 0.25) : 1.0;
        const radius = isCausal ? 11 : (isBackline ? 9 : 7);

        let color = `rgba(255, 107, 107, ${opacity})`;
        if (isCausal && isRuptureActive) {
          color = (state.mode === "cf") ? "#1dd1a1" : "#ff4757";
        }

        const showLabel = isKey || !state.focusMode;
        drawCleanPlayer(pt[0], pt[1], defJerseys[i] || `${i + 1}`, color, "#fff", radius, opacity, showLabel);

        if (isCausal && isRuptureActive) {
          drawSpotlightRing(pt[0], pt[1], state.mode === "cf" ? "#1dd1a1" : "#ff4757");
        }
      }
    });
  }

  // 7. Counterfactual Ghost & Comparison Indicators
  if (isRuptureActive && defCoordsActual && defCoordsCF) {
    const actPt = defCoordsActual[causalIdx];
    const cfPt = defCoordsCF[causalIdx];

    if (actPt && cfPt) {
      if (state.mode === "cf") {
        drawMinimalGhost(actPt, cfPt, ep.causal_defender_jersey);
      } else if (state.mode === "compare") {
        drawMinimalCompare(actPt, cfPt, ep.causal_defender_jersey);
      }
    }
  }

  // 8. Draw Ball & Trajectory Trail
  if (state.ballTrail.length > 1) {
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(state.ballTrail[0].px, state.ballTrail[0].py);
    for (let i = 1; i < state.ballTrail.length; i++) {
      ctx.lineTo(state.ballTrail[i].px, state.ballTrail[i].py);
    }
    ctx.strokeStyle = "rgba(255, 250, 101, 0.35)";
    ctx.lineWidth = 2.0;
    ctx.stroke();
    ctx.restore();
  }

  if (ep.ball_coords[f]) {
    const b = ep.ball_coords[f];
    if (b && !isNaN(b[0])) {
      const c = toCanvasCoords(b[0], b[1]);
      ctx.beginPath();
      ctx.arc(c.px, c.py, 6, 0, Math.PI * 2);
      ctx.fillStyle = "#fffa65";
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = "#000";
      ctx.stroke();
    }
  }
}

// Clean Minimalist Backline & Channel Gap
function drawCleanBackline(defCoordsActual, defCoordsCF, backlineIndices, causalIdx, isRuptureActive) {
  const coords = (state.mode === "cf") ? defCoordsCF : defCoordsActual;
  const pts = backlineIndices
    .map(idx => ({ idx, pt: coords[idx] }))
    .filter(item => item.pt && !isNaN(item.pt[0]))
    .sort((a, b) => a.pt[1] - b.pt[1]);

  if (pts.length < 2) return;

  const canvasPts = pts.map(item => ({ ...toCanvasCoords(item.pt[0], item.pt[1]), idx: item.idx }));

  ctx.save();
  ctx.beginPath();
  ctx.moveTo(canvasPts[0].px, canvasPts[0].py);
  for (let i = 1; i < canvasPts.length; i++) {
    ctx.lineTo(canvasPts[i].px, canvasPts[i].py);
  }

  if (state.mode === "cf") {
    ctx.strokeStyle = "#1dd1a1";
    ctx.lineWidth = 2.5;
    ctx.stroke();

    ctx.strokeStyle = "rgba(29, 209, 161, 0.3)";
    ctx.lineWidth = 6.0;
    ctx.stroke();
  } else if (isRuptureActive) {
    ctx.strokeStyle = "rgba(255, 71, 87, 0.85)";
    ctx.lineWidth = 2.0;
    ctx.setLineDash([5, 4]);
    ctx.stroke();
  } else {
    ctx.strokeStyle = "rgba(255, 255, 255, 0.35)";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([3, 3]);
    ctx.stroke();
  }
  ctx.restore();

  if (isRuptureActive) {
    const causalItem = pts.find(item => item.idx === causalIdx);
    if (causalItem) {
      const neighbors = pts.filter(item => item.idx !== causalIdx);
      neighbors.sort((a, b) => Math.abs(a.pt[1] - causalItem.pt[1]) - Math.abs(b.pt[1] - causalItem.pt[1]));
      const nbr = neighbors[0];
      if (nbr) {
        const c1 = toCanvasCoords(causalItem.pt[0], causalItem.pt[1]);
        const c2 = toCanvasCoords(nbr.pt[0], nbr.pt[1]);
        const midX = (c1.px + c2.px) / 2;
        const midY = (c1.py + c2.py) / 2;

        ctx.save();
        ctx.fillStyle = (state.mode === "cf") ? "#1dd1a1" : "#ff4757";
        ctx.font = "bold 10px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        const text = (state.mode === "cf") ? `🛡️ ${state.episode.cf_gap_width_m}m Sealed` : `⚡ ${state.episode.actual_gap_width_m}m Gap`;
        ctx.fillText(text, midX + 15, midY);
        ctx.restore();
      }
    }
  }
}

// Spotlight Pulse Ring around Causal Actor
function drawSpotlightRing(x, y, color) {
  const c = toCanvasCoords(x, y);
  const pulseR = 15 + Math.sin(state.pulsePhase) * 3;

  ctx.save();
  ctx.beginPath();
  ctx.arc(c.px, c.py, pulseR, 0, Math.PI * 2);
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.8;
  ctx.setLineDash([3, 3]);
  ctx.stroke();
  ctx.restore();
}

// Clean Minimal Ghost Marker in Counterfactual Mode
function drawMinimalGhost(actPt, cfPt, jersey) {
  const cAct = toCanvasCoords(actPt[0], actPt[1]);
  const cCf = toCanvasCoords(cfPt[0], cfPt[1]);

  ctx.save();
  ctx.beginPath();
  ctx.moveTo(cAct.px, cAct.py);
  ctx.lineTo(cCf.px, cCf.py);
  ctx.strokeStyle = "rgba(29, 209, 161, 0.7)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([3, 3]);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(cAct.px, cAct.py, 10, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(255, 71, 87, 0.6)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([2, 2]);
  ctx.stroke();

  const dist = Math.hypot(actPt[0] - cfPt[0], actPt[1] - cfPt[1]);
  ctx.fillStyle = "#ff6b6b";
  ctx.font = "bold 9px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(`-${dist.toFixed(1)}m Drift`, cAct.px, cAct.py - 14);
  ctx.restore();
}

// Minimal Dual Compare
function drawMinimalCompare(actPt, cfPt, jersey) {
  const cAct = toCanvasCoords(actPt[0], actPt[1]);
  const cCf = toCanvasCoords(cfPt[0], cfPt[1]);

  ctx.save();
  ctx.beginPath();
  ctx.moveTo(cAct.px, cAct.py);
  ctx.lineTo(cCf.px, cCf.py);
  ctx.strokeStyle = "#feca57";
  ctx.lineWidth = 1.5;
  ctx.stroke();

  const midX = (cAct.px + cCf.px) / 2;
  const midY = (cAct.py + cCf.py) / 2;
  const dist = Math.hypot(actPt[0] - cfPt[0], actPt[1] - cfPt[1]);

  ctx.fillStyle = "#feca57";
  ctx.font = "bold 9px monospace";
  ctx.textAlign = "center";
  ctx.fillText(`Δ ${dist.toFixed(1)}m`, midX, midY - 6);

  ctx.beginPath();
  ctx.arc(cAct.px, cAct.py, 8, 0, Math.PI * 2);
  ctx.fillStyle = "#ff4757";
  ctx.fill();

  ctx.beginPath();
  ctx.arc(cCf.px, cCf.py, 8, 0, Math.PI * 2);
  ctx.fillStyle = "#1dd1a1";
  ctx.fill();

  ctx.restore();
}

// Clean Player Token
function drawCleanPlayer(x, y, jersey, color, textColor, radius = 8, opacity = 1.0, showLabel = true) {
  const c = toCanvasCoords(x, y);

  ctx.save();
  ctx.globalAlpha = opacity;

  ctx.beginPath();
  ctx.arc(c.px, c.py, radius, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.lineWidth = 1.0;
  ctx.strokeStyle = "rgba(255, 255, 255, 0.8)";
  ctx.stroke();

  if (showLabel && radius >= 8) {
    ctx.fillStyle = textColor;
    ctx.font = "bold 8px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(jersey, c.px, c.py);
  }

  ctx.restore();
}

// Subtle PPCF
function drawSubtlePPCF(attCoords, defCoords, isCF) {
  if (!attCoords || !defCoords) return;

  const cols = 20;
  const rows = 13;
  const cellW = canvas.width / cols;
  const cellH = canvas.height / rows;

  ctx.save();
  for (let i = 0; i < cols; i++) {
    const px = (i + 0.5) * cellW;
    const pitchX = px / PITCH_SCALE;

    for (let j = 0; j < rows; j++) {
      const py = (j + 0.5) * cellH;
      const pitchY = 68.0 - (py / PITCH_SCALE);

      let minAtt = 999.0;
      let minDef = 999.0;

      for (const p of attCoords) {
        if (p) {
          const d = Math.hypot(p[0] - pitchX, p[1] - pitchY);
          if (d < minAtt) minAtt = d;
        }
      }
      for (const p of defCoords) {
        if (p) {
          const d = Math.hypot(p[0] - pitchX, p[1] - pitchY);
          if (d < minDef) minDef = d;
        }
      }

      const diff = minDef - minAtt;
      const ppcf = 1.0 / (1.0 + Math.exp(-0.35 * diff));

      if (ppcf > 0.6) {
        ctx.fillStyle = "rgba(0, 210, 211, 0.12)";
        ctx.fillRect(i * cellW, j * cellH, cellW, cellH);
      } else if (ppcf < 0.4) {
        ctx.fillStyle = isCF ? "rgba(29, 209, 161, 0.12)" : "rgba(255, 107, 107, 0.10)";
        ctx.fillRect(i * cellW, j * cellH, cellW, cellH);
      }
    }
  }
  ctx.restore();
}

// Subtle Hull
function drawSubtleHull(coords, isCF) {
  const validPts = coords.filter(p => p && !isNaN(p[0])).map(p => toCanvasCoords(p[0], p[1]));
  if (validPts.length < 3) return;

  const hull = computeConvexHull(validPts);
  if (hull.length < 3) return;

  ctx.save();
  ctx.beginPath();
  ctx.moveTo(hull[0].px, hull[0].py);
  for (let i = 1; i < hull.length; i++) {
    ctx.lineTo(hull[i].px, hull[i].py);
  }
  ctx.closePath();

  ctx.strokeStyle = isCF ? "rgba(29, 209, 161, 0.4)" : "rgba(255, 107, 107, 0.35)";
  ctx.lineWidth = 1.2;
  ctx.stroke();
  ctx.restore();
}

function computeConvexHull(pts) {
  pts.sort((a, b) => a.px === b.px ? a.py - b.py : a.px - b.px);
  const cross = (o, a, b) => (a.px - o.px) * (b.py - o.py) - (a.py - o.py) * (b.px - o.px);

  const lower = [];
  for (const p of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
      lower.pop();
    }
    lower.push(p);
  }

  const upper = [];
  for (let i = pts.length - 1; i >= 0; i--) {
    const p = pts[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
      upper.pop();
    }
    upper.push(p);
  }

  upper.pop();
  lower.pop();
  return lower.concat(upper);
}

// FIFA Markings
function drawPitchMarkings() {
  ctx.strokeStyle = "rgba(255, 255, 255, 0.35)";
  ctx.lineWidth = 1.5;

  ctx.strokeRect(0, 0, canvas.width, canvas.height);

  ctx.beginPath();
  ctx.moveTo(canvas.width / 2, 0);
  ctx.lineTo(canvas.width / 2, canvas.height);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(canvas.width / 2, canvas.height / 2, 91.5, 0, Math.PI * 2);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(canvas.width / 2, canvas.height / 2, 3.5, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
  ctx.fill();

  const penHeight = 40.32 * PITCH_SCALE;
  const penTop = (canvas.height - penHeight) / 2;
  ctx.strokeRect(0, penTop, 165, penHeight);
  ctx.strokeRect(canvas.width - 165, penTop, 165, penHeight);

  const sixHeight = 18.32 * PITCH_SCALE;
  const sixTop = (canvas.height - sixHeight) / 2;
  ctx.strokeRect(0, sixTop, 55, sixHeight);
  ctx.strokeRect(canvas.width - 55, sixTop, 55, sixHeight);

  ctx.beginPath();
  ctx.arc(110, canvas.height / 2, 3, 0, Math.PI * 2);
  ctx.arc(canvas.width - 110, canvas.height / 2, 3, 0, Math.PI * 2);
  ctx.fill();
}

// Update UI, Sidebar & Lucid What-If Dossier
function updateUI() {
  if (!state.episode) return;

  const f = state.currentFrame;
  const ep = state.episode;
  const dos = ep.cf_dossier;

  const timeSec = ep.times_sec[f] || 0.0;
  const mins = Math.floor(timeSec / 60);
  const secs = (timeSec % 60).toFixed(2);
  timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.padStart(5, '0')}`;

  const rawScore = ep.structural_scores[f] || 0.1;
  const pct = Math.min(100, Math.max(10, Math.round(rawScore * 80)));
  gaugeBar.style.width = `${pct}%`;
  threatScoreVal.textContent = rawScore.toFixed(2);

  const isRupture = (f >= ep.domino_frame_idx);

  // Floating Narrative Banner
  if (tacticalBanner) {
    tacticalBanner.className = "tactical-banner";
    if (state.mode === "cf") {
      tacticalBanner.classList.add("banner-cf");
      bannerIcon.textContent = "🛡️";
      bannerText.textContent = `COUNTERFACTUAL WHAT-IF: Defender #${ep.causal_defender_jersey} held 18m line → Passing channel sealed (-${ep.risk_reduction_pct}% threat)`;
    } else if (state.mode === "compare") {
      tacticalBanner.classList.add("banner-compare");
      bannerIcon.textContent = "⚡";
      bannerText.textContent = `DUAL OVERLAY: Actual error (Red) vs Counterfactual anchor (Green) | ${ep.actual_gap_width_m}m vs ${ep.cf_gap_width_m}m gap`;
    } else {
      tacticalBanner.classList.add("banner-actual");
      if (isRupture) {
        bannerIcon.textContent = "⚠️";
        bannerText.textContent = `ACTUAL MATCH REALITY: Defender #${ep.causal_defender_jersey} drifted out of line → ${ep.actual_gap_width_m}m corridor opened`;
      } else {
        bannerIcon.textContent = "🟢";
        bannerText.textContent = "DEFENSIVE FORMATION COHERENT: Scanning match sequence for structural rupture point...";
      }
    }
  }

  // Sidebar Metrics Cards
  if (state.mode === "cf") {
    threatBadge.className = "status-badge status-safe";
    threatBadge.textContent = "DEFENSE ANCHORED";
    metricLineVar.textContent = "1.2 m (Disciplined)";
    metricMaxGap.textContent = `${ep.cf_gap_width_m} m (Sealed)`;
    metricDangerCtrl.textContent = `${Math.round(ep.cf_danger_scores[f] || 110)} m²`;
  } else {
    if (f >= ep.threat_frame_idx) {
      threatBadge.className = "status-badge status-collapse";
      threatBadge.textContent = "TERMINAL SHOT";
    } else if (f >= ep.domino_frame_idx) {
      threatBadge.className = "status-badge status-warning";
      threatBadge.textContent = "DOMINO RUPTURE";
    } else {
      threatBadge.className = "status-badge status-safe";
      threatBadge.textContent = "STABLE";
    }

    metricLineVar.textContent = (rawScore * 2.8).toFixed(1) + " m";
    metricMaxGap.textContent = (isRupture ? ep.actual_gap_width_m : 4.8).toFixed(1) + " m";
    metricDangerCtrl.textContent = `${Math.round(ep.actual_danger_scores[f] || 180)} m²`;
  }

  // Sidebar Comparison Table
  if (tdActualGap) tdActualGap.textContent = `${ep.actual_gap_width_m} m`;
  if (tdCfGap) tdCfGap.textContent = `${ep.cf_gap_width_m} m (Sealed)`;
  if (tdActualDanger) tdActualDanger.textContent = `${Math.round(ep.actual_danger_scores[f] || 180)} m²`;
  if (tdCfDanger) tdCfDanger.textContent = `${Math.round(ep.cf_danger_scores[f] || 128)} m² (-${ep.risk_reduction_pct}%)`;
  if (tdActualLine) tdActualLine.textContent = isRupture ? "⚡ Ruptured" : "Stable";
  if (tdCfLine) tdCfLine.textContent = isRupture ? "🛡️ Laser Intact" : "Stable";
  if (tdActualAtt) tdActualAtt.textContent = (f >= ep.threat_frame_idx) ? "⚽ Shot Conceded" : "Onside Run";
  if (tdCfAtt) tdCfAtt.textContent = isRupture ? "🚩 Flagged Offside" : "Contained";

  // Rich What-If Narrative Box in Sidebar
  if (dos) {
    if (whatifBadge) {
      if (dos.source === "gemini-ai") {
        whatifBadge.textContent = "✨ Gemini 2.5 Flash";
        whatifBadge.className = "whatif-pill ai-source-badge";
      } else {
        whatifBadge.textContent = `t - ${ep.lead_time_sec}s Window`;
        whatifBadge.className = "whatif-pill";
      }
    }
    if (whatifSummary) whatifSummary.textContent = dos.executive_summary;
    if (whatifActual) whatifActual.textContent = `${dos.actual_reality.error_mechanism}. ${dos.actual_reality.tactical_cost}`;
    if (whatifCF) whatifCF.textContent = `${dos.counterfactual_simulation.action} Result: ${dos.counterfactual_simulation.channel_denial} ${dos.counterfactual_simulation.offside_trap}`;
    if (coachDirectiveText) coachDirectiveText.textContent = dos.coaching_directives.player_instruction;
    if (coachDrillText) coachDrillText.textContent = dos.coaching_directives.training_drill;
  }

  // Causal Root Box
  if (isRupture) {
    if (state.mode === "cf") {
      causalRootName.textContent = `Defender #${ep.causal_defender_jersey} [COUNTERFACTUAL ANCHOR]`;
      causalRootDesc.innerHTML = `<strong style="color:#1dd1a1">Intervention Validated:</strong> Maintained zonal offside plane. Passing corridor closed (-${ep.risk_reduction_pct}% threat).`;
    } else {
      causalRootName.textContent = `Defender #${ep.causal_defender_jersey} [CAUSAL BREAKDOWN]`;
      causalRootDesc.textContent = ep.causal_error_desc;
    }
  } else {
    causalRootName.textContent = "Formation Coherent";
    causalRootDesc.textContent = `Scanning ${ep.total_frames} frames for structural breakdown...`;
  }
}

// Boot Studio
init();
