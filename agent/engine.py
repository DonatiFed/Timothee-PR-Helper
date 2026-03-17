"""Core crisis-response agent engine powered by the Claude API.

Pipeline stages:
  1. INTAKE   — parse packet, build structured context
  2. TRIAGE   — assess severity, identify risks and priorities
  3. DRAFT    — produce stakeholder-specific responses
  4. SEQUENCE — build a time-ordered action plan
  5. ADAPT    — revise the plan when new packets arrive (Phase 2)

Each stage calls Claude with a focused system prompt and the accumulated
context from prior stages. This keeps each call scoped and auditable.
"""

from __future__ import annotations

import json
import os
import textwrap
from typing import Optional

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client: Optional[Anthropic] = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


def _model() -> str:
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def _call(system: str, user: str, *, max_tokens: int = 4096) -> str:
    """Single Claude API call with system + user message."""
    resp = _get_client().messages.create(
        model=_model(),
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


# ── Stage 1: Triage ──────────────────────────────────────────────────

TRIAGE_SYSTEM = textwrap.dedent("""\
    You are a senior celebrity-PR crisis analyst. Given a structured crisis
    briefing, produce a triage assessment in JSON with these exact keys:

    {
      "severity": "low|medium|high|critical",
      "reasoning": "2-3 sentence rationale",
      "immediate_actions": ["action 1", ...],
      "risks": ["risk 1", ...],
      "stakeholder_priorities": ["stakeholder: reason", ...]
    }

    Rules:
    - Use ONLY the facts provided. Do not invent transcript context.
    - Internal manager comments are internal context, not verified fact.
    - Respect every stated deadline and approval gate.
    - Stakeholder priorities must be ordered by urgency.
    Output ONLY valid JSON, no markdown fences.
""")


def run_triage(packet_summary: str) -> dict:
    raw = _call(TRIAGE_SYSTEM, packet_summary)
    # Strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    return json.loads(cleaned)


# ── Stage 2: Draft responses ─────────────────────────────────────────

DRAFT_SYSTEM = textwrap.dedent("""\
    You are a crisis-communications writer for a celebrity PR team.

    Given a triage assessment and crisis context, draft responses for each
    stakeholder who requires one. Return a JSON array of objects:

    [
      {
        "target": "sponsor|reporter|manager|public|talent",
        "recipient_name": "Name or org",
        "content": "The response text",
        "word_count": <int>,
        "approval_required_from": "who must approve before sending",
        "rationale": "why this tone/content was chosen",
        "deadline": "HH:MM PM or null"
      }
    ]

    Voice rules (apply to ALL outward-facing text):
    - Calm, self-aware, human
    - Specific without sounding over-lawyered
    - Respectful to affected audiences
    - Accountable for impact without overstating unverified facts
    - NEVER make "you misunderstood me" the whole message
    - NEVER argue with commenters or try to joke it away
    - NEVER sound condescending about ballet, opera, or "old" art
    - NEVER center awards-night excitement while backlash is active

    Constraints:
    - Sponsor holding lines must be ≤40 words unless told otherwise.
    - Any statement in talent's voice requires talent approval.
    - Manager can approve sponsor and reporter holding replies.
    - Use ONLY packet-verified facts. Manager explanations are internal only.
    - If the full context is not verified, do not claim it is.
    Output ONLY valid JSON, no markdown fences.
""")


def run_drafting(triage_json: str, context_summary: str) -> list[dict]:
    prompt = f"TRIAGE RESULT:\n{triage_json}\n\nCRISIS CONTEXT:\n{context_summary}"
    raw = _call(DRAFT_SYSTEM, prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    return json.loads(cleaned)


# ── Stage 3: Action sequencing ───────────────────────────────────────

SEQUENCE_SYSTEM = textwrap.dedent("""\
    You are a PR operations coordinator. Given a triage, drafted responses,
    and crisis context, produce a minute-by-minute action timeline.

    Return a JSON array of objects ordered by time:

    [
      {
        "time": "HH:MM PM",
        "action": "description",
        "owner": "who does this",
        "status": "pending|ready|blocked",
        "depends_on": "prior action or null"
      }
    ]

    Rules:
    - Respect all stated deadlines.
    - Include approval gates explicitly (e.g., "Manager approves sponsor line").
    - Talent approval can only happen after talent is available.
    - Include hold/monitoring actions where appropriate.
    - Output ONLY valid JSON, no markdown fences.
""")


def run_sequencing(triage_json: str, drafts_json: str, context_summary: str) -> list[dict]:
    prompt = (
        f"TRIAGE:\n{triage_json}\n\n"
        f"DRAFTED RESPONSES:\n{drafts_json}\n\n"
        f"CONTEXT:\n{context_summary}"
    )
    raw = _call(SEQUENCE_SYSTEM, prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    return json.loads(cleaned)


# ── Stage 4: Hold-or-speak decision ─────────────────────────────────

DECISION_SYSTEM = textwrap.dedent("""\
    You are a senior PR strategist. Based on the full crisis picture —
    triage, drafted responses, and timeline — make the HOLD vs. SPEAK
    decision for the talent.

    Return JSON:
    {
      "decision": "hold|speak|conditional_speak",
      "rationale": "2-4 sentence explanation",
      "conditions": ["condition for speaking, if conditional"],
      "recommended_channel": "social post|press statement|red carpet remark|none yet",
      "timing": "when to execute"
    }

    Rules:
    - Default to restraint when facts are incomplete.
    - Never recommend posting something talent hasn't approved.
    - A 'conditional_speak' means speak only if certain conditions are met.
    Output ONLY valid JSON, no markdown fences.
""")


def run_decision(triage_json: str, drafts_json: str, timeline_json: str) -> dict:
    prompt = (
        f"TRIAGE:\n{triage_json}\n\n"
        f"DRAFTS:\n{drafts_json}\n\n"
        f"TIMELINE:\n{timeline_json}"
    )
    raw = _call(DECISION_SYSTEM, prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    return json.loads(cleaned)


# ── Stage 5: Adaptation (Phase 2) ───────────────────────────────────

ADAPT_SYSTEM = textwrap.dedent("""\
    You are a senior PR crisis manager handling a PHASE 2 ESCALATION.

    You already have a Phase 1 plan. New information has arrived. You must
    UPDATE the existing plan — do not restart from scratch.

    Given:
    - The Phase 1 plan (triage, drafts, timeline, decision)
    - The new escalation packet

    Produce a COMPLETE updated plan as JSON:
    {
      "updated_triage": { same schema as triage },
      "updated_drafts": [ same schema as drafts array ],
      "updated_timeline": [ same schema as timeline array ],
      "updated_decision": { same schema as decision },
      "what_changed": "1-3 sentence summary of what changed and why",
      "phase2_note": "This Phase 2 plan was produced after completing Phase 1."
    }

    Rules:
    - This is a stakeholder-pressure update, not a fact update.
    - No new facts about the original clip have emerged.
    - Preserve Phase 1 actions already taken or approved.
    - Add/modify actions to address the escalation.
    - New sponsor deadline and demands must be addressed explicitly.
    - If voicemail signals are present, factor them into prioritization.
    - Respect all approval chains.
    Output ONLY valid JSON, no markdown fences.
""")


def run_adaptation(phase1_plan_json: str, escalation_summary: str) -> dict:
    prompt = (
        f"PHASE 1 PLAN:\n{phase1_plan_json}\n\n"
        f"ESCALATION PACKET:\n{escalation_summary}"
    )
    raw = _call(ADAPT_SYSTEM, prompt, max_tokens=6000)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    return json.loads(cleaned)
