"""Orchestrates the full crisis-response pipeline across Phase 1 and Phase 2.

Usage:
    from agent.pipeline import run_phase1, run_phase2

    p1 = run_phase1("path/to/packet_a.md")
    p2 = run_phase2(p1, "path/to/packet_b.md")
"""

from __future__ import annotations

import json
from pathlib import Path

from agent.parser import parse_packet
from agent.engine import (
    run_triage,
    run_drafting,
    run_sequencing,
    run_decision,
    run_adaptation,
)


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _build_context_summary(parsed: dict) -> str:
    """Build a concise textual summary for LLM context windows."""
    lines = []
    lines.append(f"TALENT: {parsed['talent_name']}")
    lines.append(f"SCENARIO TIME: {parsed['scenario_time']}")
    if parsed["situation_summary"]:
        lines.append(f"SITUATION: {parsed['situation_summary']}")
    if parsed["clip_description"]:
        lines.append(f"CLIP: {parsed['clip_description']}")
    if parsed["known_limits"]:
        lines.append("KNOWN LIMITS:")
        for lim in parsed["known_limits"]:
            lines.append(f"  - {lim}")
    if parsed["timing_constraints"]:
        lines.append("TIMING CONSTRAINTS:")
        for tc in parsed["timing_constraints"]:
            lines.append(f"  - {tc}")
    if parsed["voice_guidelines"]:
        vg = parsed["voice_guidelines"]
        if vg.get("aim_for"):
            lines.append("VOICE — AIM FOR: " + "; ".join(vg["aim_for"]))
        if vg.get("do_not"):
            lines.append("VOICE — DO NOT: " + "; ".join(vg["do_not"]))
    if parsed["inbound_messages"]:
        lines.append("INBOUND MESSAGES:")
        for msg in parsed["inbound_messages"]:
            sender = msg.sender if hasattr(msg, "sender") else msg.get("sender", "")
            content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            priority = msg.priority if hasattr(msg, "priority") else msg.get("priority", "")
            lines.append(f"  [{priority}] {sender}: {content}")
    if parsed.get("escalation_details"):
        lines.append("ESCALATION:")
        for ed in parsed["escalation_details"]:
            lines.append(f"  - {ed}")
    if parsed.get("voicemail_signals"):
        lines.append("VOICEMAIL SIGNALS:")
        for vm in parsed["voicemail_signals"]:
            lines.append(f"  - {vm['sender']} (received {vm['received']}, {vm['duration']})")
    return "\n".join(lines)


def _build_escalation_summary(parsed: dict) -> str:
    """Build a summary focused on the escalation for Phase 2."""
    lines = [_build_context_summary(parsed)]
    lines.append("\nESCALATION NOTE: This is a stakeholder-pressure update, not a fact update.")
    lines.append("No new factual evidence about the original clip has emerged.")
    return "\n".join(lines)


def run_phase1(packet_a_path: str, *, verbose: bool = False) -> dict:
    """Run the full Phase 1 pipeline on a Packet A style file.

    Returns a dict with all intermediate + final outputs.
    """
    log = print if verbose else (lambda *a, **k: None)

    log("📄 Parsing packet...")
    raw_md = _read(packet_a_path)
    parsed = parse_packet(raw_md)
    context_summary = _build_context_summary(parsed)

    log("🔍 Running triage...")
    triage = run_triage(context_summary)
    triage_json = json.dumps(triage, indent=2)
    log(f"   Severity: {triage.get('severity', 'unknown')}")

    log("✏️  Drafting stakeholder responses...")
    drafts = run_drafting(triage_json, context_summary)
    drafts_json = json.dumps(drafts, indent=2)
    log(f"   Drafted {len(drafts)} response(s)")

    log("📅 Sequencing actions...")
    timeline = run_sequencing(triage_json, drafts_json, context_summary)
    timeline_json = json.dumps(timeline, indent=2)
    log(f"   {len(timeline)} action(s) sequenced")

    log("⚖️  Making hold/speak decision...")
    decision = run_decision(triage_json, drafts_json, timeline_json)
    log(f"   Decision: {decision.get('decision', 'unknown')}")

    phase1_plan = {
        "phase": "Phase 1",
        "context_summary": context_summary,
        "triage": triage,
        "drafts": drafts,
        "timeline": timeline,
        "decision": decision,
        "parsed_packet": {
            k: v for k, v in parsed.items()
            if k not in ("inbound_messages", "raw_markdown")
        },
    }

    log("✅ Phase 1 complete.")
    return phase1_plan


def run_phase2(phase1_plan: dict, packet_b_path: str, *, verbose: bool = False) -> dict:
    """Run Phase 2 adaptation on a Packet B style escalation file.

    Takes the Phase 1 plan and updates it — does NOT restart from scratch.
    """
    log = print if verbose else (lambda *a, **k: None)

    log("\n── Phase 2: Escalation ──")
    log("📄 Parsing escalation packet...")
    raw_md = _read(packet_b_path)
    parsed_b = parse_packet(raw_md)
    escalation_summary = _build_escalation_summary(parsed_b)

    phase1_json = json.dumps({
        "triage": phase1_plan["triage"],
        "drafts": phase1_plan["drafts"],
        "timeline": phase1_plan["timeline"],
        "decision": phase1_plan["decision"],
    }, indent=2)

    log("🔄 Adapting plan to escalation...")
    adapted = run_adaptation(phase1_json, escalation_summary)

    phase2_plan = {
        "phase": "Phase 2",
        "phase2_note": "This Phase 2 plan was produced after completing Phase 1.",
        "escalation_summary": escalation_summary,
        "updated_triage": adapted.get("updated_triage", {}),
        "updated_drafts": adapted.get("updated_drafts", []),
        "updated_timeline": adapted.get("updated_timeline", []),
        "updated_decision": adapted.get("updated_decision", {}),
        "what_changed": adapted.get("what_changed", ""),
        "phase1_plan": phase1_plan,
    }

    log("✅ Phase 2 complete.")
    return phase2_plan
