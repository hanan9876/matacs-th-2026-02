"""Deterministic scoring step of the triage design.

Input: extracted.json (structured facts, as the AI extraction step would return
after validation) + criteria.json (admin config). No LLM call is needed here:
the AI extracts facts, this code does the maths, so reruns are identical.

Run: python scoring.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
BLOCKING_FLAGS = {"embedded_instruction", "timeline_missing"}


def clamp(x):
    return max(0.0, min(100.0, x))


def mandatory_failures(p):
    out = []
    if not p["licence"]:
        out.append("no licence held by bidder")
    if not (p["wsib"] and p["insurance_5m"]):
        out.append("WSIB / $5M insurance not both confirmed")
    return out


def subscores(p, c):
    s = c["scales"]
    exp = clamp(p["qualifying_installs"] / s["experience_full_marks_at_installs"] * 100)
    full_under = s["price_full_marks_at_pct_under_ceiling"] / 100 * c["budget_ceiling"]
    price = clamp((c["budget_ceiling"] - p["price"]) / full_under * 100)
    if p["weeks"] is None or p["weeks"] > c["max_weeks"]:
        timeline = 0.0
    else:
        timeline = clamp((c["max_weeks"] - p["weeks"]) /
                         (c["max_weeks"] - s["timeline_full_marks_at_weeks"]) * 100)
    warranty = (clamp(p["panel_years"] / s["panel_warranty_full_marks_years"] * 100) +
                clamp(p["workmanship_years"] / s["workmanship_warranty_full_marks_years"] * 100)) / 2
    team = 25 * sum([p["named_lead"], p["crew"], p["safety_plan"], p["monitoring_plan"]])
    return {"experience": exp, "price": price, "timeline": timeline,
            "warranty": warranty, "team": team}


def total(sub, c):
    return sum(sub[k] * c["weights"][k] for k in sub) / 100


def main():
    c = json.loads((HERE / "criteria.json").read_text())
    data = json.loads((HERE / "extracted.json").read_text())
    rows = []
    for name, p in data.items():
        fails = mandatory_failures(p)
        sub = subscores(p, c)
        t = round(total(sub, c), 1)
        blocking = set(p["flags"]) & BLOCKING_FLAGS
        if p["price"] > c["budget_ceiling"]:
            blocking.add("over_budget")
        if fails:
            status = "ineligible"
        elif blocking:
            status = "flagged"
        else:
            status = "ranked"
        rows.append((name, status, t, fails, sorted(blocking), sub))
    ranked = sorted([r for r in rows if r[1] == "ranked"], key=lambda r: -r[2])
    print(f"{'Prop':<5}{'Status':<12}{'Rank':<6}{'Total':<8}Notes")
    for i, r in enumerate(ranked, 1):
        print(f"{r[0]:<5}{r[1]:<12}{i:<6}{r[2]:<8}")
    for r in rows:
        if r[1] != "ranked":
            print(f"{r[0]:<5}{r[1]:<12}{'-':<6}{r[2]:<8}(provisional, not ranked) {r[3] or r[4]}")
    print("\nSub-scores (0-100):")
    for r in rows:
        print(r[0], {k: round(v, 1) for k, v in r[5].items()})


if __name__ == "__main__":
    main()
