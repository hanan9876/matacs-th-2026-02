# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** Hanan Arshad
- **Reference:** MATACS-TH-2026-02
- **Time actually spent:** about 60 minutes

## Files

| File | What it is |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions (under 1,000 words) |
| [diagram/flow.png](diagram/flow.png) | Process flow from upload to ranked output, showing AI steps, rule steps and human checkpoints |
| [PROMPTS.md](PROMPTS.md) | The extraction prompt and the reason-writing prompt, as I would send them |
| [ranking.json](ranking.json) | Expected ranking of proposals A–E |
| [prototype/](prototype/) | Optional. A small script that applies the scoring step to extracted facts |

### Prototype

`prototype/scoring.py` reads `prototype/extracted.json` (facts per proposal, as the extraction step would return them) and `prototype/criteria.json` (admin settings), then applies the mandatory gates, flags and weighted scoring. It makes no AI call, which is deliberate: only extraction and the explanation use AI, and the scoring is plain code so reruns are identical. No API keys are used, so no `.env.example` is needed.

```
cd prototype
python scoring.py
```

Output matches `ranking.json`: A 73.5, E 60.9, B ineligible, C flagged, D flagged.

## How I used AI tools

I used Claude to help draft the extraction and reason-writing prompts, build the scoring script, draw the flow diagram and tidy the write-up. I corrected its output in two places: its first write-up draft was about 1,200 words, over the 1,000-word limit, so I had it cut to under 900; and its first diagram had a legend overlapping step 1 and an arrow that wrongly linked the ineligible box to the flagged box, so I had both fixed. I also checked the scoring by hand (for example A = 73.5) before trusting the script, and kept all scoring in plain code rather than letting the AI assign scores, because AI scores are not repeatable.

## Notes

- Proposals are referred to by letter only; the brief and the sample text are not copied here.
- Scoring scales (such as full marks at 12 installs) are my own defaults and would be editable by the admin.
