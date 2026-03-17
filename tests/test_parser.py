"""Unit tests for the packet parser — no API key needed."""

import pytest
from pathlib import Path

from agent.parser import parse_packet, _classify_stakeholder, _estimate_priority
from agent.models import StakeholderType, MessagePriority


# ── Fixtures ─────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent

@pytest.fixture
def packet_a_text():
    return (ROOT / "packet_a.md").read_text(encoding="utf-8")

@pytest.fixture
def packet_b_text():
    return (ROOT / "packet_b.md").read_text(encoding="utf-8")


# ── Packet A parsing ────────────────────────────────────────────────

class TestParsePacketA:
    def test_extracts_talent_name(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert result["talent_name"] == "Timothée Chalamet"

    def test_extracts_scenario_time(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert "5:30" in result["scenario_time"]

    def test_extracts_situation_summary(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert "22-second" in result["situation_summary"] or "clip" in result["situation_summary"].lower()

    def test_extracts_clip_description(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert "ballet" in result["clip_description"].lower() or "opera" in result["clip_description"].lower()

    def test_extracts_known_limits(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert len(result["known_limits"]) >= 3
        assert any("real" in lim.lower() for lim in result["known_limits"])

    def test_extracts_timing_constraints(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert len(result["timing_constraints"]) >= 3
        # Must find the 6:05 PM and 5:50 PM deadlines
        all_text = " ".join(result["timing_constraints"])
        assert "6:05" in all_text
        assert "5:50" in all_text

    def test_extracts_voice_guidelines(self, packet_a_text):
        result = parse_packet(packet_a_text)
        vg = result["voice_guidelines"]
        assert len(vg.get("aim_for", [])) >= 3
        assert len(vg.get("do_not", [])) >= 4

    def test_extracts_inbound_messages(self, packet_a_text):
        result = parse_packet(packet_a_text)
        assert len(result["inbound_messages"]) >= 3  # sponsor, reporter, manager

    def test_sponsor_message_identified(self, packet_a_text):
        result = parse_packet(packet_a_text)
        sponsors = [m for m in result["inbound_messages"]
                     if m.stakeholder_type == StakeholderType.SPONSOR]
        assert len(sponsors) >= 1

    def test_reporter_message_identified(self, packet_a_text):
        result = parse_packet(packet_a_text)
        reporters = [m for m in result["inbound_messages"]
                      if m.stakeholder_type == StakeholderType.REPORTER]
        assert len(reporters) >= 1

    def test_manager_message_identified(self, packet_a_text):
        result = parse_packet(packet_a_text)
        managers = [m for m in result["inbound_messages"]
                     if m.stakeholder_type == StakeholderType.MANAGER]
        assert len(managers) >= 1


# ── Packet B parsing ────────────────────────────────────────────────

class TestParsePacketB:
    def test_extracts_talent_name(self, packet_b_text):
        result = parse_packet(packet_b_text)
        assert result["talent_name"] == "Timothée Chalamet"

    def test_extracts_scenario_time(self, packet_b_text):
        result = parse_packet(packet_b_text)
        assert "6:15" in result["scenario_time"]

    def test_extracts_escalation_details(self, packet_b_text):
        result = parse_packet(packet_b_text)
        assert len(result["escalation_details"]) >= 2
        all_text = " ".join(result["escalation_details"]).lower()
        assert "escalat" in all_text

    def test_extracts_sponsor_escalation_message(self, packet_b_text):
        result = parse_packet(packet_b_text)
        sponsors = [m for m in result["inbound_messages"]
                     if m.stakeholder_type == StakeholderType.SPONSOR]
        assert len(sponsors) >= 1
        assert any("6:35" in m.content for m in sponsors)

    def test_extracts_voicemail_signals(self, packet_b_text):
        result = parse_packet(packet_b_text)
        assert len(result["voicemail_signals"]) >= 2

    def test_voicemail_has_required_fields(self, packet_b_text):
        result = parse_packet(packet_b_text)
        for vm in result["voicemail_signals"]:
            assert "sender" in vm
            assert "received" in vm
            assert "duration" in vm

    def test_sponsor_escalation_is_immediate_priority(self, packet_b_text):
        result = parse_packet(packet_b_text)
        sponsors = [m for m in result["inbound_messages"]
                     if m.stakeholder_type == StakeholderType.SPONSOR]
        assert any(m.priority == MessagePriority.IMMEDIATE for m in sponsors)


# ── Helper function tests ───────────────────────────────────────────

class TestClassifyStakeholder:
    def test_sponsor(self):
        assert _classify_stakeholder("Maison Valeur partnership lead") == StakeholderType.SPONSOR

    def test_reporter(self):
        assert _classify_stakeholder("Reporter — Alex Chen") == StakeholderType.REPORTER

    def test_journalist(self):
        assert _classify_stakeholder("Tom Ellery, Journalist") == StakeholderType.REPORTER

    def test_manager(self):
        assert _classify_stakeholder("Manager, 5:25 PM") == StakeholderType.MANAGER

    def test_unknown_defaults_public(self):
        assert _classify_stakeholder("Random Person") == StakeholderType.PUBLIC


class TestEstimatePriority:
    def test_escalation_language_is_immediate(self):
        assert _estimate_priority(
            StakeholderType.SPONSOR, "We are escalating internally"
        ) == MessagePriority.IMMEDIATE

    def test_pause_language_is_immediate(self):
        assert _estimate_priority(
            StakeholderType.SPONSOR, "considering pausing all brand activity"
        ) == MessagePriority.IMMEDIATE

    def test_sponsor_without_urgency_is_urgent(self):
        assert _estimate_priority(
            StakeholderType.SPONSOR, "We are monitoring closely"
        ) == MessagePriority.URGENT

    def test_reporter_is_standard(self):
        assert _estimate_priority(
            StakeholderType.REPORTER, "Can you confirm the quote?"
        ) == MessagePriority.STANDARD


# ── Synthetic packet test ───────────────────────────────────────────

class TestSyntheticPacket:
    """Test that the parser generalizes to a packet with different content
    but the same markdown structure."""

    SYNTHETIC_A = """\
# Packet A — The photo surfaces

**Talent:** Jordan Rivera
**Scenario time:** 3:00 PM

## Situation

A blurry photo from a private event started circulating at 2:15 PM. By 3:00 PM it is trending.

## Viral clip

The photo appears to show Jordan making an offensive gesture at a charity gala.

Known limits:
- the photo is real
- it is from a private event two weeks ago
- the full context of the moment is unknown

## Timing and approvals

- Jordan is in a meeting until **3:45 PM**.
- Any public statement requires **Jordan's approval**.
- The manager can approve holding replies.
- Sponsor needs a line by **3:20 PM**.
- That line must be **30 words or fewer**.

## Voice guide for outward-facing language

Aim for:
- empathetic and measured
- honest about the situation

Do not:
- dismiss the concern
- blame the photographer

## Inbound messages

### Sponsor — GreenLeaf partnership lead, 2:50 PM

> We're seeing negative tags. What is Jordan's position?

### Reporter — Sam Lee, City Herald, 2:55 PM

> We're running a story. Can you comment?

### Manager, 2:58 PM

> The photo is real but it looks worse than it was. Jordan was reacting to a friend's joke.
"""

    def test_synthetic_talent_name(self):
        result = parse_packet(self.SYNTHETIC_A)
        assert result["talent_name"] == "Jordan Rivera"

    def test_synthetic_scenario_time(self):
        result = parse_packet(self.SYNTHETIC_A)
        assert "3:00" in result["scenario_time"]

    def test_synthetic_timing_constraints(self):
        result = parse_packet(self.SYNTHETIC_A)
        all_text = " ".join(result["timing_constraints"])
        assert "3:45" in all_text
        assert "3:20" in all_text

    def test_synthetic_inbound_count(self):
        result = parse_packet(self.SYNTHETIC_A)
        assert len(result["inbound_messages"]) >= 3

    def test_synthetic_stakeholder_types(self):
        result = parse_packet(self.SYNTHETIC_A)
        types = {m.stakeholder_type for m in result["inbound_messages"]}
        assert StakeholderType.SPONSOR in types
        assert StakeholderType.REPORTER in types
        assert StakeholderType.MANAGER in types
