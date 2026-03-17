Challenge Brief

Build the best "Timmy vs. Opera/Ballet" crisis-response agent

Build a crisis-response agent for a fast-moving celebrity backlash. The job is to assess risk, route work across stakeholders, produce aligned communications, and update the plan when pressure increases.

We score based on judgment, sequencing, coordination, workflow evidence, and how well the workflow adapts to unseen inputs.

This challenge is designed to:
- require a real agentic workflow
- allow different solution styles
- show decisions, approvals, and revisions in action
- reward process quality, not polished copy alone
- reward workflows that generalize beyond one fixed example

Why this scenario works

This challenge uses a controlled version of the Timothée Chalamet ballet/opera backlash. In public coverage, that issue moved from a clipped quote into arts-community criticism, meme amplification, institution responses, and awards-night commentary.

The scenario combines incomplete context, rapid spread across social platforms, sponsor risk, and hard timing constraints. Timmy is a high-visibility actor with a polished public image and a large online audience. Because the quote is about ballet and opera, the backlash spreads beyond celebrity coverage into culture and institution accounts. That makes the story harder to contain and raises sponsor and press pressure.

Scenario structure

All entrants receive the same two public packets.

Packet A — The clip breaks
Scenario time: 5:30 PM

A 22-second clip is spreading. Reporter, sponsor, and management messages arrive. Timmy is off-phone until 6:05 PM. A sponsor-safe holding line is needed by 5:50 PM.

Packet B — Sponsor escalation
Scenario time: 6:15 PM

No new facts appear about the clip. The sponsor escalates internally and may pause all brand activity unless a credible plan arrives by 6:35 PM.

Packet B is included from the start for fairness. In scenario time, it happens later. Complete Phase 1 before you handle Packet B.

What the public packets are for

Packet A and Packet B are builder-facing examples. They show the structure, timing, approvals, and file types your workflow must be able to handle.

They are not the full test set.

Organizers will judge entries using unseen evaluation inputs built in the same style and file formats as Packet A and Packet B. Those hidden inputs will test whether your workflow can adapt to new but comparable facts, signals, and stakeholder pressure rather than only perform well on the published example packets.

A strong use of hidden evaluation inputs is short voicemail-style items. These may include:
- high-priority voicemails from a sponsor or manager
- lower-priority voicemails from a less urgent stakeholder

Each voicemail-style input will include at minimum:
- sender
- timestamp

The goal is to test whether the workflow can correctly interpret urgency, route attention, and re-prioritize across multiple inbound signals without relying on one exact published packet.

What entrants must do

Build a workflow that can:
- assess crisis severity
- decide whether to speak or hold comment
- handle sponsor, reporter, management, and public response together
- sequence the next 30 to 60 minutes of actions
- revise the plan when a later escalation arrives
- generalize to unseen inputs that follow the same packet structure, including short voicemail-style signals

Rules for using the scenario

- Use only packet facts for scenario claims.
- Treat manager comments as internal context unless the packet verifies them.
- Do not invent missing transcript context.
- Do not assume legal review, full interview access, or outside evidence.
- Respect every stated approval limit and deadline.
- Complete Phase 1 before Packet B.
- Phase 2 must update Phase 1. Do not restart from scratch.
- Clearly label Phase 1 and Phase 2.
- Include one sentence stating that Phase 2 was produced after Phase 1.
- Build for the packet format, not only for the exact published facts.

Valid builds

You do not need a full production app. Valid entries can be code-based, no-code, notebook-based, prompt/config-based, or structured workflow specs. Small builds are valid if the operating logic is clear. No app, deployment, or demo video is required.

Submission requirements

Submit:
1. a public GitHub repo
2. the official submission form with team name, contact email, repo URL, and final commit SHA

The final commit SHA is the version we judge.

Your repo must include:
- one main submission file
- one standalone first-hour triage table artifact
- a short workflow overview or README
- short instructions showing how your workflow should be run or reviewed on Packet A-type and Packet B-type inputs
- any optional support files needed to understand how the build works

Required outputs

The main submission file must include:

Phase 1
- crisis severity with a short reason
- public response or a decision to hold comment, with a short reason
- reporter reply
- sponsor reply, including a sponsor-safe holding line of 40 words or fewer
- awards-night contingency plan
- three red flags

Phase 2
- what changed
- what stays the same
- revised next 30 minutes
- revised sponsor reply
- one sentence on whether the public-response timing changes

Workflow evidence
- workflow proof block
- raw-to-final reporter reply pair
- human edit disclosure

The separate triage table must include:
- stakeholder
- priority
- next action
- owner
- approval needed
- due by

How we judge entries

The published packets help entrants understand the task and demonstrate their workflow. Final judging is based on how well the workflow holds up on unseen evaluation inputs of the same file types and overall scenario shape.

- Crisis judgment, triage, and sequencing — 40%

- Does the agent read the room, route work to the right stakeholders, and sequence the right next moves under timing pressure?

- Cross-stakeholder coordination — 20%

- Do the public, reporter, sponsor, and event-facing outputs stay aligned with each other?

- Adaptation to unseen same-format inputs — 25%

- When the facts, tone, urgency, or stakeholder pressure change inside Packet A-type and Packet B-type inputs, including voicemail-style items with sender and timestamp, does the workflow adjust intelligently rather than collapse or repeat a canned answer?

- Agent/workflow credibility — 15%

- Does the submission show a reusable process with real approval logic, believable workflow evidence, and a setup organizers can inspect against hidden evaluation inputs?

High-scoring entries show clear triage, sensible restraint, strong approval logic, aligned outputs, and a workflow another operator could run again on a new version of the same problem.
