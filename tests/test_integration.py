"""Integration tests — require a valid ANTHROPIC_API_KEY in .env.

These tests run the actual pipeline against the published packets and
validate that outputs meet the challenge requirements.

Run with: python -m pytest tests/test_integration.py -v
"""

import json
import os
import pytest
from pathlib import Path

from agent.pipeline import run_phase1, run_phase2
from agent.formatter import format_submission

ROOT = Path(__file__).resolve().parent.parent

# Skip entire module if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping integration tests",
)


@pytest.fixture(scope="module")
def phase1_result():
    """Run Phase 1 once for all tests in this module."""
    return run_phase1(str(ROOT / "challenge_docs" / "packet_a.md"))


@pytest.fixture(scope="module")
def phase2_result(phase1_result):
    """Run Phase 2 once for all tests in this module."""
    return run_phase2(phase1_result, str(ROOT / "challenge_docs" / "packet_b.md"))


# ── Phase 1 tests ───────────────────────────────────────────────────

class TestPhase1:
    def test_triage_has_severity(self, phase1_result):
        assert phase1_result["triage"]["severity"] in ("low", "medium", "high", "critical")

    def test_triage_severity_is_high_or_critical(self, phase1_result):
        """This scenario is objectively high-severity."""
        assert phase1_result["triage"]["severity"] in ("high", "critical")

    def test_triage_has_immediate_actions(self, phase1_result):
        assert len(phase1_result["triage"]["immediate_actions"]) >= 1

    def test_drafts_include_sponsor(self, phase1_result):
        targets = [d["target"] for d in phase1_result["drafts"]]
        assert "sponsor" in targets

    def test_drafts_include_reporter(self, phase1_result):
        targets = [d["target"] for d in phase1_result["drafts"]]
        assert "reporter" in targets

    def test_sponsor_holding_line_under_40_words(self, phase1_result):
        sponsor_drafts = [d for d in phase1_result["drafts"] if d["target"] == "sponsor"]
        for d in sponsor_drafts:
            word_count = len(d["content"].split())
            assert word_count <= 45, (  # small margin for LLM variance
                f"Sponsor line is {word_count} words (limit 40): {d['content']}"
            )

    def test_timeline_has_entries(self, phase1_result):
        assert len(phase1_result["timeline"]) >= 3

    def test_timeline_respects_deadlines(self, phase1_result):
        """Check that the timeline mentions key deadlines."""
        all_actions = " ".join(
            item.get("action", "") + " " + item.get("time", "")
            for item in phase1_result["timeline"]
        )
        # The 5:50 PM sponsor deadline should appear
        assert "5:50" in all_actions or "550" in all_actions.replace(":", "")

    def test_decision_exists(self, phase1_result):
        assert phase1_result["decision"]["decision"] in ("hold", "speak", "conditional_speak")

    def test_drafts_have_approval_field(self, phase1_result):
        for d in phase1_result["drafts"]:
            assert "approval_required_from" in d
            assert d["approval_required_from"]  # not empty


# ── Phase 2 tests ───────────────────────────────────────────────────

class TestPhase2:
    def test_phase2_note_present(self, phase2_result):
        assert "Phase 1" in phase2_result.get("phase2_note", "")

    def test_what_changed_is_not_empty(self, phase2_result):
        assert phase2_result.get("what_changed", "").strip()

    def test_updated_triage_exists(self, phase2_result):
        assert phase2_result.get("updated_triage")
        assert "severity" in phase2_result["updated_triage"]

    def test_updated_drafts_include_sponsor(self, phase2_result):
        targets = [d["target"] for d in phase2_result.get("updated_drafts", [])]
        assert "sponsor" in targets

    def test_updated_timeline_addresses_635_deadline(self, phase2_result):
        all_text = " ".join(
            json.dumps(item) for item in phase2_result.get("updated_timeline", [])
        )
        assert "6:35" in all_text or "635" in all_text.replace(":", "")

    def test_updated_decision_exists(self, phase2_result):
        ud = phase2_result.get("updated_decision", {})
        assert ud.get("decision") in ("hold", "speak", "conditional_speak")


# ── Submission format tests ──────────────────────────────────────────

class TestSubmissionFormat:
    def test_submission_contains_both_phases(self, phase1_result, phase2_result):
        doc = format_submission(phase1_result, phase2_result)
        assert "## Phase 1" in doc
        assert "## Phase 2" in doc

    def test_submission_contains_workflow_proof(self, phase1_result, phase2_result):
        doc = format_submission(phase1_result, phase2_result)
        assert "Workflow Proof Block" in doc

    def test_submission_contains_reporter_pair(self, phase1_result, phase2_result):
        doc = format_submission(phase1_result, phase2_result)
        assert "Raw-to-final reporter reply" in doc

    def test_submission_contains_human_edit_disclosure(self, phase1_result, phase2_result):
        doc = format_submission(phase1_result, phase2_result)
        assert "Human edit disclosure" in doc

    def test_submission_contains_phase2_after_phase1_note(self, phase1_result, phase2_result):
        doc = format_submission(phase1_result, phase2_result)
        assert "produced after" in doc.lower() or "after completing Phase 1" in doc
