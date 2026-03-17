#!/usr/bin/env python3
"""Main entry point — runs the full crisis-response pipeline.

Usage:
    python run.py                          # uses default challenge_docs/packet_a.md
    python run.py --packet-a <path> --packet-b <path>
    python run.py --phase1-only --packet-a custom_packet.md
"""

import argparse
import json
import sys
from pathlib import Path

from agent.pipeline import run_phase1, run_phase2
from agent.formatter import format_submission


def main():
    parser = argparse.ArgumentParser(description="Timothée Crisis-Response Agent")
    parser.add_argument(
        "--packet-a", default="challenge_docs/packet_a.md",
        help="Path to Phase 1 packet (default: challenge_docs/packet_a.md)",
    )
    parser.add_argument(
        "--packet-b", default="challenge_docs/packet_b.md",
        help="Path to Phase 2 escalation packet (default: challenge_docs/packet_b.md)",
    )
    parser.add_argument(
        "--phase1-only", action="store_true",
        help="Run only Phase 1 (skip escalation)",
    )
    parser.add_argument(
        "--output", "-o", default="output/submission.md",
        help="Output path for the submission document",
    )
    parser.add_argument(
        "--json-output", default="output/raw_output.json",
        help="Output path for raw JSON results",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print progress to stdout",
    )
    args = parser.parse_args()

    # Validate input files exist
    if not Path(args.packet_a).exists():
        print(f"Error: packet file not found: {args.packet_a}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("  Timothée Crisis-Response Agent")
    print("=" * 60)

    # Phase 1
    print("\n▶ Running Phase 1...")
    phase1 = run_phase1(args.packet_a, verbose=args.verbose)
    print(f"  Severity: {phase1['triage'].get('severity', '?').upper()}")
    print(f"  Drafts: {len(phase1['drafts'])}")
    print(f"  Timeline actions: {len(phase1['timeline'])}")
    print(f"  Decision: {phase1['decision'].get('decision', '?').upper()}")

    # Phase 2
    phase2 = {}
    if not args.phase1_only:
        if not Path(args.packet_b).exists():
            print(f"Warning: escalation packet not found: {args.packet_b}", file=sys.stderr)
            print("  Skipping Phase 2.")
        else:
            print("\n▶ Running Phase 2 (escalation)...")
            phase2 = run_phase2(phase1, args.packet_b, verbose=args.verbose)
            print(f"  Updated severity: {phase2.get('updated_triage', {}).get('severity', '?').upper()}")
            print(f"  Updated drafts: {len(phase2.get('updated_drafts', []))}")
            print(f"  What changed: {phase2.get('what_changed', '—')}")

    # Write outputs
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Formatted submission
    submission_md = format_submission(phase1, phase2)
    Path(args.output).write_text(submission_md, encoding="utf-8")
    print(f"\n✅ Submission written to {args.output}")

    # Raw JSON
    json_out = {
        "phase1": phase1,
        "phase2": phase2,
    }
    # Remove non-serializable items
    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    def _default(o):
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)

    json_path.write_text(
        json.dumps(json_out, indent=2, default=_default), encoding="utf-8"
    )
    print(f"✅ Raw JSON written to {args.json_output}")
    print("\nDone.")


if __name__ == "__main__":
    main()
