"""Parse packet markdown files into structured CrisisContext objects.

This parser is designed to generalize to any packet following the same
markdown structure as Packet A / Packet B — headings, blockquotes,
bullet lists, and timing metadata.
"""

from __future__ import annotations

import re
from typing import Optional

from agent.models import (
    CrisisContext,
    InboundMessage,
    MessagePriority,
    StakeholderType,
)


def _classify_stakeholder(sender_block: str) -> StakeholderType:
    lower = sender_block.lower()
    if "sponsor" in lower or "partnership" in lower or "brand" in lower:
        return StakeholderType.SPONSOR
    if "reporter" in lower or "journalist" in lower or "press" in lower:
        return StakeholderType.REPORTER
    if "manager" in lower:
        return StakeholderType.MANAGER
    return StakeholderType.PUBLIC


def _extract_deadline(text: str) -> Optional[str]:
    match = re.search(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b", text)
    return match.group(1) if match else None


def _estimate_priority(stakeholder: StakeholderType, text: str) -> MessagePriority:
    urgent_signals = ["escalat", "pause", "hold", "cancel", "immediately", "urgent",
                      "within the next", "precautionary"]
    text_lower = text.lower()
    if any(s in text_lower for s in urgent_signals):
        return MessagePriority.IMMEDIATE
    if stakeholder in (StakeholderType.SPONSOR, StakeholderType.MANAGER):
        return MessagePriority.URGENT
    if stakeholder == StakeholderType.REPORTER:
        return MessagePriority.STANDARD
    return MessagePriority.LOW


def parse_packet(markdown: str) -> dict:
    """Parse a packet markdown file and return a structured dict.

    Returns a dict with keys that map onto CrisisContext + extra escalation
    fields so both Packet A and Packet B style files work.
    """
    result: dict = {
        "talent_name": "",
        "scenario_time": "",
        "situation_summary": "",
        "clip_description": "",
        "known_facts": [],
        "known_limits": [],
        "timing_constraints": [],
        "voice_guidelines": {"aim_for": [], "do_not": []},
        "inbound_messages": [],
        "escalation_details": [],
        "voicemail_signals": [],
        "raw_markdown": markdown,
    }

    # Extract talent name
    talent_match = re.search(r"\*\*Talent:\*\*\s*(.+)", markdown)
    if talent_match:
        result["talent_name"] = talent_match.group(1).strip()

    # Extract scenario time
    time_match = re.search(r"\*\*Scenario time:\*\*\s*(.+)", markdown)
    if time_match:
        result["scenario_time"] = time_match.group(1).strip()

    # Extract situation paragraph (first paragraph under ## Situation)
    sit_match = re.search(r"## Situation\s*\n\n(.+?)(?:\n\n|\n##)", markdown, re.DOTALL)
    if sit_match:
        result["situation_summary"] = sit_match.group(1).strip()

    # Extract clip description
    clip_match = re.search(
        r"## Viral clip\s*\n\n(.+?)(?:\n\n(?:Known limits|##))", markdown, re.DOTALL
    )
    if clip_match:
        result["clip_description"] = clip_match.group(1).strip()

    # Known limits as bullet list
    limits_match = re.search(r"Known limits:\s*\n((?:- .+\n?)+)", markdown)
    if limits_match:
        result["known_limits"] = [
            line.lstrip("- ").strip()
            for line in limits_match.group(1).strip().split("\n")
            if line.strip()
        ]

    # Timing constraints — grab bullet lists under ## Timing
    timing_match = re.search(
        r"## Timing and approvals\s*\n\n((?:- .+\n?)+)", markdown
    )
    if timing_match:
        result["timing_constraints"] = [
            line.lstrip("- ").strip()
            for line in timing_match.group(1).strip().split("\n")
            if line.strip()
        ]

    # Voice guidelines
    aim_match = re.search(r"Aim for:\s*\n((?:- .+\n?)+)", markdown)
    if aim_match:
        result["voice_guidelines"]["aim_for"] = [
            line.lstrip("- ").strip()
            for line in aim_match.group(1).strip().split("\n")
            if line.strip()
        ]
    donot_match = re.search(r"Do not:\s*\n((?:- .+\n?)+)", markdown)
    if donot_match:
        result["voice_guidelines"]["do_not"] = [
            line.lstrip("- ").strip()
            for line in donot_match.group(1).strip().split("\n")
            if line.strip()
        ]

    # Inbound messages — find ### blocks under ## Inbound messages
    # Also handle ## Sponsor escalation message and ## Additional inbound voicemails
    inbound_blocks = re.findall(
        r"###\s+(.+?)(?:\n\n?)(>[\s\S]*?)(?=\n###|\n##|\Z)", markdown
    )
    for sender_line, body in inbound_blocks:
        body_clean = "\n".join(
            line.lstrip("> ").strip() for line in body.strip().split("\n")
        ).strip()
        if not body_clean:
            continue
        stakeholder = _classify_stakeholder(sender_line)
        msg = InboundMessage(
            sender=sender_line.strip(),
            stakeholder_type=stakeholder,
            timestamp=_extract_deadline(sender_line) or result["scenario_time"],
            content=body_clean,
            priority=_estimate_priority(stakeholder, body_clean),
            requires_response_by=_extract_deadline(body_clean),
        )
        result["inbound_messages"].append(msg)

    # Voicemail signals (Packet B style — ### blocks with MP3 links)
    vm_blocks = re.findall(
        r"###\s+(.+?)\n\*\*Received:\*\*\s*(.+?)\n\*\*Duration:\*\*\s*(.+?)\n\*\*MP3:\*\*\s*(.+?)(?:\n|$)",
        markdown,
    )
    for name, received, duration, mp3_link in vm_blocks:
        result["voicemail_signals"].append({
            "sender": name.strip(),
            "received": received.strip(),
            "duration": duration.strip(),
            "mp3_link": mp3_link.strip(),
        })

    # Escalation-specific content (## What changed)
    changed_match = re.search(
        r"## What changed\s*\n\n((?:- .+\n?)+)", markdown
    )
    if changed_match:
        result["escalation_details"] = [
            line.lstrip("- ").strip()
            for line in changed_match.group(1).strip().split("\n")
            if line.strip()
        ]

    return result


def packet_to_context(parsed: dict) -> CrisisContext:
    """Convert parsed packet dict to a CrisisContext model."""
    return CrisisContext(
        talent_name=parsed["talent_name"],
        scenario_time=parsed["scenario_time"],
        situation_summary=parsed["situation_summary"],
        clip_description=parsed["clip_description"],
        known_facts=parsed.get("known_facts", []),
        known_limits=parsed.get("known_limits", []),
        timing_constraints=parsed.get("timing_constraints", []),
        voice_guidelines=parsed.get("voice_guidelines", {}),
        inbound_messages=parsed.get("inbound_messages", []),
    )
