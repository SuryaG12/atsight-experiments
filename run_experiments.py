"""Experiment harness for the ATSight paper.

Experiment 1 - Consistency and distribution:
  * Determinism: score one resume 10 times, report variance (should be ~0).
  * Distribution: score the full 50-resume corpus, report mean/std per tier.

Experiment 2 - Ablation:
  Take one strong resume and apply one degradation at a time, measuring the
  score delta each causes. Answers: what does the scorer actually care about?

Usage:
  python run_experiments.py            # runs everything
Output:
  results/scores.csv                   # every resume, total + per-check points
  results/determinism.csv              # 10 repeated runs of one resume
  results/ablation.csv                 # degradation -> score delta
"""
from __future__ import annotations

import csv
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
BACKEND = Path.home() / "workspace" / "resume-analyzer-build" / "backend"
sys.path.insert(0, str(BACKEND))

from ats_scorer import score_ats  # noqa: E402

CORPUS = HERE / "corpus"
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

CHECK_NAMES = ["Contact information", "Section headers",
               "Quantified achievements", "Length", "Action verbs",
               "ATS-friendly formatting", "Keyword relevance"]


def score_file(path: Path) -> dict:
    result = score_ats(path.read_text())
    row = {"file": path.name, "total": result.total}
    for c in result.checks:
        row[c.name] = c.points
    return row


def experiment_1() -> None:
    # Determinism: same resume scored 10 times.
    target = CORPUS / "strong-01.txt"
    totals = [score_file(target)["total"] for _ in range(10)]
    with open(RESULTS / "determinism.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "total"])
        w.writerows(enumerate(totals, 1))
    var = statistics.pvariance(totals)
    print(f"[exp1] determinism: 10 runs, mean={statistics.mean(totals):.1f}, "
          f"variance={var:.4f}")

    # Distribution across the corpus.
    rows = []
    for path in sorted(CORPUS.glob("*.txt")):
        rows.append(score_file(path))
    with open(RESULTS / "scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "total", *CHECK_NAMES])
        w.writeheader()
        w.writerows(rows)
    tiers: dict[str, list[float]] = {}
    for r in rows:
        tier = r["file"].rsplit("-", 1)[0]
        tiers.setdefault(tier, []).append(r["total"])
    print("[exp1] per-tier totals (mean +/- std):")
    for tier in sorted(tiers):
        vals = tiers[tier]
        print(f"  {tier:16s} n={len(vals):2d}  "
              f"{statistics.mean(vals):6.1f} +/- {statistics.pstdev(vals):4.1f}")


def degrade_email(text: str) -> str:
    return re.sub(r"\S+@example\.com", "", text)


def degrade_numbers(text: str) -> str:
    # Strip quantified achievements: percentages, dollar amounts, counts.
    text = re.sub(r"\d+\s?%", "several percent", text)
    text = re.sub(r"\$\s?[\d,]+", "a budget", text)
    text = re.sub(r"\b\d{2,}\+?\b", "many", text)
    return text


def degrade_headers(text: str) -> str:
    swaps = {"Experience": "My Story", "Education": "Schooling",
             "Skills": "Things I Know", "Projects": "Stuff I Made",
             "Summary": "About Me"}
    for old, new in swaps.items():
        text = re.sub(rf"^{old}$", new, text, flags=re.M)
    return text


def degrade_skills_section(text: str) -> str:
    return re.sub(r"(?ms)^Skills\n.*?(?=\n[A-Z][a-z]+(\s[A-Z][a-z]+)?\n|\Z)",
                  "", text, count=1)


def degrade_bullets(text: str) -> str:
    # Join bullets into dense paragraphs (kills the action-verb check).
    lines = []
    buf = []
    for ln in text.splitlines():
        if ln.startswith("- "):
            buf.append(ln[2:])
        else:
            if buf:
                lines.append(" ".join(buf) + ".")
                buf = []
            lines.append(ln)
    if buf:
        lines.append(" ".join(buf) + ".")
    return "\n".join(lines)


ABLATIONS = [
    ("remove_email", degrade_email),
    ("remove_quantified_numbers", degrade_numbers),
    ("nonstandard_headers", degrade_headers),
    ("remove_skills_section", degrade_skills_section),
    ("bullets_to_paragraphs", degrade_bullets),
]


def experiment_2() -> None:
    base_text = (CORPUS / "strong-01.txt").read_text()
    base = score_ats(base_text).total
    rows = []
    print(f"[exp2] baseline strong-01.txt: {base:.1f}")
    for name, fn in ABLATIONS:
        total = score_ats(fn(base_text)).total
        delta = total - base
        rows.append({"degradation": name, "total": round(total, 1),
                     "delta": round(delta, 1)})
        print(f"  {name:26s} {total:6.1f}  (delta {delta:+.1f})")
    with open(RESULTS / "ablation.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["degradation", "total", "delta"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    experiment_1()
    experiment_2()
    print(f"\nResults written to {RESULTS}")
