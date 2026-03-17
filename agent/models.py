"""Data models for the crisis-response agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StakeholderType(str, Enum):
    SPONSOR = "sponsor"
    REPORTER = "reporter"
    MANAGER = "manager"
    PUBLIC = "public"
    TALENT = "talent"


class MessagePriority(str, Enum):
    IMMEDIATE = "immediate"
    URGENT = "urgent"
    STANDARD = "standard"
    LOW = "low"


@dataclass
class InboundMessage:
    sender: str
    stakeholder_type: StakeholderType
    timestamp: str
    content: str
    priority: MessagePriority = MessagePriority.STANDARD
    requires_response_by: Optional[str] = None


@dataclass
class CrisisContext:
    talent_name: str
    scenario_time: str
    situation_summary: str
    clip_description: str
    known_facts: list[str] = field(default_factory=list)
    known_limits: list[str] = field(default_factory=list)
    timing_constraints: list[str] = field(default_factory=list)
    voice_guidelines: dict = field(default_factory=dict)
    inbound_messages: list[InboundMessage] = field(default_factory=list)


@dataclass
class TriageResult:
    severity: Severity
    reasoning: str
    immediate_actions: list[str]
    risks: list[str]
    stakeholder_priorities: list[str]


@dataclass
class DraftResponse:
    target: StakeholderType
    recipient_name: str
    content: str
    word_count: int
    approval_required_from: str
    rationale: str
    deadline: Optional[str] = None


@dataclass
class ActionItem:
    time: str
    action: str
    owner: str
    status: str = "pending"
    depends_on: Optional[str] = None


@dataclass
class CrisisPlan:
    phase: str
    triage: TriageResult
    drafted_responses: list[DraftResponse] = field(default_factory=list)
    action_timeline: list[ActionItem] = field(default_factory=list)
    hold_or_speak_decision: str = ""
    decision_rationale: str = ""
    approval_chain: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
