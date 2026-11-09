# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

I started with the required four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- `Owner` stores the owner's name, daily time budget, and multiple pets. It provides access to all tasks across the household.
- `Pet` stores a pet's name, species, and task list. It can add tasks, count tasks, return pending tasks, and complete a task.
- `Task` stores a description, time, frequency, duration, priority, completion status, due date, and category. It can mark itself complete and create the next occurrence for recurring work.
- `Scheduler` is the system's brain. It retrieves tasks from the owner's pets, sorts and filters them, detects conflicts, handles completion, and builds a daily schedule.

The three main user actions are adding a pet, adding a task to a pet, and generating today's schedule. Those actions map directly to the `Owner.add_pet`, `Pet.add_task`, and `Scheduler.daily_schedule`/`build_plan` methods.

### b. Design changes

I added `ScheduleEntry` as a small result object for the final schedule and separated the scheduler's algorithms into named methods. This kept the UI from reaching into scheduling details and made sorting, filtering, recurrence, and conflict detection independently testable.

I also kept the original `Task` after completion and append the next recurring occurrence to the pet's task list. That makes completion history visible instead of replacing the original task.

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

The scheduler considers task date, completion status, pet, start time, frequency, duration, priority, and the owner's available minutes. It sorts tasks chronologically, uses priority when tasks have the same time, filters tasks by pet/status/date, and checks duplicate start times across pets.

### b. Tradeoffs

The conflict detector intentionally uses a lightweight exact-start-time rule. It warns when two tasks start at the same time, but it does not yet calculate every possible overlap from task durations. This is easier to explain and is sufficient for the first version, while a future version could compare time intervals.

The scheduler also keeps higher-priority work when the available-minute budget is limited. That is reasonable because medication or another high-priority care task should be shown before optional enrichment when time is constrained.

## 3. AI Collaboration

### a. How I used AI

I used Hermes as the AI coding assistant for design brainstorming, implementation, test generation, documentation, and verification. The most effective prompts were specific about the required classes and behaviors, such as asking for a scheduler that retrieves tasks from all of an owner's pets and asking for tests for recurrence and conflicts.

I used separate focused passes for the domain model, the Streamlit integration, the algorithmic layer, and the test/documentation pass. Keeping those concerns separate made it easier to compare the implementation against each phase of the assignment.

### b. Judgment and verification

I did not accept a design that only returned a raw list of objects for the schedule. I changed it to return readable schedule entries and warnings because a pet owner needs to understand the result. I verified the implementation by running `main.py`, compiling the Python files, and running the automated test suite.

## 4. Testing and Verification

### a. What I tested

The test suite verifies:

- `mark_complete()` changes a task's status;
- adding a task increases a pet's task count;
- tasks sort chronologically;
- daily recurrence creates the next day's task;
- weekly recurrence creates the next week's task;
- conflicts are detected across pets;
- filtering by pet and completion status works; and
- invalid frequencies are rejected.

### b. Confidence

I rate my confidence at 4 out of 5 stars. The current test suite passes with eight tests, and the CLI demo produces a readable schedule. If I had more time, I would add interval-based overlap tests, persistence tests, and Streamlit interaction tests.

## 5. Reflection

### a. What went well

The project now has a clear path from user action to backend behavior: the UI calls methods on the domain objects, and the scheduler produces a result that can be displayed directly. The CLI demo also makes the backend verifiable without relying on the browser.

### b. What I would improve

I would add saved data so tasks survive restarting the app, an edit/delete workflow for existing tasks, and a calendar view for several days. I would also replace exact-time conflict detection with interval-based conflict detection.

### c. Key takeaway

The lead architect's job is not just to accept generated code. It is to define the objects and behavior clearly, check that relationships make sense, and verify the result with tests and a working demo. AI accelerated the implementation, but the requirements and verification steps determined whether the solution was acceptable.
