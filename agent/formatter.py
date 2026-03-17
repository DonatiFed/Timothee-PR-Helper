"""Format agent outputs into the submission document."""

from __future__ import annotations

import json
from datetime import datetime


def _json_block(data: dict | list, label: str = "") -> str:
    header = f"### {label}\n" if label else ""
    return f"{header}```json\n{json.dumps(data, indent=2)}\n```\n"


def _draft_section(drafts: list[dict], phase_label: str) -> str:
    lines = [f"### {phase_label} — Drafted Responses\n"]
    for i, d in enumerate(drafts, 1):
        target = d.get("target", "unknown")
        recipient = d.get("recipient_name", "")
        content = d.get("content", "")
        wc = d.get("word_count", len(content.split()))
        approval = d.get("approval_required_from", "")
        rationale = d.get("rationale", "")
        deadline = d.get("deadline", "—")

        lines.append(f"**{i}. To: {recipient}** ({target})")
        lines.append(f"- **Deadline:** {deadline}")
        lines.append(f"- **Approval:** {approval}")
        lines.append(f"- **Word count:** {wc}")
        lines.append(f"\n> {content}\n")
        lines.append(f"*Rationale: {rationale}*\n")
    return "\n".join(lines)


def _timeline_section(timeline: list[dict], phase_label: str) -> str:
    lines = [f"### {phase_label} — Action Timeline\n"]
    lines.append("| Time | Action | Owner | Status | Depends On |")
    lines.append("|------|--------|-------|--------|------------|")
    for item in timeline:
        lines.append(
            f"| {item.get('time', '')} | {item.get('action', '')} | "
            f"{item.get('owner', '')} | {item.get('status', '')} | "
            f"{item.get('depends_on', '—') or '—'} |"
        )
    return "\n".join(lines)


def format_submission(phase1: dict, phase2: dict) -> str:
    """Build the full submission markdown document."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sections = []

    sections.append("# Crisis-Response Agent — Submission Output")
    sections.append(f"\n*Generated: {now}*\n")
    sections.append("---\n")

    # ── Phase 1 ──────────────────────────────────────────────────────
    sections.append("## Phase 1 — The Clip Breaks\n")

    sections.append("### Triage Assessment\n")
    t = phase1["triage"]
    sections.append(f"**Severity:** {t.get('severity', 'unknown').upper()}\n")
    sections.append(f"**Reasoning:** {t.get('reasoning', '')}\n")
    if t.get("immediate_actions"):
        sections.append("**Immediate actions:**")
        for a in t["immediate_actions"]:
            sections.append(f"- {a}")
    if t.get("risks"):
        sections.append("\n**Risks:**")
        for r in t["risks"]:
            sections.append(f"- {r}")
    if t.get("stakeholder_priorities"):
        sections.append("\n**Stakeholder priorities (by urgency):**")
        for s in t["stakeholder_priorities"]:
            sections.append(f"1. {s}")
    sections.append("")

    sections.append(_draft_section(phase1["drafts"], "Phase 1"))
    sections.append("")

    sections.append(_timeline_section(phase1["timeline"], "Phase 1"))
    sections.append("")

    d = phase1["decision"]
    sections.append("### Phase 1 — Hold / Speak Decision\n")
    sections.append(f"**Decision:** {d.get('decision', 'unknown').upper()}\n")
    sections.append(f"**Rationale:** {d.get('rationale', '')}\n")
    if d.get("conditions"):
        sections.append("**Conditions:**")
        for c in d["conditions"]:
            sections.append(f"- {c}")
    sections.append(f"\n**Channel:** {d.get('recommended_channel', '—')}")
    sections.append(f"**Timing:** {d.get('timing', '—')}\n")

    sections.append("---\n")

    # ── Phase 2 ──────────────────────────────────────────────────────
    sections.append("## Phase 2 — Sponsor Escalation\n")
    sections.append(f"*{phase2.get('phase2_note', 'Phase 2 produced after Phase 1.')}*\n")
    sections.append(f"**What changed:** {phase2.get('what_changed', '')}\n")

    if phase2.get("updated_triage"):
        ut = phase2["updated_triage"]
        sections.append("### Updated Triage\n")
        sections.append(f"**Severity:** {ut.get('severity', '').upper()}\n")
        sections.append(f"**Reasoning:** {ut.get('reasoning', '')}\n")
        if ut.get("immediate_actions"):
            sections.append("**Immediate actions:**")
            for a in ut["immediate_actions"]:
                sections.append(f"- {a}")
        if ut.get("risks"):
            sections.append("\n**Risks:**")
            for r in ut["risks"]:
                sections.append(f"- {r}")
        sections.append("")

    if phase2.get("updated_drafts"):
        sections.append(_draft_section(phase2["updated_drafts"], "Phase 2"))
        sections.append("")

    if phase2.get("updated_timeline"):
        sections.append(_timeline_section(phase2["updated_timeline"], "Phase 2"))
        sections.append("")

    if phase2.get("updated_decision"):
        ud = phase2["updated_decision"]
        sections.append("### Phase 2 — Updated Hold / Speak Decision\n")
        sections.append(f"**Decision:** {ud.get('decision', '').upper()}\n")
        sections.append(f"**Rationale:** {ud.get('rationale', '')}\n")
        if ud.get("conditions"):
            sections.append("**Conditions:**")
            for c in ud["conditions"]:
                sections.append(f"- {c}")
        sections.append(f"\n**Channel:** {ud.get('recommended_channel', '—')}")
        sections.append(f"**Timing:** {ud.get('timing', '—')}\n")

    sections.append("---\n")

    # ── Workflow Proof Block ─────────────────────────────────────────
    sections.append("## Workflow Proof Block\n")
    sections.append("This section documents the agent pipeline stages and their outputs.\n")
    sections.append("### Pipeline stages executed\n")
    sections.append("1. **INTAKE** — Parsed packet markdown into structured data")
    sections.append("2. **TRIAGE** — LLM-assessed severity, risks, stakeholder priorities")
    sections.append("3. **DRAFT** — LLM-generated stakeholder responses with voice constraints")
    sections.append("4. **SEQUENCE** — LLM-produced minute-by-minute action timeline")
    sections.append("5. **DECIDE** — LLM hold/speak recommendation with conditions")
    sections.append("6. **ADAPT** (Phase 2) — LLM-revised plan preserving Phase 1 actions\n")

    sections.append("### Raw triage → final triage comparison\n")
    sections.append("**Phase 1 triage severity:** " + phase1["triage"].get("severity", ""))
    sections.append("**Phase 2 triage severity:** " + phase2.get("updated_triage", {}).get("severity", ""))
    sections.append("")

    # ── Raw-to-final reporter reply pair ─────────────────────────────
    sections.append("### Raw-to-final reporter reply pair\n")
    # Find reporter drafts in both phases
    p1_reporter = next(
        (d for d in phase1["drafts"] if d.get("target") == "reporter"), None
    )
    p2_reporter = next(
        (d for d in phase2.get("updated_drafts", []) if d.get("target") == "reporter"),
        p1_reporter,
    )
    if p1_reporter:
        sections.append("**Phase 1 (initial draft):**")
        sections.append(f"> {p1_reporter.get('content', '')}\n")
    if p2_reporter and p2_reporter != p1_reporter:
        sections.append("**Phase 2 (updated after escalation):**")
        sections.append(f"> {p2_reporter.get('content', '')}\n")
    elif p1_reporter:
        sections.append("*Reporter reply unchanged in Phase 2 — no new facts emerged.*\n")

    sections.append("### Human edit disclosure\n")
    sections.append(
        "All outputs in this document were generated by the crisis-response "
        "agent pipeline. No manual edits were applied to the generated text. "
        "A human PR lead should review all outward-facing language before "
        "sending.\n"
    )

    sections.append("---\n")

    # ── Raw JSON appendix ────────────────────────────────────────────
    sections.append("## Appendix — Raw JSON Outputs\n")
    sections.append(
        "<details><summary>Click to expand Phase 1 raw JSON</summary>\n"
    )
    sections.append(_json_block({
        "triage": phase1["triage"],
        "drafts": phase1["drafts"],
        "timeline": phase1["timeline"],
        "decision": phase1["decision"],
    }, "Phase 1 Raw"))
    sections.append("</details>\n")

    sections.append(
        "<details><summary>Click to expand Phase 2 raw JSON</summary>\n"
    )
    sections.append(_json_block({
        "updated_triage": phase2.get("updated_triage"),
        "updated_drafts": phase2.get("updated_drafts"),
        "updated_timeline": phase2.get("updated_timeline"),
        "updated_decision": phase2.get("updated_decision"),
        "what_changed": phase2.get("what_changed"),
    }, "Phase 2 Raw"))
    sections.append("</details>\n")

    return "\n".join(sections)
