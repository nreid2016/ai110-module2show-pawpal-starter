# PawPal+

PawPal+ is a Streamlit pet-care planning assistant for busy owners. It tracks tasks across multiple pets, supports completion and recurring tasks, and produces a readable daily schedule with conflict warnings.

## Step 1: Problem and core user actions

The scenario is a busy pet owner who needs help staying consistent with walks, feeding, medicine, grooming, and enrichment. PawPal+ is intended to organize those tasks without hiding why a task was selected or skipped.

Three core actions a user can perform are:

1. Add a pet with a name and species so the owner can manage more than one animal.
2. Add a task for a specific pet with a time, duration, priority, and frequency.
3. Generate today's schedule to see tasks in chronological order, along with conflict warnings and completion controls.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 main.py
python3 -m streamlit run app.py
```

## CLI demo

`main.py` creates one owner, two pets, and three tasks, then prints the schedule:

```text
Today's Schedule — Sunday, November 08, 2026
  08:00 AM — Mochi: Morning walk (25 min, high priority)
  08:30 AM — Mochi: Breakfast (10 min, high priority)
  09:00 AM — Luna: Medication (5 min, high priority)
```

## Features

- Owner management: `Owner.add_pet()`, `Owner.get_pet()`, and `Owner.all_tasks()`.
- Task completion: `Task.mark_complete()` changes completion status.
- Recurrence: daily tasks create the next day's task; weekly tasks create the next week's task.
- Sorting: `Scheduler.sort_by_time()` orders tasks chronologically.
- Filtering: `Scheduler.filter_tasks()` filters by pet, completion status, or date.
- Conflict warnings: `Scheduler.detect_conflicts()` reports duplicate start times across pets.
- Daily planning: `Scheduler.daily_schedule()` and `Scheduler.build_plan()` produce a time-ordered plan within the owner's available-minute budget.
- UI integration: `app.py` stores the `Owner` object in `st.session_state`, so pets and tasks persist between Streamlit interactions.

## Testing PawPal+

Run the automated tests with:

```bash
python3 -m pytest
```

The suite covers task completion, task addition, chronological sorting, daily and weekly recurrence, cross-pet conflict detection, filtering, and invalid input.

Successful run:

```text
........                                                                 [100%]
8 passed in 0.01s
```

Confidence level: 4/5 stars. The core behaviors are covered by automated tests. The remaining uncertainty is mostly around future persistence, calendar integration, and more complex overlapping-duration rules.

## UML and project files

- `diagrams/uml_draft.mmd` — initial working class diagram.
- `diagrams/uml_final.mmd` — diagram updated to match the final implementation.
- `pawpal_system.py` — domain classes and algorithms.
- `main.py` — CLI demo and evidence output.
- `app.py` — Streamlit interface.
- `tests/test_pawpal.py` — automated tests.
- `reflection.md` — design, tradeoffs, AI collaboration, and verification reflection.
