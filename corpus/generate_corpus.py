"""Synthetic resume corpus generator for the GradeMyResume paper experiments.

Generates 50 plain-text resumes across 5 quality tiers (10 each), with all
personal data clearly fake (example.com emails, fictional names/companies).
Each tier stresses different checks of the ATS scorer:

  strong          - complete, well-structured, quantified, keyword-rich
  average         - decent but missing several elements
  keyword_stuffed - bloated skills section, thin experience (tests whether
                    keyword relevance alone can carry a weak resume)
  poor_format     - nonstandard headers, missing contact, long dense lines
  thin            - very short, minimal content

Output: corpus/*.txt plus corpus/manifest.csv (filename, tier, word count).
Deterministic: same seed -> same corpus.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

SEED = 20261017
PER_TIER = 10
OUT_DIR = Path(__file__).parent

FIRST = ["Ava", "Liam", "Maya", "Noah", "Zoe", "Ethan", "Priya", "Lucas",
         "Nina", "Omar", "Ivy", "Kai", "Rosa", "Dev", "Lena", "Marco"]
LAST = ["Chen", "Patel", "Garcia", "Kim", "Novak", "Haddad", "Okafor",
        "Lindqvist", "Marsh", "Tanaka", "Reyes", "Kapoor"]
ROLES = ["Software Engineer", "Frontend Developer", "Backend Developer",
         "Data Analyst", "DevOps Engineer", "QA Engineer"]
COMPANIES = ["Northwind Labs", "Bluepeak Systems", "Copperline Tech",
             "Foxglove Analytics", "Harborlight Software", "Juniper Stack"]
SCHOOLS = ["State University", "Polytechnic Institute", "Community College"]
SKILLS_POOL = ["Python", "JavaScript", "TypeScript", "React", "Node.js",
               "PostgreSQL", "Docker", "Kubernetes", "AWS", "Git",
               "FastAPI", "Django", "GraphQL", "Redis", "CI/CD",
               "machine learning", "data analysis", "REST APIs",
               "unit testing", "Agile"]
ACTION_VERBS = ["Built", "Developed", "Designed", "Implemented", "Led",
                "Launched", "Improved", "Automated", "Deployed", "Optimized"]
WEAK_VERBS = ["Helped", "Worked", "Did", "Assisted", "Handled", "Tried"]


def _person(rng: random.Random) -> dict:
    first = rng.choice(FIRST)
    last = rng.choice(LAST)
    return {
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}{rng.randint(10, 99)}@example.com",
        "phone": f"({rng.randint(200, 989)}) {rng.randint(200, 989)}-{rng.randint(1000, 9999)}",
        "linkedin": f"linkedin.com/in/{first.lower()}-{last.lower()}{rng.randint(10, 99)}",
        "github": f"github.com/{first.lower()}{last.lower()}{rng.randint(10, 99)}",
        "role": rng.choice(ROLES),
    }


def _experience_bullets(rng: random.Random, n: int, quantified: bool,
                        strong_verbs: bool) -> list[str]:
    verbs = ACTION_VERBS if strong_verbs else WEAK_VERBS
    templates_q = [
        "{v} a customer dashboard serving {n1}k monthly users, cutting load time by {n2}%",
        "{v} CI pipelines that reduced deploy time from {n3} minutes to {n4} minutes",
        "{v} a reporting API used by {n5}+ internal tools across {n6} teams",
        "{v} onboarding docs adopted by {n7} new hires in one quarter",
        "{v} caching layer that lowered database load by {n8}%",
        "{v} an alerting system covering {n9} services with {n10}% fewer false positives",
    ]
    templates_v = [
        "{v} on the company website and fixed various bugs",
        "{v} with the team on several different projects",
        "{v} documentation and attended sprint meetings",
        "{v} testing and helped deploy releases",
    ]
    out = []
    for _ in range(n):
        t = rng.choice(templates_q if quantified else templates_v)
        out.append("- " + t.format(
            v=rng.choice(verbs),
            n1=rng.randint(5, 80), n2=rng.randint(10, 60),
            n3=rng.randint(20, 60), n4=rng.randint(2, 10),
            n5=rng.randint(3, 15), n6=rng.randint(2, 8),
            n7=rng.randint(5, 30), n8=rng.randint(15, 70),
            n9=rng.randint(4, 20), n10=rng.randint(20, 60)))
    return out


def make_strong(p: dict, rng: random.Random) -> str:
    skills = ", ".join(rng.sample(SKILLS_POOL, rng.randint(11, 16)))
    exp = _experience_bullets(rng, rng.randint(7, 10), quantified=True,
                              strong_verbs=True)
    split = rng.randint(4, 6)
    projs = [
        "- Personal finance tracker with 2k downloads on GitHub",
        "- Open-source contributor to a testing library with 40+ merged pull requests",
        "- Built a URL shortener handling 10k redirects per day",
    ]
    lines = [
        p["name"], p["email"], p["phone"], p["linkedin"], p["github"], "",
        "Summary",
        f"{p['role']} with {rng.randint(3, 6)} years of experience building web applications "
        "and data pipelines. Looking for a senior engineering role.", "",
        "Experience",
        f"Senior {p['role']} | {rng.choice(COMPANIES)} | 2021 - Present",
        *exp[:split], "",
        f"{p['role']} | {rng.choice(COMPANIES)} | 2019 - 2021",
        *exp[split:], "",
        "Education",
        f"B.S. Computer Science | {rng.choice(SCHOOLS)} | 2015 - 2019", "",
        "Skills", skills, "",
        "Projects",
        *rng.sample(projs, rng.randint(1, 3)),
    ]
    return "\n".join(lines)


def make_average(p: dict, rng: random.Random) -> str:
    skills = ", ".join(rng.sample(SKILLS_POOL, rng.randint(6, 10)))
    exp = _experience_bullets(rng, rng.randint(4, 6),
                              quantified=rng.random() < 0.7,
                              strong_verbs=rng.random() < 0.8)
    contact = [p["name"], p["email"]]
    if rng.random() < 0.5:
        contact.append(p["phone"])
    lines = [
        *contact, "",
        "Experience",
        f"{p['role']} | {rng.choice(COMPANIES)} | 2020 - Present",
        *exp, "",
        "Education",
        f"B.S. Computer Science | {rng.choice(SCHOOLS)} | 2016 - 2020", "",
        "Skills", skills,
    ]
    return "\n".join(lines)


def make_keyword_stuffed(p: dict, rng: random.Random) -> str:
    skills = ", ".join(SKILLS_POOL) + ", " + ", ".join(rng.sample(SKILLS_POOL, rng.randint(4, 8)))
    n_bullets = rng.randint(1, 3)
    bullets = [
        "- Responsible for various engineering tasks and team support.",
        "- Participated in code reviews and project planning sessions.",
        "- Helped with deployments and documentation updates.",
    ]
    lines = [
        p["name"], p["email"], p["phone"], "",
        "Experience",
        f"{p['role']} | {rng.choice(COMPANIES)} | 2021 - Present",
        *bullets[:n_bullets], "",
        "Skills", skills,
    ]
    return "\n".join(lines)


def make_poor_format(p: dict, rng: random.Random) -> str:
    blob = (" ".join(
        f"{rng.choice(WEAK_VERBS).lower()} on {rng.choice(['website updates', 'bug fixes', 'data entry', 'testing tasks'])}"
        f" at {rng.choice(COMPANIES)};" for _ in range(rng.randint(4, 8))))
    lines = [
        p["name"], "",
        "My Story",
        f"I am a {p['role'].lower()} looking for work. " + blob, "",
        "What I Did",
        "I have done many things over the years including lots of programming "
        "and working with different teams on various stuff @#$%^&* !!!",
    ]
    return "\n".join(lines)


def make_thin(p: dict, rng: random.Random) -> str:
    lines = [
        p["name"], p["email"], "",
        "Experience",
        f"{p['role']} | {rng.choice(COMPANIES)}",
        "- Did development work.", "",
        "Skills",
        "Python, JavaScript",
    ]
    return "\n".join(lines)


BUILDERS = {
    "strong": make_strong,
    "average": make_average,
    "keyword_stuffed": make_keyword_stuffed,
    "poor_format": make_poor_format,
    "thin": make_thin,
}


def main() -> None:
    rng = random.Random(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for tier, builder in BUILDERS.items():
        for i in range(PER_TIER):
            p = _person(rng)
            text = builder(p, rng)
            fname = f"{tier}-{i + 1:02d}.txt"
            (OUT_DIR / fname).write_text(text)
            manifest.append((fname, tier, len(text.split())))
    with open(OUT_DIR / "manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "tier", "words"])
        w.writerows(manifest)
    print(f"Wrote {len(manifest)} resumes to {OUT_DIR}")


if __name__ == "__main__":
    main()
