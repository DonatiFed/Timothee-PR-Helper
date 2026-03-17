# Challenge Brief

## Build the best "Timothée vs. Opera/Ballet" crisis response agent

Build a crisis response agent for a fast moving celebrity backlash. The job is to assess risk, route work across stakeholders, produce aligned communications, and update the plan when pressure increases.

We score judgment, sequencing, coordination, workflow evidence, ease of handoff. Also, how well the workflow adapts to unseen inputs.

This challenge is designed to:
  require a real agentic workflow
  allow different solution styles
  show decisions, approvals, and revisions in action
  reward process quality, not polished copy alone
  reward workflows that generalize beyond one fixed example

## Scenario structure

All entrants receive the same two public packets.

### Packet A — The clip breaks
**Scenario time:** 5:30 PM  
A 22 second clip is spreading. Reporter, sponsor, and management messages arrive. Timmy is off phone until 6:05 PM. A sponsor safe holding line is needed by 5:50 PM.

### Packet B — Sponsor escalation
**Scenario time:** 6:15 PM  
No new facts appear about the clip. The sponsor escalates internally and may pause all brand activity unless a credible plan arrives by 6:35 PM.

Packet B is included from the start for fairness. In scenario time, it happens later. Complete Phase 1 before you handle Packet B.

## What the public packets are for

Packet A and Packet B are builder facing examples. They show the structure, timing, approvals, and file types your workflow must be able to handle.

They are not the full test set.

Organizers will judge entries using unseen evaluation inputs built in the same style and file formats as Packet A and Packet B. Those hidden inputs will test whether your workflow can adapt to new but comparable facts, signals, and stakeholder pressure rather than only perform well on the published example packets.

The goal is to test whether the workflow can correctly interpret urgency, route attention, and re prioritize across multiple inbound signals without relying on one exact published packet.

## What entrants must do

Build a workflow that can:
  assess crisis severity
  decide whether to speak or hold comment
  handle sponsor, reporter, management, and public response together
  sequence the next 30 to 60 minutes of actions
  revise the plan when a later escalation arrives
  generalize to unseen inputs that follow the same packet structure, including short voicemail style signals

## Rules for using the scenario

  Use only packet facts for scenario claims.
  Treat manager comments as internal context unless the packet verifies them.
  Do not invent missing transcript context.
  Do not assume legal review, full interview access, or outside evidence.
  Respect every stated approval limit and deadline.
  Complete Phase 1 before Packet B.
  Phase 2 must update Phase 1. Do not restart from scratch.
  Clearly label Phase 1 and Phase 2.
  Include one sentence stating that Phase 2 was produced after Phase 1.
  Build for the packet format, not only for the exact published facts.

## Valid builds

You do not need a full production app. Valid entries can be code based, no code, notebook based, prompt/config based, or structured workflow specs. Small builds are valid if the operating logic is clear. No app, deployment, or demo video is required.

## Submission requirements

Submit a public GitHub repo with:

A README explaining what you built and how to run or review it
A main submission file with your Phase A and Phase B outputs, workflow proof block, raw-to-final reporter reply pair, and human edit disclosure
Any supporting files needed to understand how the build works (code, notebooks, workflow exports, configs, demo video — include what you need, skip what you don't)
We allow a lot of flexibility and creativity here. There is no single right way to build this. **But remeber part of the grade is how easy handoff is for a PR team to start using immediately.**

How we judge entries
Entries are scored across five dimensions by human judges. The published packets help you understand the task and demonstrate your workflow. Final judging is based on how well the workflow holds up on unseen evaluation inputs of the same formats and overall scenario shape.

Crisis judgment, triage, and sequencing — 35%
Adaptation to new information — 20%
Cross-stakeholder coordination — 15%
Ease of implementation and handoff — 15%
Workflow credibility — 15%
High-scoring entries show clear triage, sensible restraint, aligned outputs across stakeholders, and a workflow someone else could pick up and run tomorrow on a new version of the same problem.

Allowed APIs and tools
Paid AI APIs: OpenAI, Claude, and Gemini only. Any free API is fine. Workflow tools (n8n, LangChain, CrewAI, etc.) are unrestricted.
