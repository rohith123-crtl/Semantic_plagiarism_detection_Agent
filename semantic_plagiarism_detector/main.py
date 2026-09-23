#!/usr/bin/env python3
"""
Semantic Plagiarism Detection Agent
===================================
Microsoft Codeathon – Problem Statement 5

Usage:
    python main.py                          # run demo with sample data
    python main.py --source file1.txt --suspect file2.txt
    python main.py --source file1.txt --suspect file2.txt --report report.html
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from detector import SemanticPlagiarismDetector
from sample_data import ORIGINAL, PARAPHRASED, DIFFERENT, LIGHTLY_EDITED


def load_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found → {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8", errors="ignore")


def print_report(report, title: str = "Detection Result"):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"  Overall Similarity : {report.overall_similarity:.1f}%")
    print(f"  Verdict            : {report.verdict}")
    print(f"  Matching sections  : {len(report.matched_pairs)}")
    print("-" * 60)

    if report.matched_pairs:
        for i, m in enumerate(report.matched_pairs, 1):
            flag = "PARAPHRASE" if m.is_paraphrase else "SIMILAR"
            print(f"\n  [{i}] {flag} — {m.similarity*100:.1f}%")
            print(f"      Source : {m.source_section.text[:120]}…")
            print(f"      Suspect: {m.suspect_section.text[:120]}…")
    else:
        print("\n  No high-similarity sections found.")
    print("=" * 60 + "\n")


def run_demo():
    print("\n🚀 Semantic Plagiarism Detection Agent – Demo Mode\n")
    detector = SemanticPlagiarismDetector(
        similarity_threshold=0.50,
        paraphrase_threshold=0.68,
    )

    # Case 1: Heavy paraphrase (should detect)
    print("▶ Case 1: Heavy paraphrase of original text")
    report1 = detector.detect(ORIGINAL, PARAPHRASED)
    print_report(report1, "Original vs Heavy Paraphrase")

    # Case 2: Completely different topic
    print("▶ Case 2: Completely different document")
    report2 = detector.detect(ORIGINAL, DIFFERENT)
    print_report(report2, "Original vs Unrelated Text")

    # Case 3: Light editing
    print("▶ Case 3: Lightly edited version")
    report3 = detector.detect(ORIGINAL, LIGHTLY_EDITED)
    print_report(report3, "Original vs Lightly Edited")

    # Save a nice HTML report for the strongest case
    html_path = Path("demo_report.html")
    html_path.write_text(report1.to_html(), encoding="utf-8")
    print(f"✅ HTML report saved → {html_path.resolve()}")

    md_path = Path("demo_report.md")
    md_path.write_text(report1.to_markdown(), encoding="utf-8")
    print(f"✅ Markdown report saved → {md_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Semantic Plagiarism Detection Agent (Codeathon)"
    )
    parser.add_argument("--source", help="Path to original / source document")
    parser.add_argument("--suspect", help="Path to document under scrutiny")
    parser.add_argument("--report", help="Optional path to save HTML report")
    parser.add_argument("--threshold", type=float, default=0.55,
                        help="Similarity threshold (0-1)")
    parser.add_argument("--demo", action="store_true", help="Run built-in demo")
    args = parser.parse_args()

    if args.demo or (not args.source and not args.suspect):
        run_demo()
        return

    if not args.source or not args.suspect:
        parser.error("Both --source and --suspect are required (or use --demo)")

    source = load_text(args.source)
    suspect = load_text(args.suspect)

    detector = SemanticPlagiarismDetector(similarity_threshold=args.threshold)
    report = detector.detect(source, suspect)
    print_report(report)

    if args.report:
        Path(args.report).write_text(report.to_html(), encoding="utf-8")
        print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()
