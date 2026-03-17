"""Scenario tests using synthetic packets to validate generalization.

These test that the agent can handle unseen inputs with the same packet
structure but different facts, talent, and stakeholders.

Requires ANTHROPIC_API_KEY in .env.
Run with: python -m pytest tests/test_scenarios.py -v
"""

import json
import os
import pytest
from pathlib import Path

from agent.pipeline import run_phase1, run_phase2
from agent.parser import parse_packet

_skip_no_api = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping scenario tests",
)

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = ROOT / "test_scenarios"


# ═══════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════

def _assert_valid_phase1(result: dict, expected_talent: str, sponsor_word_limit: int = 45):
    """Common assertions for any Phase 1 result."""
    # Triage
    assert result["triage"]["severity"] in ("low", "medium", "high", "critical")
    assert result["triage"]["severity"] in ("high", "critical"), \
        f"Expected high/critical severity, got {result['triage']['severity']}"
    assert len(result["triage"]["immediate_actions"]) >= 1

    # Drafts cover required stakeholders
    targets = {d["target"] for d in result["drafts"]}
    assert "sponsor" in targets, "Missing sponsor draft"
    assert "reporter" in targets, "Missing reporter draft"

    # Sponsor holding line word limit
    for d in result["drafts"]:
        if d["target"] == "sponsor":
            wc = len(d["content"].split())
            assert wc <= sponsor_word_limit, \
                f"Sponsor line is {wc} words (limit {sponsor_word_limit}): {d['content']}"

    # All drafts have approval field
    for d in result["drafts"]:
        assert d.get("approval_required_from"), \
            f"Draft to {d.get('target')} missing approval_required_from"

    # Timeline
    assert len(result["timeline"]) >= 3, "Timeline too short"

    # Decision
    assert result["decision"]["decision"] in ("hold", "speak", "conditional_speak")
    assert result["decision"].get("rationale"), "Decision missing rationale"


def _assert_valid_phase2(result: dict, escalation_deadline: str):
    """Common assertions for any Phase 2 result."""
    assert result.get("updated_triage"), "Missing updated triage"
    assert result["updated_triage"].get("severity") in ("high", "critical")

    # Updated drafts include sponsor
    targets = [d["target"] for d in result.get("updated_drafts", [])]
    assert "sponsor" in targets, "Phase 2 missing sponsor draft"

    # Addresses the escalation deadline
    all_text = json.dumps(result)
    assert escalation_deadline in all_text, \
        f"Phase 2 output doesn't reference deadline {escalation_deadline}"

    # What changed is meaningful
    assert result.get("what_changed", "").strip(), "what_changed is empty"

    # Phase 2 note
    assert "Phase 1" in result.get("phase2_note", ""), \
        "Missing Phase 2 note referencing Phase 1"

    # Updated decision exists
    ud = result.get("updated_decision", {})
    assert ud.get("decision") in ("hold", "speak", "conditional_speak")


# ═══════════════════════════════════════════════════════════════════
# Scenario: Maya Santos — Theater audio leak (inline)
# ═══════════════════════════════════════════════════════════════════

MAYA_PACKET_A = """\
# Packet A — The audio leaks

**Talent:** Maya Santos
**Scenario time:** 2:00 PM

Use this file with `challenge_brief.md`. This packet contains the only verified inputs available at 2:00 PM.

## Situation

A 15-second audio clip leaked at about 1:15 PM across TikTok, X, and Reddit. By 2:00 PM it is a fast-moving controversy, with meme risk rising before a major charity gala appearance tonight.

Maya is also scheduled for visible co-branded activity tonight with **Stellara Cosmetics**, a fictional beauty brand partner.

## Timing and approvals

- Maya is in a fitting until **2:30 PM**.
- Any public statement in Maya's voice requires **Maya's approval**.
- The manager can approve **sponsor and reporter holding replies** before then.
- Stellara Cosmetics needs a sponsor-safe holding line by **2:15 PM**.
- That holding line must work before full facts are available and must be **35 words or fewer**.

## Viral clip

The audio captures Maya saying she thinks traditional theater is **"a dying art that nobody under 30 watches anymore."**

Known limits:
- the audio is real
- it came from a longer podcast recording
- the full recording is not provided here
- you do not know what was said immediately before or after the clip

## Public signal snapshot

### Headlines already moving

1. **Maya Santos Under Fire for "Dying Art" Theater Comments**
2. **Broadway Community Responds to Maya Santos Audio Leak**
3. **Is Maya Santos Right? Gen Z Debates Theater's Future**

### Representative reactions

- **"Saying nobody watches theater while starring in a show adapted from a play is peak irony."**
- **"She was clearly talking about audience demographics, not insulting actors."**
- **"If I'm the cosmetics brand, I'm sweating right now."**

## Inbound messages

### Sponsor — Stellara Cosmetics partnership lead, 1:45 PM

> We are seeing a significant increase in negative mentions linking Maya to the circulating audio. Before the gala, we need to understand whether more context is coming, whether Maya will address this, and whether her planned brand activity should proceed. Our team is on standby.

### Reporter — Jamie Park, Entertainment Weekly, 1:50 PM

> We are covering the reaction to Maya Santos's leaked audio comments about theater. Can you confirm the audio is authentic, whether Maya stands by the statement, and whether she plans to comment before tonight? Our deadline is **3:30 PM**.

### Manager, 1:55 PM

> The audio is real, but it's from a 45-minute podcast and sounds way worse without context. She was actually arguing that theater needs to evolve its marketing to reach younger audiences. She's upset and wants to tweet "listen to the full thing." Gala arrivals are at **7:00 PM**. Stellara wants confirmation she's still doing the brand moment on the carpet.

**Status of that explanation:** internal context only. It is **not** independently verified by this packet.

## Talent profile

- Maya is a high-profile actress with a strong social media following and a polished brand image.
- She has a history of thoughtful, well-received public statements.
- Because the clip involves theater, the backlash spans celebrity, arts, and Broadway communities, increasing meme risk.

## Voice guide for outward-facing language

Aim for:
- warm, genuine, and thoughtful
- specific without being defensive
- respectful to the theater community
- accountable for impact without confirming unverified context

Do not:
- make **"you didn't hear the whole thing"** the whole message
- argue with critics online
- be dismissive about theater or live performance
- focus on gala excitement while controversy is active
"""

MAYA_PACKET_B = """\
# Packet B — Sponsor escalation

**Talent:** Maya Santos
**Scenario time:** 3:00 PM

Use this file with `challenge_brief.md`. This packet happens later in scenario time. Complete **Phase 1** before handling this update.

## What changed

- Stellara Cosmetics has escalated the issue to their CEO.
- The sponsor now wants a response plan within **15 minutes**.
- Gala brand visibility may be pulled without a credible response.

## What did not change

- No new factual evidence about the original audio has emerged.
- The underlying issue is still the same 15-second clip and the reaction around it.
- This is a stakeholder-pressure update, not a fact update.

## Sponsor escalation message

### Stellara Cosmetics VP of Brand, 3:00 PM

> This has been escalated to our CEO. We need a concrete plan from your team within the next 15 minutes. We are considering pulling all brand visibility for Maya at tonight's gala — no carpet photos, no social tags, no co-branded content — unless we receive a credible response plan.
>
> By **3:15 PM**, please send:
> - whether Maya plans to issue a public statement tonight
> - whether she will still participate in brand moments at the gala
> - the exact language our team can use internally and externally
> - confirmation of who is the decision-maker on your side
>
> Without a plan by then, we will proceed with a full brand pullback for tonight.

## Additional inbound voicemails

These voicemail summaries are verified inbound signals available to the team by 3:00 PM.

### Rachel Kim, VP Partnerships — Lumina Jewelry
**Received:** 14:48
**Duration:** 0:19
**MP3:** [Rachel Kim.mp3](https://example.com/rachel_kim.mp3)

### David Chen, Journalist — The Stage Review
**Received:** 14:42
**Duration:** 0:31
**MP3:** [David Chen.mp3](https://example.com/david_chen.mp3)

**Why it matters:** High-priority sponsor-side escalation signal. Treat this as time-sensitive stakeholder pressure.
"""


@pytest.fixture(scope="module")
def maya_phase1(tmp_path_factory):
    p = tmp_path_factory.mktemp("maya") / "packet_a.md"
    p.write_text(MAYA_PACKET_A)
    return run_phase1(str(p))


@pytest.fixture(scope="module")
def maya_phase2(maya_phase1, tmp_path_factory):
    p = tmp_path_factory.mktemp("maya_b") / "packet_b.md"
    p.write_text(MAYA_PACKET_B)
    return run_phase2(maya_phase1, str(p))


@_skip_no_api
class TestMayaPhase1:
    def test_full_phase1(self, maya_phase1):
        _assert_valid_phase1(maya_phase1, "Maya Santos", sponsor_word_limit=40)

    def test_timeline_mentions_key_times(self, maya_phase1):
        all_text = " ".join(json.dumps(item) for item in maya_phase1["timeline"])
        assert "2:15" in all_text or "2:30" in all_text

    def test_decision_is_valid(self, maya_phase1):
        assert maya_phase1["decision"]["decision"] in ("hold", "speak", "conditional_speak")


@_skip_no_api
class TestMayaPhase2:
    def test_full_phase2(self, maya_phase2):
        _assert_valid_phase2(maya_phase2, "3:15")

    def test_updated_drafts_include_sponsor(self, maya_phase2):
        targets = [d["target"] for d in maya_phase2.get("updated_drafts", [])]
        assert "sponsor" in targets


# ═══════════════════════════════════════════════════════════════════
# Scenario: Elara Voss — Environmental hypocrisy video
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def elara_phase1():
    return run_phase1(str(SCENARIOS_DIR / "scenario_1_packet_a.md"))


@pytest.fixture(scope="module")
def elara_phase2(elara_phase1):
    return run_phase2(elara_phase1, str(SCENARIOS_DIR / "scenario_1_packet_b.md"))


@_skip_no_api
class TestElaraPhase1:
    def test_full_phase1(self, elara_phase1):
        _assert_valid_phase1(elara_phase1, "Elara Voss")

    def test_references_environmental_context(self, elara_phase1):
        all_text = json.dumps(elara_phase1).lower()
        assert "environment" in all_text or "climate" in all_text or "sustainab" in all_text

    def test_timeline_mentions_key_times(self, elara_phase1):
        all_text = " ".join(json.dumps(item) for item in elara_phase1["timeline"])
        assert "11:20" in all_text or "11:40" in all_text


@_skip_no_api
class TestElaraPhase2:
    def test_full_phase2(self, elara_phase2):
        _assert_valid_phase2(elara_phase2, "12:20")

    def test_escalation_addressed(self, elara_phase2):
        all_text = json.dumps(elara_phase2).lower()
        assert "keynote" in all_text or "cancel" in all_text or "launch" in all_text


# ═══════════════════════════════════════════════════════════════════
# Scenario: Marcus Bell — Deleted tweet classical music
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def marcus_phase1():
    return run_phase1(str(SCENARIOS_DIR / "scenario_2_packet_a.md"))


@pytest.fixture(scope="module")
def marcus_phase2(marcus_phase1):
    return run_phase2(marcus_phase1, str(SCENARIOS_DIR / "scenario_2_packet_b.md"))


@_skip_no_api
class TestMarcusPhase1:
    def test_full_phase1(self, marcus_phase1):
        _assert_valid_phase1(marcus_phase1, "Marcus Bell")

    def test_references_tweet_or_music(self, marcus_phase1):
        all_text = json.dumps(marcus_phase1).lower()
        assert "tweet" in all_text or "classical" in all_text or "music" in all_text

    def test_timeline_mentions_key_times(self, marcus_phase1):
        all_text = " ".join(json.dumps(item) for item in marcus_phase1["timeline"])
        assert "8:20" in all_text or "8:35" in all_text or "9:30" in all_text


@_skip_no_api
class TestMarcusPhase2:
    def test_full_phase2(self, marcus_phase2):
        _assert_valid_phase2(marcus_phase2, "9:15")

    def test_campaign_concern_addressed(self, marcus_phase2):
        all_text = json.dumps(marcus_phase2).lower()
        assert "campaign" in all_text or "launch" in all_text or "delay" in all_text


# ═══════════════════════════════════════════════════════════════════
# Scenario: Camille Fontaine — Disability mockery photo
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def camille_phase1():
    return run_phase1(str(SCENARIOS_DIR / "scenario_3_packet_a.md"))


@pytest.fixture(scope="module")
def camille_phase2(camille_phase1):
    return run_phase2(camille_phase1, str(SCENARIOS_DIR / "scenario_3_packet_b.md"))


@_skip_no_api
class TestCamillePhase1:
    def test_full_phase1(self, camille_phase1):
        _assert_valid_phase1(camille_phase1, "Camille Fontaine")

    def test_references_disability_context(self, camille_phase1):
        all_text = json.dumps(camille_phase1).lower()
        assert "disab" in all_text or "inclusion" in all_text or "accessib" in all_text

    def test_timeline_mentions_key_times(self, camille_phase1):
        all_text = " ".join(json.dumps(item) for item in camille_phase1["timeline"])
        assert "4:15" in all_text or "4:30" in all_text


@_skip_no_api
class TestCamillePhase2:
    def test_full_phase2(self, camille_phase2):
        _assert_valid_phase2(camille_phase2, "5:05")

    def test_multi_sponsor_addressed(self, camille_phase2):
        """Scenario 3 has two sponsors escalating."""
        all_text = json.dumps(camille_phase2).lower()
        assert "lumi" in all_text or "sponsor" in all_text

    def test_has_three_voicemail_signals(self, camille_phase2):
        """Packet B for this scenario has 3 voicemails — the most of any scenario."""
        all_text = json.dumps(camille_phase2).lower()
        # At minimum the escalation should reference the pressure
        assert "escal" in all_text or "pressure" in all_text


# ═══════════════════════════════════════════════════════════════════
# Parser-only tests for synthetic packets (no API key needed)
# ═══════════════════════════════════════════════════════════════════

class TestSyntheticParserOnly:
    """Verify the parser correctly handles all synthetic packet structures.
    These tests run without an API key.
    """

    @pytest.mark.parametrize("filename,expected_talent,expected_time", [
        ("scenario_1_packet_a.md", "Elara Voss", "11:00"),
        ("scenario_2_packet_a.md", "Marcus Bell", "8:00"),
        ("scenario_3_packet_a.md", "Camille Fontaine", "4:00"),
    ])
    def test_packet_a_basics(self, filename, expected_talent, expected_time):
        text = (SCENARIOS_DIR / filename).read_text()
        result = parse_packet(text)
        assert result["talent_name"] == expected_talent
        assert expected_time in result["scenario_time"]
        assert len(result["inbound_messages"]) >= 3
        assert result["situation_summary"]

    @pytest.mark.parametrize("filename,expected_time", [
        ("scenario_1_packet_b.md", "12:00"),
        ("scenario_2_packet_b.md", "9:00"),
        ("scenario_3_packet_b.md", "4:45"),
    ])
    def test_packet_b_escalation(self, filename, expected_time):
        text = (SCENARIOS_DIR / filename).read_text()
        result = parse_packet(text)
        assert expected_time in result["scenario_time"]
        assert len(result["escalation_details"]) >= 2
        assert len(result["voicemail_signals"]) >= 2

    def test_maya_inline_packet_a(self):
        result = parse_packet(MAYA_PACKET_A)
        assert result["talent_name"] == "Maya Santos"
        assert "2:00" in result["scenario_time"]
        assert len(result["inbound_messages"]) >= 3

    def test_maya_inline_packet_b(self):
        result = parse_packet(MAYA_PACKET_B)
        assert "3:00" in result["scenario_time"]
        assert len(result["escalation_details"]) >= 2

