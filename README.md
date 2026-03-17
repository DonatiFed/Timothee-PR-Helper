# Timothée Crisis-Response Agent

An AI-powered crisis-response agent for celebrity PR teams. Built for the **"Timothée vs. Opera/Ballet" challenge** — handles fast-moving backlash events with structured triage, multi-stakeholder coordination, and adaptive replanning.

Powered by **Claude (Opus 4)** via the Anthropic API.

## What it does

The agent runs a **5-stage LLM pipeline**, processing crisis packets (markdown) and producing a complete, actionable PR plan:

| Stage | What it does | Output |
|-------|-------------|--------|
| **INTAKE** | Parses packet markdown into structured data | `CrisisContext` (talent, timeline, stakeholders, constraints) |
| **TRIAGE** | Assesses severity, identifies risks, orders stakeholder priorities | `TriageResult` (severity, risks, actions, priority list) |
| **DRAFT** | Generates stakeholder-specific responses with voice/tone constraints | 4+ drafts (sponsor, reporter, manager, public statement) |
| **SEQUENCE** | Builds a minute-by-minute action timeline with approval gates | Ordered `ActionItem` list with owners, statuses, dependencies |
| **DECIDE** | Makes the hold/speak recommendation with conditions | `hold`, `speak`, or `conditional_speak` + rationale |

For **Phase 2 escalations** (e.g. sponsor ultimatum), the agent runs an **ADAPT** stage that updates the existing plan without restarting — preserving actions already taken while addressing new pressure.

## How it works

Each pipeline stage calls Claude with a focused system prompt and the accumulated context from prior stages. This keeps calls scoped, auditable, and easy to review. The regex-based parser generalizes to any packet following the same markdown structure (headings, blockquotes, bullet lists, timing metadata, voicemail signals).

**Pipeline flow:**
```
Packet A (markdown) → INTAKE → TRIAGE → DRAFT → SEQUENCE → DECIDE → Phase 1 plan
Packet B (markdown) → ADAPT(Phase 1 plan) → Phase 2 plan (updated, not restarted)
Both plans → FORMATTER → output/submission.md
```

## Quick start

```bash
# 1. Clone & install
git clone <repo-url> && cd Timothee-PR-Helper
pip install -r requirements.txt

# 2. Set up your API key
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY

# 3. Run the full pipeline (Phase 1 + Phase 2)
python run.py -v

# 4. Review output
cat output/submission.md
```

**Requirements:** Python 3.10+, an [Anthropic API key](https://console.anthropic.com/).

## Usage

```bash
# Full run (both phases, default packets)
python run.py

# Phase 1 only
python run.py --phase1-only

# Custom packets (for unseen evaluation inputs)
python run.py --packet-a path/to/new_packet_a.md --packet-b path/to/new_packet_b.md

# Verbose mode (prints each pipeline stage as it runs)
python run.py -v

# Custom output location
python run.py -o output/my_submission.md
```

### Running on unseen inputs

The pipeline is designed to generalize. To test with new crisis packets:

```bash
python run.py --packet-a new_crisis_a.md --packet-b new_crisis_b.md -v
```

The parser extracts talent name, scenario time, stakeholder messages, deadlines, and voicemail signals from any markdown following the same heading/blockquote structure as the published packets.

## Running tests

```bash
# Parser unit tests (no API key needed — 32 tests)
python -m pytest tests/test_parser.py -v

# Synthetic scenario parser tests (no API key needed — 8 tests)
python -m pytest tests/test_scenarios.py::TestSyntheticParserOnly -v

# All offline tests
python -m pytest tests/test_parser.py tests/test_scenarios.py::TestSyntheticParserOnly -v

# Integration tests against published packets (requires API key)
python -m pytest tests/test_integration.py -v

# Full synthetic scenario tests (requires API key)
python -m pytest tests/test_scenarios.py -v

# Run a synthetic scenario through the full pipeline manually
python run.py --packet-a test_scenarios/scenario_1_packet_a.md \
              --packet-b test_scenarios/scenario_1_packet_b.md -v
```

## Project structure

```
├── run.py                      # CLI entry point (--packet-a, --packet-b, --phase1-only, -v)
├── agent/
│   ├── models.py               # Dataclasses: CrisisContext, TriageResult, DraftResponse, ActionItem, CrisisPlan
│   ├── parser.py               # Regex-based markdown parser — extracts structured data from any packet
│   ├── engine.py               # Claude API wrapper — system prompts for each pipeline stage
│   ├── pipeline.py             # Orchestrator: run_phase1() and run_phase2()
│   └── formatter.py            # Generates submission.md from pipeline outputs
├── challenge_docs/             # Challenge inputs (published)
│   ├── packet_a.md             # Phase 1 — "The clip breaks" (5:30 PM scenario)
│   ├── packet_b.md             # Phase 2 — "Sponsor escalation" (6:15 PM scenario)
│   └── challenge_brief.md      # Challenge rules, scoring rubric, and constraints
├── test_scenarios/             # Synthetic crisis packets for generalization testing
│   ├── scenario_1_packet_a.md  # Elara Voss — environmental hypocrisy video
│   ├── scenario_1_packet_b.md  #   └── sponsor threatens to pull nature campaign
│   ├── scenario_2_packet_a.md  # Marcus Bell — deleted tweet mocking classical music
│   ├── scenario_2_packet_b.md  #   └── sponsor ultimatum over brand values
│   ├── scenario_3_packet_a.md  # Camille Fontaine — disability mockery photo
│   └── scenario_3_packet_b.md  #   └── dual sponsor escalation (Lumière + Maison Étoile)
├── tests/
│   ├── conftest.py             # Auto-skips API-dependent tests when no key is set
│   ├── test_parser.py          # 32 parser unit tests (no API key needed)
│   ├── test_integration.py     # Full pipeline tests against published packets
│   └── test_scenarios.py       # Synthetic scenario tests (4 scenarios × parser + pipeline)
├── output/                     # Generated outputs (included in repo for review)
│   ├── submission.md           # Main submission — Phase 1 + Phase 2 + workflow proof
│   └── raw_output.json         # Full raw JSON from all pipeline stages
├── .env.example                # Template: ANTHROPIC_API_KEY and CLAUDE_MODEL
├── .gitignore
└── requirements.txt            # anthropic, python-dotenv, pytest
```

## Design decisions

- **One LLM call per stage** — Each stage has its own system prompt. Outputs are JSON, making them auditable, chainable, and easy to debug or override individually.
- **Parser generalizes by design** — Uses regex patterns against markdown structure (headings, blockquotes, bullet lists, timestamps), not hardcoded content. Works on any packet following the same format.
- **3 synthetic test scenarios** — Three completely different crisis scenarios (Elara Voss / environment, Marcus Bell / classical music, Camille Fontaine / disability) each with Packet A + B pairs prove the pipeline handles unseen inputs. A fourth inline scenario (Maya Santos / theater) is embedded in the test suite.
- **Phase 2 updates, never restarts** — The ADAPT stage receives the full Phase 1 plan and must preserve completed actions, only adding or modifying what the escalation requires.
- **Voice constraints enforced at draft time** — The DRAFT system prompt embeds all voice/tone guidelines (word limits, no jargon, empathetic but not defensive) so every response is on-brand before human review.
- **Approval gates in timeline** — The SEQUENCE stage models who must approve what and when, with `ready → pending → blocked` status tracking and explicit dependency chains.
- **Hold/speak decision with conditions** — The DECIDE stage doesn't just recommend; it specifies what conditions must be met, which channel to use, and exact timing.

## Output

Running `python run.py` produces `output/submission.md` containing:

| Section | Description |
|---------|-------------|
| Phase 1 — Triage | Severity assessment, risks, stakeholder priorities |
| Phase 1 — Drafted Responses | Sponsor holding line, reporter reply, manager guidance, public statement |
| Phase 1 — Action Timeline | Minute-by-minute plan with owners, statuses, dependencies |
| Phase 1 — Hold/Speak Decision | Recommendation with conditions and timing |
| Phase 2 — Updated Plan | Revised triage, new drafts (e.g. sponsor response package), compressed timeline |
| Phase 2 — Updated Decision | Escalated recommendation reflecting new pressure |
| Workflow Proof Block | Pipeline stages executed, raw→final triage comparison |
| Reporter Reply Pair | Raw Phase 1 draft vs. final (shows what changed or didn't) |
| Human Edit Disclosure | States no manual edits were applied to generated text |
| Appendix — Raw JSON | Full JSON outputs from every pipeline stage |


