#!/usr/bin/env python3
"""
Semantic Plagiarism Detection Agent — Premium Web UI
Microsoft Codeathon · Problem Statement 5

Run:  python web_app.py
Then open: http://127.0.0.1:7860
"""

from __future__ import annotations
import json
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import numpy as np

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Local imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from detector import SemanticPlagiarismDetector
from sample_data import ORIGINAL, PARAPHRASED, DIFFERENT, LIGHTLY_EDITED

# ---------------------------------------------------------------------------
# Global detector (reused for speed)
# ---------------------------------------------------------------------------
DETECTOR = SemanticPlagiarismDetector(
    similarity_threshold=0.42,
    paraphrase_threshold=0.62,
    min_section_words=10,
)

# ---------------------------------------------------------------------------
# HTML UI (Immersive Textures, Glassmorphism, Cinematic Transitions)
# ---------------------------------------------------------------------------
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Semantic Plagiarism Detector</title>
<style>
  :root {
    --apple-ease: cubic-bezier(0.25, 1, 0.3, 1);
    --bounce-ease: cubic-bezier(0.34, 1.56, 0.64, 1);
    
    /* Light Mode Defaults */
    --bg-color: #fbfbfd;
    --text-main: #1d1d1f;
    --text-sec: #86868b;
    --glass-bg: rgba(255, 255, 255, 0.55);
    --glass-border: rgba(255, 255, 255, 0.8);
    --glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
    --mesh-opacity: 0.45;
    --input-bg: rgba(255, 255, 255, 0.4);
    --accent: #0071e3;
    --danger: #ff3b30;
    --warning: #ff9500;
    --success: #34c759;
  }
  
  :root.dark {
    --bg-color: #000000;
    --text-main: #f5f5f7;
    --text-sec: #a1a1aa;
    --glass-bg: rgba(28, 28, 30, 0.55);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    --mesh-opacity: 0.15;
    --input-bg: rgba(0, 0, 0, 0.3);
    --accent: #2997ff;
  }
  
  * { box-sizing: border-box; margin: 0; padding: 0; }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, sans-serif;
    color: var(--text-main);
    min-height: 100vh;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
    background: var(--bg-color);
    transition: background-color 0.6s var(--apple-ease), color 0.6s var(--apple-ease);
  }

  /* Animated Mesh Gradient Background */
  .bg-mesh {
    position: fixed; top: -50%; left: -50%; right: -50%; bottom: -50%;
    width: 200%; height: 200%;
    background: 
      radial-gradient(circle at 50% 50%, rgba(255, 182, 255, 1) 0%, transparent 40%),
      radial-gradient(circle at 80% 20%, rgba(182, 227, 255, 1) 0%, transparent 40%),
      radial-gradient(circle at 20% 80%, rgba(255, 219, 182, 1) 0%, transparent 40%);
    opacity: var(--mesh-opacity);
    animation: meshFlow 20s infinite alternate linear;
    z-index: -2;
    transition: opacity 0.6s var(--apple-ease);
  }
  @keyframes meshFlow {
    0% { transform: rotate(0deg) scale(1); }
    100% { transform: rotate(20deg) scale(1.2); }
  }

  /* Top Navigation */
  .navbar {
    position: fixed; top: 0; width: 100%; padding: 1.2rem 2.5rem;
    display: flex; justify-content: space-between; align-items: center;
    z-index: 100;
  }
  .nav-logo {
    font-weight: 800; font-size: 1.4rem; letter-spacing: -0.04em;
    color: var(--text-main); transition: color 0.6s;
    background: linear-gradient(135deg, var(--text-main), var(--text-sec));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  
  /* iOS Style Theme Toggle */
  .theme-switch-wrapper { display: flex; align-items: center; gap: 12px; }
  .theme-icon { color: var(--text-sec); transition: color 0.4s; }
  .theme-switch { position: relative; display: inline-block; width: 56px; height: 32px; }
  .theme-switch input { opacity: 0; width: 0; height: 0; }
  .slider {
    position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(0,0,0,0.08); backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border); border-radius: 34px;
    transition: background-color 0.4s, border-color 0.6s;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
  }
  .slider:before {
    position: absolute; content: ""; height: 24px; width: 24px; left: 3px; bottom: 3px;
    background-color: white; border-radius: 50%;
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), background-color 0.6s;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  }
  input:checked + .slider { background-color: var(--accent); border-color: var(--accent); }
  input:checked + .slider:before { transform: translateX(24px); }
  .dark .slider { background-color: rgba(255,255,255,0.1); }
  .dark input:checked + .slider { background-color: var(--accent); }
  .dark .slider:before { background-color: #e5e5ea; }
  .dark input:checked + .slider:before { background-color: #ffffff; }

  /* Typography */
  h1 { 
    font-size: 3.5rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 0.5rem; text-align: center; 
    background: linear-gradient(180deg, var(--text-main) 0%, var(--text-sec) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  p.subtitle { font-size: 1.1rem; color: var(--text-sec); text-align: center; margin-bottom: 3rem; transition: color 0.6s; }

  /* Layout */
  .container { max-width: 1100px; margin: 0 auto; padding: 7rem 2rem 4rem; display: flex; flex-direction: column; align-items: center; }
  
  /* Cinematic Transition Container */
  .input-section { width: 100%; transition: all 0.8s var(--apple-ease); transform-origin: center top; }
  .input-section.hidden { opacity: 0; transform: scale(0.9) translateY(-20px); filter: blur(10px); pointer-events: none; position: absolute; }

  /* Glassmorphism Cards with Immersive Noise Texture */
  .glass {
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(30px) saturate(200%); -webkit-backdrop-filter: blur(30px) saturate(200%);
    border: 1px solid var(--glass-border); border-radius: 20px; box-shadow: var(--glass-shadow);
    transition: background 0.6s, border-color 0.6s, box-shadow 0.6s;
    overflow: hidden;
  }
  /* Grain Texture Overlay */
  .glass::before {
    content: ""; position: absolute; inset: 0; border-radius: inherit;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 0;
  }
  /* Ensure content sits above the noise */
  .glass > * { position: relative; z-index: 1; }

  .editor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; width: 100%; margin-bottom: 2.5rem; }
  @media (max-width: 800px) { .editor-grid { grid-template-columns: 1fr; } }
  
  .editor-card {
    padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;
    transition: transform 0.4s var(--apple-ease), box-shadow 0.4s var(--apple-ease), background 0.6s, border 0.6s;
  }
  .editor-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(0,0,0,0.15); }
  
  .card-header { display: flex; justify-content: space-between; align-items: center; padding: 0 0.25rem; }
  .card-title { font-size: 0.95rem; font-weight: 700; letter-spacing: -0.02em; color: var(--text-main); transition: color 0.6s; }
  .word-count { font-size: 0.8rem; color: var(--text-sec); font-variant-numeric: tabular-nums; transition: color 0.6s; font-weight: 500; }
  
  textarea {
    width: 100%; height: 250px;
    background: var(--input-bg); border: 1px solid var(--glass-border); border-radius: 12px;
    padding: 1.25rem; font-family: inherit; font-size: 0.95rem; line-height: 1.6;
    color: var(--text-main); resize: none;
    transition: all 0.4s var(--apple-ease);
  }
  textarea:focus {
    outline: none; background: var(--glass-bg); border-color: var(--accent);
    box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.2);
  }
  
  /* Buttons */
  .actions { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; position: relative; z-index: 10; }
  
  button {
    font-family: inherit; font-size: 0.95rem; font-weight: 600; letter-spacing: -0.01em;
    padding: 0.75rem 1.5rem; border-radius: 999px; border: none; cursor: pointer;
    transition: transform 0.3s var(--bounce-ease), background 0.4s, box-shadow 0.4s, color 0.4s, border-color 0.4s;
    display: flex; align-items: center; gap: 0.5rem; color: var(--text-main);
  }
  button:active { transform: scale(0.92); }
  
  .btn-primary {
    background: linear-gradient(135deg, var(--text-main), #555); color: var(--bg-color);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2); padding: 0.8rem 2rem; font-size: 1.05rem;
  }
  .dark .btn-primary { background: linear-gradient(135deg, #fff, #bbb); color: #000; }
  .btn-primary:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 12px 28px rgba(0,0,0,0.25); }
  
  .btn-secondary {
    background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow);
  }
  .btn-secondary:hover { transform: translateY(-2px); background: var(--glass-border); }

  /* Loader */
  .loader-container {
    position: fixed; inset: 0; z-index: 50; display: flex; flex-direction: column; justify-content: center; align-items: center;
    opacity: 0; pointer-events: none; transition: opacity 0.5s var(--apple-ease);
  }
  .loader-container.active { opacity: 1; pointer-events: all; }
  
  .spinner-3d {
    width: 60px; height: 60px; border-radius: 50%; border: 4px solid transparent; border-top-color: var(--accent); border-right-color: var(--accent);
    animation: spin3D 1s cubic-bezier(0.68, -0.55, 0.26, 1.55) infinite; margin-bottom: 1.5rem;
  }
  @keyframes spin3D {
    0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
    100% { transform: rotateX(180deg) rotateY(360deg) rotateZ(360deg); }
  }
  .loader-text { font-size: 1.2rem; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: var(--text-main); animation: pulse 1.5s infinite; transition: color 0.6s; }
  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

  /* Results (Creative Entrance) */
  .results-section {
    width: 100%; display: none; flex-direction: column; gap: 2rem;
    opacity: 0; transform: perspective(1000px) rotateX(-10deg) translateY(60px) scale(0.95);
    transform-origin: center top; transition: all 0.9s var(--bounce-ease);
  }
  .results-section.visible { display: flex; opacity: 1; transform: perspective(1000px) rotateX(0deg) translateY(0) scale(1); }
  
  .score-panel { padding: 3rem; display: flex; align-items: center; justify-content: center; gap: 4rem; }
  @media (max-width: 700px) { .score-panel { flex-direction: column; gap: 2rem; text-align: center; } }
  
  .gauge-container { position: relative; width: 180px; height: 180px; }
  .gauge-svg { transform: rotate(-90deg); width: 100%; height: 100%; overflow: visible; }
  .gauge-bg { fill: none; stroke: var(--glass-border); stroke-width: 14; stroke-linecap: round; transition: stroke 0.6s; }
  .gauge-fg {
    fill: none; stroke: var(--accent); stroke-width: 14; stroke-linecap: round;
    stroke-dasharray: 502.65; stroke-dashoffset: 502.65;
    transition: stroke-dashoffset 1.5s var(--bounce-ease), stroke 0.5s;
    filter: drop-shadow(0 4px 16px rgba(0,0,0,0.25));
  }
  
  /* Textured Font for Percentage */
  .gauge-val {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    width: 100%; text-align: center;
  }
  #scoreValStr {
    font-size: 2.8rem; font-weight: 800; letter-spacing: -0.04em;
    /* This gradient will be overridden by JS for dynamic colors */
    background: linear-gradient(135deg, var(--text-main), var(--text-sec));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }
  .gauge-pct {
    font-size: 1.4rem; font-weight: 700; margin-left: 2px;
    background: inherit; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  
  /* Textured Verdict Title */
  .verdict-info h3 { 
    font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -0.04em; 
    background: linear-gradient(135deg, var(--text-main), var(--text-sec));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .verdict-info p { max-width: 400px; margin-bottom: 2rem; color: var(--text-sec); transition: color 0.6s; font-weight: 500; }
  
  .stats { display: flex; gap: 2.5rem; }
  @media (max-width: 700px) { .stats { justify-content: center; } }
  .stat-val { font-size: 1.8rem; font-weight: 800; color: var(--text-main); transition: color 0.6s; letter-spacing: -0.02em; }
  .stat-lbl { font-size: 0.75rem; color: var(--text-sec); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; transition: color 0.6s; }
  
  /* Matches */
  .match-card {
    padding: 1.5rem; margin-bottom: 1.5rem;
    opacity: 0; transform: perspective(1000px) rotateX(15deg) translateY(30px);
    transition: all 0.7s var(--bounce-ease), background 0.6s, border 0.6s;
  }
  .match-card.show { opacity: 1; transform: perspective(1000px) rotateX(0deg) translateY(0); }
  
  .match-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; }
  .match-badge { padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
  .badge-high { background: rgba(255,59,48,0.15); color: var(--danger); border: 1px solid rgba(255,59,48,0.2); }
  .badge-para { background: rgba(255,149,0,0.15); color: var(--warning); border: 1px solid rgba(255,149,0,0.2); }
  
  .match-score { 
    font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(135deg, var(--text-main), var(--text-sec));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  
  .match-content { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
  @media (max-width: 700px) { .match-content { grid-template-columns: 1fr; } }
  
  .match-col { background: var(--input-bg); padding: 1.25rem; border-radius: 12px; border: 1px solid var(--glass-border); transition: background 0.6s, border 0.6s; }
  .col-lbl { font-size: 0.75rem; color: var(--text-sec); font-weight: 700; margin-bottom: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; transition: color 0.6s; }
  .col-txt { font-size: 0.95rem; line-height: 1.6; color: var(--text-main); transition: color 0.6s; font-weight: 500; }

  /* Toast */
  .toast {
    position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%) translateY(100px) scale(0.9);
    background: var(--text-main); color: var(--bg-color); padding: 0.8rem 1.8rem; border-radius: 999px;
    font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: all 0.5s var(--bounce-ease), background 0.6s, color 0.6s; z-index: 2000;
  }
  .toast.show { transform: translateX(-50%) translateY(0) scale(1); }
</style>
</head>
<body>

<div class="bg-mesh"></div>

<nav class="navbar">
  <div class="nav-logo">SPD</div>
  
  <div class="theme-switch-wrapper">
    <svg class="theme-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
    <label class="theme-switch" for="checkbox">
      <input type="checkbox" id="checkbox" onchange="toggleTheme()" aria-label="Toggle Theme">
      <div class="slider"></div>
    </label>
    <svg class="theme-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
  </div>
</nav>

<div class="loader-container" id="loader">
  <div class="spinner-3d"></div>
  <div class="loader-text">Analyzing</div>
</div>

<div class="toast" id="toast">Message</div>

<div class="container">
  
  <div class="input-section" id="inputSection">
    <h1>Semantic Plagiarism</h1>
    <p class="subtitle">Meaning-level detection.</p>
    
    <div class="editor-grid">
      <div class="glass editor-card">
        <div class="card-header">
          <span class="card-title">Source Text</span>
          <span class="word-count" id="srcCount">0 words</span>
        </div>
        <textarea id="source" placeholder="Enter original reference text..."></textarea>
      </div>
      
      <div class="glass editor-card">
        <div class="card-header">
          <span class="card-title">Suspect Text</span>
          <span class="word-count" id="susCount">0 words</span>
        </div>
        <textarea id="suspect" placeholder="Enter suspect document text..."></textarea>
      </div>
    </div>
    
    <div class="actions">
      <button class="btn-primary" onclick="runAnalysis()">Analyze Documents</button>
      <button class="btn-secondary" onclick="loadSample('para')">Demo: Paraphrase</button>
      <button class="btn-secondary" onclick="loadSample('light')">Demo: Light Edit</button>
      <button class="btn-secondary" onclick="loadSample('diff')">Demo: Unrelated</button>
    </div>
  </div>
  
  <div class="results-section" id="resultsSection">
    <div class="actions" style="margin-bottom: 0;">
      <button class="btn-secondary" onclick="resetView()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg> Back to Editor
      </button>
    </div>

    <div class="glass score-panel">
      <div class="gauge-container">
        <svg class="gauge-svg" viewBox="0 0 200 200">
          <circle class="gauge-bg" cx="100" cy="100" r="80"></circle>
          <circle class="gauge-fg" id="gaugeFg" cx="100" cy="100" r="80"></circle>
        </svg>
        <div class="gauge-val">
          <span id="scoreValStr">0</span><span class="gauge-pct">%</span>
        </div>
      </div>
      
      <div class="verdict-info">
        <h3 id="verdictTitle">--</h3>
        <p id="verdictDesc">--</p>
        <div class="stats">
          <div><div class="stat-val" id="statMatches">0</div><div class="stat-lbl">Matches</div></div>
          <div><div class="stat-val" id="statSrc">0</div><div class="stat-lbl">Src Sec</div></div>
          <div><div class="stat-val" id="statSus">0</div><div class="stat-lbl">Sus Sec</div></div>
        </div>
      </div>
    </div>
    
    <div id="matchList"></div>
    
    <div class="actions" style="margin-top: 1rem;">
      <button class="btn-secondary" onclick="downloadReport('html')">Export HTML Report</button>
      <button class="btn-secondary" onclick="downloadReport('md')">Export Markdown</button>
    </div>
  </div>
</div>

<script>
// Sleek CSS-based Theme Toggle
function toggleTheme() {
  document.documentElement.classList.toggle('dark');
}

// Check system pref
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) { 
  document.getElementById('checkbox').checked = true;
  document.documentElement.classList.add('dark');
}

const samples = {
  para: {
    source: `Artificial intelligence has transformed numerous industries by enabling machines to perform tasks that traditionally required human intelligence. Machine learning algorithms can analyse large datasets to identify patterns and make predictions with remarkable accuracy. In healthcare, AI systems assist doctors in diagnosing diseases from medical images and predicting patient outcomes. Natural language processing allows computers to understand and generate human language, powering applications such as chatbots and translation services. Despite these advances, concerns remain about data privacy, algorithmic bias, and the potential displacement of human workers. Researchers continue to develop more transparent and ethical AI systems that can be trusted in critical decision-making scenarios.`,
    suspect: `The field of artificial intelligence has revolutionised many sectors by allowing computers to execute activities that once depended on human cognition. Algorithms based on machine learning are capable of examining vast collections of data in order to discover trends and generate forecasts with high precision. Within the medical domain, intelligent systems help physicians detect illnesses using scans and estimate how patients will progress. Through natural language processing, machines can interpret and produce spoken or written language, which supports tools like virtual assistants and automated translators. Nevertheless, issues related to the confidentiality of information, unfair bias in models, and the risk that automation may replace human jobs still exist. Scientists are persistently creating AI solutions that are more interpretable and morally sound so they can be relied upon for important choices.`
  },
  light: {
    source: `Artificial intelligence has transformed numerous industries by enabling machines to perform tasks that traditionally required human intelligence. Machine learning algorithms can analyse large datasets to identify patterns and make predictions with remarkable accuracy. In healthcare, AI systems assist doctors in diagnosing diseases from medical images and predicting patient outcomes. Natural language processing allows computers to understand and generate human language, powering applications such as chatbots and translation services. Despite these advances, concerns remain about data privacy, algorithmic bias, and the potential displacement of human workers. Researchers continue to develop more transparent and ethical AI systems that can be trusted in critical decision-making scenarios.`,
    suspect: `Artificial intelligence has changed many industries by enabling machines to perform tasks that traditionally required human intelligence. Machine learning algorithms can examine large datasets to find patterns and make predictions with high accuracy. In the healthcare sector, AI systems help doctors diagnose diseases from medical images and predict patient outcomes. Natural language processing enables computers to understand and generate human language, powering apps such as chatbots and translation tools. Despite these advances, worries remain about data privacy, algorithmic bias, and possible job losses for human workers. Researchers keep developing more transparent and ethical AI systems that can be trusted for critical decisions.`
  },
  diff: {
    source: `Artificial intelligence has transformed numerous industries by enabling machines to perform tasks that traditionally required human intelligence. Machine learning algorithms can analyse large datasets to identify patterns and make predictions with remarkable accuracy. In healthcare, AI systems assist doctors in diagnosing diseases from medical images and predicting patient outcomes.`,
    suspect: `Climate change represents one of the most pressing challenges of the twenty-first century. Rising global temperatures are causing polar ice caps to melt, leading to higher sea levels and more frequent extreme weather events. Governments and international organisations have set ambitious targets to reduce greenhouse gas emissions through renewable energy adoption and carbon pricing mechanisms.`
  }
};

let lastReport = null;

const sourceEl = document.getElementById('source');
const suspectEl = document.getElementById('suspect');
const inputSec = document.getElementById('inputSection');
const resSec = document.getElementById('resultsSection');
const loader = document.getElementById('loader');

sourceEl.addEventListener('input', () => updateCount('source', 'srcCount'));
suspectEl.addEventListener('input', () => updateCount('suspect', 'susCount'));

function updateCount(id, outId) {
  const val = document.getElementById(id).value.trim();
  const cnt = val ? val.split(/\s+/).length : 0;
  document.getElementById(outId).textContent = cnt + ' words';
}

function loadSample(k) {
  sourceEl.value = samples[k].source; suspectEl.value = samples[k].suspect;
  updateCount('source', 'srcCount'); updateCount('suspect', 'susCount');
  showToast('Sample loaded');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

function resetView() {
  resSec.classList.remove('visible');
  setTimeout(() => {
    resSec.style.display = 'none';
    inputSec.style.position = 'relative';
    inputSec.classList.remove('hidden');
    // reset gauge
    const fg = document.getElementById('gaugeFg');
    fg.style.transition = 'none';
    fg.style.strokeDashoffset = 502.65;
  }, 600); // wait for results to animate out
}

function animateVal(id, start, end, dur) {
  const el = document.getElementById(id);
  let startT = null;
  const step = (t) => {
    if (!startT) startT = t;
    const p = Math.min((t - startT) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 4);
    const v = start + (end - start) * ease;
    el.textContent = (end % 1 !== 0) ? v.toFixed(1) : Math.round(v);
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

async function runAnalysis() {
  const src = sourceEl.value.trim();
  const sus = suspectEl.value.trim();
  if (!src || !sus) { showToast('Please enter both documents'); return; }
  
  // Cinematic Transition: Hide inputs, show loader
  inputSec.classList.add('hidden');
  
  setTimeout(() => {
    inputSec.style.position = 'absolute';
    loader.classList.add('active');
  }, 400);
  
  try {
    const res = await fetch('/api/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source: src, suspect: sus })
    });
    if (!res.ok) throw new Error('API Error');
    const data = await res.json();
    lastReport = data;
    
    // Simulate delay for dramatic effect
    setTimeout(() => {
      loader.classList.remove('active');
      setTimeout(() => renderResults(data), 400);
    }, 800);
    
  } catch(e) {
    loader.classList.remove('active');
    setTimeout(() => {
      inputSec.style.position = 'relative';
      inputSec.classList.remove('hidden');
      showToast(e.message);
    }, 400);
  }
}

function renderResults(data) {
  resSec.style.display = 'flex';
  
  // Trigger reflow for CSS animation
  void resSec.offsetWidth;
  resSec.classList.add('visible');
  
  const pct = data.overall_similarity;
  
  // Dynamic Gradients for Textured Immersive Fonts
  let color = 'var(--success)';
  let gradient = 'linear-gradient(135deg, #34c759, #30b0c7)'; // Green to Teal
  
  if (pct >= 55) {
    color = 'var(--danger)';
    gradient = 'linear-gradient(135deg, #ff3b30, #ff9500)'; // Red to Orange
  } else if (pct >= 35) {
    color = 'var(--warning)';
    gradient = 'linear-gradient(135deg, #ff9500, #ffcc00)'; // Orange to Yellow
  }
  
  // Apply Gradient Texture to Gauge Number
  const scoreValStr = document.getElementById('scoreValStr');
  scoreValStr.style.background = gradient;
  scoreValStr.style.webkitBackgroundClip = 'text';
  scoreValStr.style.webkitTextFillColor = 'transparent';
  
  // Apply Gradient Texture to Verdict Title
  const vt = document.getElementById('verdictTitle');
  vt.textContent = data.verdict;
  vt.style.background = gradient;
  vt.style.webkitBackgroundClip = 'text';
  vt.style.webkitTextFillColor = 'transparent';
  
  // Animate Gauge Line
  const fg = document.getElementById('gaugeFg');
  fg.style.stroke = color;
  const offset = 502.65 - (pct / 100) * 502.65;
  setTimeout(() => fg.style.strokeDashoffset = offset, 200); 
  
  // Animate Numbers
  animateVal('scoreValStr', 0, pct, 1800);
  animateVal('statMatches', 0, data.matches.length, 1200);
  animateVal('statSrc', 0, data.source_sections, 1200);
  animateVal('statSus', 0, data.suspect_sections, 1200);
  
  document.getElementById('verdictDesc').textContent = 
    pct >= 55 ? 'High probability of plagiarism detected.' :
    pct >= 35 ? 'Moderate similarity found. Indicates paraphrasing or shared sources.' :
    'Low similarity. Documents appear original.';
    
  // Matches
  const list = document.getElementById('matchList');
  list.innerHTML = '';
  
  if (data.matches.length === 0) {
    list.innerHTML = '<div class="glass" style="padding: 3rem; text-align: center; color: var(--text-sec); border-radius: 20px;">No matching sections found.</div>';
  } else {
    data.matches.forEach((m, i) => {
      const isPara = m.is_paraphrase;
      const cColor = isPara ? 'var(--warning)' : 'var(--danger)';
      const cGrad = isPara ? 'linear-gradient(135deg, #ff9500, #ffcc00)' : 'linear-gradient(135deg, #ff3b30, #ff9500)';
      const bgClass = isPara ? 'badge-para' : 'badge-high';
      const label = isPara ? 'Paraphrased' : 'High Similarity';
      
      const card = document.createElement('div');
      card.className = 'glass match-card';
      card.innerHTML = `
        <div class="match-header">
          <span class="match-badge ${bgClass}">${label}</span>
          <span class="match-score" style="background: ${cGrad}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ${(m.similarity * 100).toFixed(1)}%
          </span>
        </div>
        <div class="match-content">
          <div class="match-col">
            <div class="col-lbl">Source Document</div>
            <div class="col-txt">${escape(m.source_text)}</div>
          </div>
          <div class="match-col">
            <div class="col-lbl">Suspect Document</div>
            <div class="col-txt">${escape(m.suspect_text)}</div>
          </div>
        </div>
      `;
      list.appendChild(card);
      
      // Staggered 3D entrance
      setTimeout(() => card.classList.add('show'), 200 * i + 400);
    });
  }
}

function escape(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function downloadReport(type) {
  if (!lastReport) return;
  const content = type === 'html' ? lastReport.html : lastReport.markdown;
  const blob = new Blob([content], { type: type === 'html' ? 'text/html' : 'text/markdown' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = `plagiarism_report.${type}`; a.click();
  showToast('Report downloaded');
}

window.addEventListener('DOMContentLoaded', () => loadSample('para'));
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# JSON encoder that handles numpy types
# ---------------------------------------------------------------------------
class _NumpyEncoder(json.JSONEncoder):
    """Safely serialise numpy scalars / arrays that json.dumps chokes on."""
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # quieter logs
        if args and "200" in str(args[1]):
            return
        print(f"[{self.address_string()}] {format % args}")

    def _json(self, code: int, data: dict):
        body = json.dumps(data, cls=_NumpyEncoder).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/health":
            self._json(200, {"status": "ok", "engine": "semantic-v1"})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/detect":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            source = payload.get("source", "").strip()
            suspect = payload.get("suspect", "").strip()
            if not source or not suspect:
                self._json(400, {"error": "Both source and suspect texts are required"})
                return

            report = DETECTOR.detect(source, suspect)

            matches = []
            for m in report.matched_pairs:
                matches.append({
                    "similarity": round(float(m.similarity), 4),
                    "is_paraphrase": bool(m.is_paraphrase),
                    "source_text": m.source_section.text,
                    "suspect_text": m.suspect_section.text,
                })

            self._json(200, {
                "overall_similarity": float(report.overall_similarity),
                "verdict": report.verdict,
                "matches": matches,
                "source_sections": len(report.source_sections),
                "suspect_sections": len(report.suspect_sections),
                "html": report.to_html(),
                "markdown": report.to_markdown(),
            })
        except Exception as e:
            self._json(500, {"error": str(e)})


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main():
    port = 7860
    server = HTTPServer(("0.0.0.0", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print("=" * 56)
    print("  Semantic Plagiarism Detection Agent")
    print("  Premium Web UI")
    print("=" * 56)
    print(f"  -> Open in browser:  {url}")
    print("  -> Press Ctrl+C to stop")
    print("=" * 56)

    # Auto-open browser after short delay (optional)
    def _open():
        import time
        time.sleep(0.8)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
