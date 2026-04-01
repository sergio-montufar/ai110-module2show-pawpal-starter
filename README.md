# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The scheduler in `pawpal_system.py` includes four algorithmic improvements beyond basic priority ordering:

- **Sort by time** -- Tasks with a `scheduled_time` (`"HH:MM"` format) are sorted chronologically using a lambda key that compares time strings lexicographically, with priority score as a tiebreaker.
- **Preference-aware scoring** -- `Task.schedule_score()` combines the base priority (1-3) with a +2 bonus when the task category matches an owner preference, so preferred care areas float to the top.
- **Recurring tasks** -- When a `"daily"` or `"weekly"` task is marked complete, `mark_complete()` uses `timedelta` to compute the next date and automatically creates a new Task instance assigned to the same pet.
- **Conflict detection** -- `Scheduler.detect_conflicts()` performs a pairwise overlap check (`a_start < b_end and b_start < a_end`) on all timed tasks and returns human-readable warnings identifying same-pet and cross-pet conflicts without crashing the program.
