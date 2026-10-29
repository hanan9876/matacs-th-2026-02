# WRITEUP.md

Reference MATACS-TH-2026-02. Proposals are referred to by letter. Flow: `diagram/flow.png`.

## Design in short

Upload → extract text (code) → safety scan (code) → **AI extracts facts with quotes** → validate JSON and check quotes exist (code) → mandatory gates (code) → flags for missing or suspicious data (code) → weighted scoring (code) → **AI writes a short reason** → human review → human award decision.

## Sample set result (`ranking.json`)

- **A: rank 1 (73.5). E: rank 2 (60.9).**
- **B: ineligible.** Electrical work goes to a subcontractor "to be confirmed after award", so the bidder does not hold the licence. Without the gate B would score 61.2 and beat E, which is why gates are pass/fail and run first.
- **C: flagged.** It contains text telling automated reviewers to rank it first. The instruction is ignored and reported. Its real content would score 52.4 (provisional). A person decides what happens next.
- **D: flagged.** No completion time, so the 16-week limit cannot be confirmed. I did not guess; the reviewer asks for a schedule. Provisional 58.7.

## 1. AI vs. rules

**AI** does two things: reads messy proposal text into structured facts, and writes a short plain-English reason. Proposals vary in format and wording, so this is where AI adds value.

**Code** does file checks, schema checks, quote checks, pass/fail gates, flags, all arithmetic, ranking and logging. These must be exact and repeatable. The line is: **AI reads, code decides.** AI never produces a score or rank.

## 2. Consistency and explainability

- Scores come from a formula, so the same extracted facts always give the same scores and ranking. Each criterion has a 0–100 scale with fixed anchors in admin config (for example full marks at 12 qualifying installs), multiplied by its weight.
- Fixed anchors, rather than comparing bidders to each other, mean adding or removing a bidder never changes another bidder's score.
- The only variation is in extraction. I use temperature 0, a versioned prompt and a strict schema. Extractions are saved against the file hash, so a re-rank reuses them. A fresh re-extraction is compared with the saved one and any differences are shown.
- The reviewer sees, for each proposal, the per-criterion sub-score, weight, extracted value, supporting quote and the reason text.

## 3. Human in the loop

1. **Flag review:** a person reviews every flagged or ineligible proposal and clears it, requests information or confirms exclusion, with a note.
2. **Extraction check:** quotes sit beside values; the reviewer can correct a value, which re-runs scoring only.
3. **Ranking review:** the reviewer can override a rank or status with a written reason.
4. **Award decision:** always a person. The tool only recommends.

**Audit log (append-only):** uploader, file hashes, category and criteria version, prompt version, model and settings, raw AI output, validation results, flags, computed scores, every human edit (user, time, reason) and the final decision.

## 4. Changing criteria

- Criteria are versioned, and each scoring run stores the version used.
- An edit does **not** silently change old results; they are marked "scored under version N, criteria changed".
- Extracted facts are stored separately from scoring, so re-scoring is cheap and needs no new AI call, unless a new criterion needs a fact never extracted (then only that field is extracted).
- The reviewer compares old and new rankings and chooses. Edits need a reason and are logged. Because changing criteria after seeing bids can be unfair, the tool warns when it happens.
- Code enforces that weights total 100%.

## 5. Risks and guards

- **Wrong extraction** (e.g. counting installs under 100 kW or older than 5 years): required quotes, quote-exists check, schema validation, reviewer can correct. Unclear values become null.
- **Made-up facts:** "only what is stated, otherwise null" rule. A value without a matching quote is rejected and flagged.
- **Prompt injection** (as in C): proposal text is wrapped as data; the model cannot set scores; a code scan and a model-reported field both flag it; flagged proposals go to a human. At worst, injection could distort extracted facts, which are checked against quotes.
- **Missing or vague information** (D, B): never assumed. D is flagged; "to be confirmed" does not count as holding a licence in B.
- **Bias:** only admin-defined criteria are used, the prompt ignores company name, size and location, and a fixed formula treats all bidders alike. I would test by rewording the same proposal and checking extraction does not change.
- **Over-reliance:** the list is labelled a recommendation, flagged items are shown prominently, and a human decides.
- **Cost:** one extraction call and one short explanation call per proposal, cached by file hash, re-scoring uses no AI, and file size limits apply.
- **Confidentiality:** access-controlled storage, and a vendor agreement that excludes training on the data.

## Assumptions

- "Since 2021" is accepted as within 5 years, as no dates are given.
- Scales (12 installs, 25% under budget, 8 weeks for full marks) are my defaults, editable by the admin.
- Price is scored on the stated total only.
