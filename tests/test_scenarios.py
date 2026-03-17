"""Scenario tests using synthetic packets to validate generalization.

These test that the agent can handle unseen inputs with the same packet
structure but different facts, talent, and stakeholders.

Requires ANTHROPIC_API_KEY in .env.
Run with: python -m pytest tests/test_scenarios.py -v
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

from agent.pipeline import run_phase1, run_phase2

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping scenario tests",
)


# ── Synthetic Packet A ──────────────────────────────────────────────

SYNTHETIC_PACKET_A = """\
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

SYNTHETIC_PACKET_B = """\
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
def synthetic_packet_a_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SYNTHETIC_PACKET_A)
        return f.name


@pytest.fixture(scope="module")
def synthetic_packet_b_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SYNTHETIC_PACKET_B)
        return f.name


@pytest.fixture(scope="module")
def synthetic_phase1(synthetic_packet_a_path):
    return run_phase1(synthetic_packet_a_path)


@pytest.fixture(scope="module")
def synthetic_phase2(synthetic_phase1, synthetic_packet_b_path):
    return run_phase2(synthetic_phase1, synthetic_packet_b_path)


class TestSyntheticPhase1:
    """Validate that the agent handles a completely different scenario."""

    def test_triage_severity(self, synthetic_phase1):
        assert synthetic_phase1["triage"]["severity"] in ("high", "critical")

    def test_drafts_cover_stakeholders(self, synthetic_phase1):
        targets = {d["target"] for d in synthetic_phase1["drafts"]}
        assert "sponsor" in targets
        assert "reporter" in targets

    def test_sponsor_line_within_word_limit(self, synthetic_phase1):
        """Synthetic packet says ≤35 words."""
        sponsor_drafts = [d for d in synthetic_phase1["drafts"] if d["target"] == "sponsor"]
        for d in sponsor_drafts:
            wc = len(d["content"].split())
            assert wc <= 40, f"Sponsor line is {wc} words (limit ~35): {d['content']}"

    def test_timeline_mentions_key_times(self, synthetic_phase1):
        all_text = " ".join(json.dumps(item) for item in synthetic_phase1["timeline"])
        # Should reference 2:15 PM (sponsor deadline) and 2:30 PM (talent available)
        assert "2:15" in all_text or "2:30" in all_text

    def test_decision_is_valid(self, synthetic_phase1):
        assert synthetic_phase1["decision"]["decision"] in ("hold", "speak", "conditional_speak")


class TestSyntheticPhase2:
    """Validate Phase 2 adaptation on the synthetic scenario."""

    def test_updated_triage_exists(self, synthetic_phase2):
        assert synthetic_phase2.get("updated_triage")

    def test_addresses_new_deadline(self, synthetic_phase2):
        """Phase 2 deadline is 3:15 PM."""
        all_text = json.dumps(synthetic_phase2)
        assert "3:15" in all_text

    def test_updated_drafts_include_sponsor(self, synthetic_phase2):
        targets = [d["target"] for d in synthetic_phase2.get("updated_drafts", [])]
        assert "sponsor" in targets

    def test_what_changed_not_empty(self, synthetic_phase2):
        assert synthetic_phase2.get("what_changed", "").strip()

    def test_phase2_note(self, synthetic_phase2):
        assert "Phase 1" in synthetic_phase2.get("phase2_note", "")
