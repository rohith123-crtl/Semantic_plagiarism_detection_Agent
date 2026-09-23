# Semantic Plagiarism Detection Agent

**Microsoft Codeathon – Problem Statement 5**  
**Domain:** Education | **Technology:** NLP · Embeddings · Semantic Search

---

## Problem

Traditional plagiarism checkers rely on exact word / phrase matching. Students can easily evade detection by paraphrasing or restructuring content.

**Goal:** Build a system that detects similarity based on *meaning*, not just surface form.

---

## Solution Overview

| Requirement                    | Implementation                                      |
|--------------------------------|-----------------------------------------------------|
| Document / text processing     | Paragraph + size-based chunking                     |
| Semantic embeddings            | Pluggable embedder (TF-IDF+n-gram offline / SBERT)  |
| Similarity calculation         | Cosine similarity on L2-normalised vectors          |
| Paraphrase detection           | Dual threshold (similar vs strong paraphrase)       |
| Matching section identification| Greedy best-match pairing of sections               |
| Similarity percentage          | Weighted overall score (avg similarity + coverage)  |
| Plagiarism report              | Console + Markdown + HTML reports                   |

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Source Doc │────▶│  Sectioner   │────▶│                 │
└─────────────┘     └──────────────┘     │  Embedder       │
                                         │  (TF-IDF / SBERT)│
┌─────────────┐     ┌──────────────┐     │                 │
│ Suspect Doc │────▶│  Sectioner   │────▶│                 │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │ Cosine Matrix   │
                                         │ + Greedy Match  │
                                         └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │ Report Generator│
                                         │ (MD / HTML / CLI)│
                                         └─────────────────┘
```

---

## Quick Start

### Premium Web UI (Recommended for Jury)

```bash
python web_app.py
```
Open **http://127.0.0.1:7860**

- Modern dark SaaS interface with animated similarity gauge  
- Side-by-side matching section comparison  
- One-click sample loads (heavy paraphrase / light edit / unrelated)  
- Downloadable HTML & Markdown reports  
- Fully offline · zero extra dependencies  

### CLI Mode

```bash
python main.py --demo
python main.py --source original.txt --suspect student.txt --report report.html
```

---

## Switching to Real Semantic Embeddings

When network / packages are available:

```bash
pip install sentence-transformers
```

Then in `detector.py` or `main.py`:

```python
from embedder import SentenceTransformerEmbedder
detector = SemanticPlagiarismDetector(
    embedder=SentenceTransformerEmbedder("all-MiniLM-L6-v2")
)
```

The rest of the pipeline stays identical.

---

## Project Structure

```
semantic_plagiarism_detector/
├── web_app.py           # ⭐ Premium Web UI (start here for jury)
├── main.py              # CLI entry point + demo
├── detector.py          # Core engine + report generation
├── embedder.py          # Pluggable embedding backends
├── sample_data.py       # Built-in test documents
├── requirements.txt
└── README.md
```

---

## Evaluation Notes for Judges

- Works **completely offline** (no internet / API keys required).
- Clean separation of concerns → easy to extend with better models.
- Produces human-readable reports suitable for educators.
- Handles both heavy paraphrasing and light editing scenarios.
- Explicit thresholds make the system tunable for different strictness levels.

---

*Built for Forge Alumnus × Microsoft Codeathon*
