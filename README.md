# Timothée Crisis-Response Agent

An AI-powered crisis-response agent for celebrity PR teams. Built for the "Timothée vs. Opera/Ballet" challenge — handles fast-moving backlash events with structured triage, multi-stakeholder coordination, and adaptive replanning.

## What it does

The agent runs a **5-stage pipeline** powered by Claude, processing crisis packets and producing actionable PR plans:

1. **INTAKE** — Parses packet markdown into structured data (talent, timeline, stakeholders, constraints)
2. **TRIAGE** — Assesses severity, identifies risks, orders stakeholder priorities
3. **DRAFT** — Generates stakeholder-specific responses (sponsor holding lines, reporter replies, talent statements) with voice/tone constraints
4. **SEQUENCE** — Builds a minute-by-minute action timeline with approval gates
5. **DECIDE** — Makes the hold/speak recommendation with conditions

For **Phase 2 escalations**, the agent runs an **ADAPT** stage that updates the existing plan without restarting — preserving actions already taken while addressing new pressure.

## How it works

Each pipeline stage calls Claude with a focused system prompt and accumulated context. This keeps calls scoped, auditable, and easy to review. The parser generalizes to any packet following the same markdown structure (headings, blockquotes, bullet lists, timing metadata, voicemail signals).

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your API key
cp .env.example .env
# Edit .env and add your Anthropic API key

# 3. Run the full pipeline (Phase 1 + Phase 2)
python run.py -v

# 4. Check output
cat output/submission.md
```

## Usage

```bash
# Full run (both phases)
python run.py

# Phase 1 only
python run.py --phase1-only

# Custom packets (for unseen evaluation inputs)
python run.py --packet-a path/to/new_packet_a.md --packet-b path/to/new_packet_b.md

# Verbose mode
python run.py -v

# Custom output location
python run.py -o output/my_submission.md
```

## Running tests

```bash
# Unit tests (no API key needed)
python -m pytest tests/test_parser.py -v

# Integration tests (requires API key)
python -m pytest tests/test_integration.py -v

# Scenario tests with synthetic packets
python -m pytest tests/test_scenarios.py -v
```

## Project structure

```
├── run.py                  # Main entry point
├── agent/
│   ├── models.py           # Data models (CrisisContext, TriageResult, etc.)
│   ├── parser.py           # Packet markdown parser
│   ├── engine.py           # Claude API calls for each pipeline stage
│   ├── pipeline.py         # Orchestrator (run_phase1, run_phase2)
│   └── formatter.py        # Submission document generator
├── tests/
│   ├── test_parser.py      # Parser unit tests
│   ├── test_integration.py # Full pipeline integration tests
│   └── test_scenarios.py   # Synthetic scenario tests
├── packet_a.md             # Phase 1 scenario inputs
├── packet_b.md             # Phase 2 escalation inputs
├── challenge_brief.md      # Challenge rules and scoring
├── .env.example            # API key template
├── .gitignore
└── requirements.txt
```

## Design decisions

- **Modular pipeline** — Each stage is a separate LLM call with its own system prompt. This makes outputs auditable and easy to debug/override.
- **Structured JSON outputs** — Every stage returns JSON, making it easy to chain stages and format the final submission.
- **Parser generalizes** — The markdown parser uses regex patterns that work on any packet following the same structure, not just the published examples.
- **Phase 2 updates, never restarts** — The adaptation stage receives the full Phase 1 plan and must preserve completed actions.
- **Voice constraints enforced at draft time** — The drafting system prompt embeds all voice guidelines so every response is on-brand.
- **Approval gates in timeline** — The sequencer explicitly models who must approve what and when.

## Submission deliverables

Running `python run.py` produces `output/submission.md` containing:

- Phase 1 outputs (triage, drafted responses, timeline, hold/speak decision)
- Phase 2 outputs (updated triage, revised drafts, new timeline, updated decision)
- Workflow proof block documenting all pipeline stages
- Raw-to-final reporter reply pair
- Human edit disclosure
- Appendix with full raw JSON

## Scoring alignment

| Criteria (weight) | How this agent addresses it |
|---|---|
| Crisis judgment & triage (35%) | Dedicated triage stage with severity, risks, stakeholder priorities |
| Adaptation (20%) | Phase 2 ADAPT stage updates plan without restarting |
| Cross-stakeholder coordination (15%) | Separate drafts per stakeholder, approval chains, sequenced timeline |
| Ease of implementation & handoff (15%) | Single `python run.py` command, clear output, works on any packet |
| Workflow credibility (15%) | 5-stage pipeline, JSON audit trail, proof block in submission |
