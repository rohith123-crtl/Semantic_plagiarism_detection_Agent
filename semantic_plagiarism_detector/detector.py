"""
Semantic Plagiarism Detection Engine
====================================
Implements all minimum requirements:
  • Document / text processing
  • Semantic embeddings
  • Similarity calculation
  • Paraphrase detection
  • Matching section identification
  • Similarity percentage
  • Plagiarism report
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import numpy as np

from embedder import get_embedder, BaseEmbedder


@dataclass
class Section:
    id: int
    text: str
    start_char: int
    end_char: int


@dataclass
class Match:
    source_section: Section
    suspect_section: Section
    similarity: float
    is_paraphrase: bool


@dataclass
class PlagiarismReport:
    overall_similarity: float
    matched_pairs: List[Match]
    source_sections: List[Section]
    suspect_sections: List[Section]
    verdict: str
    details: Dict = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [
            "# Semantic Plagiarism Detection Report",
            "",
            f"**Overall Similarity:** `{self.overall_similarity:.1f}%`",
            f"**Verdict:** {self.verdict}",
            "",
            "## Summary",
            f"- Source sections analysed : {len(self.source_sections)}",
            f"- Suspect sections analysed: {len(self.suspect_sections)}",
            f"- High-similarity matches  : {len(self.matched_pairs)}",
            "",
        ]

        if not self.matched_pairs:
            lines.append("No significant semantic matches found.")
            return "\n".join(lines)

        lines.append("## Matching Sections (Potential Paraphrases)")
        lines.append("")
        for i, m in enumerate(self.matched_pairs, 1):
            flag = "🟡 PARAPHRASE" if m.is_paraphrase else "🔴 HIGH SIMILARITY"
            lines.extend([
                f"### Match {i} — {flag} ({m.similarity*100:.1f}%)",
                "",
                "**Source section:**",
                f"> {m.source_section.text[:400]}{'…' if len(m.source_section.text) > 400 else ''}",
                "",
                "**Suspect section:**",
                f"> {m.suspect_section.text[:400]}{'…' if len(m.suspect_section.text) > 400 else ''}",
                "",
                "---",
                "",
            ])
        return "\n".join(lines)

    def to_html(self) -> str:
        color = "#c0392b" if self.overall_similarity >= 40 else "#e67e22" if self.overall_similarity >= 25 else "#27ae60"
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Plagiarism Report</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
.score {{ font-size: 2.5rem; font-weight: 700; color: {color}; }}
.match {{ border-left: 4px solid #3498db; padding: 0.8rem 1rem; margin: 1rem 0; background: #f8f9fa; }}
.para  {{ border-left-color: #f39c12; }}
.high  {{ border-left-color: #e74c3c; }}
blockquote {{ margin: 0.3rem 0; color: #555; }}
</style></head><body>
<h1>Semantic Plagiarism Detection Report</h1>
<p class="score">{self.overall_similarity:.1f}%</p>
<p><strong>Verdict:</strong> {self.verdict}</p>
<p>Source sections: {len(self.source_sections)} &nbsp;|&nbsp;
   Suspect sections: {len(self.suspect_sections)} &nbsp;|&nbsp;
   Matches: {len(self.matched_pairs)}</p>
"""
        if not self.matched_pairs:
            html += "<p>No significant semantic matches found.</p>"
        else:
            html += "<h2>Matching Sections</h2>"
            for i, m in enumerate(self.matched_pairs, 1):
                cls = "para" if m.is_paraphrase else "high"
                label = "PARAPHRASE" if m.is_paraphrase else "HIGH SIMILARITY"
                html += f"""
<div class="match {cls}">
  <strong>Match {i} — {label} ({m.similarity*100:.1f}%)</strong>
  <p><em>Source:</em></p>
  <blockquote>{_escape(m.source_section.text[:500])}</blockquote>
  <p><em>Suspect:</em></p>
  <blockquote>{_escape(m.suspect_section.text[:500])}</blockquote>
</div>"""
        html += "</body></html>"
        return html


def _escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


class SemanticPlagiarismDetector:
    """
    Main engine.
    """

    def __init__(
        self,
        embedder: Optional[BaseEmbedder] = None,
        similarity_threshold: float = 0.55,
        paraphrase_threshold: float = 0.72,
        min_section_words: int = 15,
    ):
        self.embedder = embedder or get_embedder(prefer_semantic=True)
        self.similarity_threshold = similarity_threshold
        self.paraphrase_threshold = paraphrase_threshold
        self.min_section_words = min_section_words

    # ------------------------------------------------------------------
    # 1. Document / text processing
    # ------------------------------------------------------------------
    def process_document(self, text: str) -> List[Section]:
        """Split document into meaningful sections (paragraphs)."""
        # Normalise newlines
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Split on blank lines or long gaps
        raw_paras = re.split(r"\n\s*\n+", text.strip())
        sections: List[Section] = []
        offset = 0
        for i, para in enumerate(raw_paras):
            para = para.strip()
            if not para:
                continue
            # Skip very short fragments
            if len(para.split()) < self.min_section_words:
                # Try to merge with next if possible, otherwise keep if reasonable
                if len(para.split()) < 8:
                    offset += len(para) + 2
                    continue
            start = text.find(para, offset)
            end = start + len(para)
            sections.append(Section(id=len(sections), text=para, start_char=start, end_char=end))
            offset = end
        # Fallback: if almost no sections, chunk by sentences / fixed size
        if len(sections) < 2:
            sections = self._chunk_by_size(text, max_words=120)
        return sections

    def _chunk_by_size(self, text: str, max_words: int = 120) -> List[Section]:
        words = text.split()
        sections = []
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i + max_words])
            if len(chunk.split()) >= self.min_section_words:
                sections.append(Section(
                    id=len(sections),
                    text=chunk,
                    start_char=0,  # approximate
                    end_char=0
                ))
        return sections

    # ------------------------------------------------------------------
    # 2 & 3. Embeddings + Similarity
    # ------------------------------------------------------------------
    def _cosine_matrix(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Cosine similarity matrix (A and B are already L2-normalised)."""
        return np.dot(A, B.T)

    # ------------------------------------------------------------------
    # 4–6. Detection pipeline
    # ------------------------------------------------------------------
    def detect(self, source_text: str, suspect_text: str) -> PlagiarismReport:
        source_secs = self.process_document(source_text)
        suspect_secs = self.process_document(suspect_text)

        if not source_secs or not suspect_secs:
            return PlagiarismReport(
                overall_similarity=0.0,
                matched_pairs=[],
                source_sections=source_secs,
                suspect_sections=suspect_secs,
                verdict="Insufficient text to analyse."
            )

        # Generate embeddings
        src_texts = [s.text for s in source_secs]
        sus_texts = [s.text for s in suspect_secs]

        # Fit embedder on combined corpus for better IDF (important for TF-IDF mode)
        if hasattr(self.embedder, "fit"):
            self.embedder.fit(src_texts + sus_texts)

        src_emb = self.embedder.embed(src_texts)
        sus_emb = self.embedder.embed(sus_texts)

        sim_matrix = self._cosine_matrix(src_emb, sus_emb)

        # Find matching pairs
        matches: List[Match] = []
        used_src = set()
        used_sus = set()

        # Greedy matching of highest similarities
        flat = [(sim_matrix[i, j], i, j) for i in range(len(source_secs))
                for j in range(len(suspect_secs))]
        flat.sort(reverse=True)

        for score, i, j in flat:
            if score < self.similarity_threshold:
                break
            if i in used_src or j in used_sus:
                continue
            is_para = score >= self.paraphrase_threshold
            matches.append(Match(
                source_section=source_secs[i],
                suspect_section=suspect_secs[j],
                similarity=float(score),
                is_paraphrase=is_para
            ))
            used_src.add(i)
            used_sus.add(j)

        # Overall similarity: blend of match quality + coverage + peak signal
        max_sim = float(sim_matrix.max()) if sim_matrix.size else 0.0
        if matches:
            total_sus_words = sum(len(s.text.split()) for s in suspect_secs)
            matched_words = sum(len(m.suspect_section.text.split()) for m in matches)
            coverage = matched_words / max(total_sus_words, 1)
            avg_sim = sum(m.similarity for m in matches) / len(matches)
            # Strong single matches should still score high
            overall = (avg_sim * 0.55 + coverage * 0.25 + max_sim * 0.20) * 100
        else:
            # Soft fallback so weak but real signals are visible
            overall = max_sim * 100 * 0.55

        overall = min(100.0, max(0.0, overall))

        # Verdict
        if overall >= 55:
            verdict = "HIGH RISK of semantic plagiarism"
        elif overall >= 35:
            verdict = "MODERATE similarity – review recommended"
        elif overall >= 20:
            verdict = "LOW similarity – mostly original"
        else:
            verdict = "No significant semantic plagiarism detected"

        return PlagiarismReport(
            overall_similarity=round(overall, 1),
            matched_pairs=matches,
            source_sections=source_secs,
            suspect_sections=suspect_secs,
            verdict=verdict,
            details={
                "threshold": self.similarity_threshold,
                "paraphrase_threshold": self.paraphrase_threshold,
                "num_matches": len(matches),
            }
        )
