"""Core domain model for the PawPal+ pet-care scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Iterable


@dataclass
class Task:
    """Represent one pet-care activity."""

    description: str
    time: time
    frequency: str = "once"
    duration_minutes: int = 15
    priority: str = "medium"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    category: str = "general"

    def __post_init__(self) -> None:
        """Validate task values."""
        if not self.description.strip():
            raise ValueError("Task description cannot be blank")
        if self.frequency not in {"once", "daily", "weekly"}:
            raise ValueError("Frequency must be once, daily, or weekly")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be greater than zero")
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("Priority must be low, medium, or high")

    def mark_complete(self, completed_on: date | None = None) -> Task | None:
        """Mark this task complete and return its next recurring occurrence."""
        self.completed = True
        if self.frequency == "once":
            return None
        completed_on = completed_on or self.due_date
        days = 1 if self.frequency == "daily" else 7
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_date=completed_on + timedelta(days=days),
            category=self.category,
        )

    def is_due_on(self, day: date) -> bool:
        """Return whether this task belongs on the selected date."""
        return self.due_date == day and not self.completed


@dataclass
class Pet:
    """Store a pet and its care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]

    def complete_task(self, description: str, completed_on: date | None = None) -> Task | None:
        """Complete a matching task and add its next recurring occurrence."""
        for task in self.tasks:
            if task.description == description and not task.completed:
                next_task = task.mark_complete(completed_on)
                if next_task:
                    self.tasks.append(next_task)
                return next_task
        raise ValueError(f"No pending task named {description!r}")


@dataclass
class Owner:
    """Manage multiple pets and provide access to their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    daily_minutes: int = 120

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's household."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet:
        """Return a pet by name."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        raise ValueError(f"Pet {name!r} was not found")

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every pet/task pair managed by this owner."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass(frozen=True)
class ScheduleEntry:
    """Pair a pet with a task in a displayed schedule."""

    pet: Pet
    task: Task


class Scheduler:
    """Sort, filter, recur, and detect conflicts across an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self, tasks: Iterable[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Return tasks in chronological order."""
        return sorted(tasks or self.owner.all_tasks(), key=lambda pair: (pair[1].time, pair[0].name.lower()))

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        day: date | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet, completion status, and due date."""
        pairs = self.owner.all_tasks()
        if pet_name:
            pairs = [(pet, task) for pet, task in pairs if pet.name == pet_name]
        if completed is not None:
            pairs = [(pet, task) for pet, task in pairs if task.completed is completed]
        if day:
            pairs = [(pet, task) for pet, task in pairs if task.due_date == day]
        return self.sort_by_time(pairs)

    def detect_conflicts(self, tasks: Iterable[tuple[Pet, Task]] | None = None) -> list[str]:
        """Return warnings for tasks with overlapping start times."""
        sorted_tasks = self.sort_by_time(tasks)
        warnings = []
        for first, second in zip(sorted_tasks, sorted_tasks[1:]):
            if first[1].time == second[1].time:
                warnings.append(
                    f"Conflict: {first[0].name}'s {first[1].description} and "
                    f"{second[0].name}'s {second[1].description} start at {first[1].time:%H:%M}."
                )
        return warnings

    def mark_task_complete(self, pet_name: str, description: str, completed_on: date | None = None) -> Task | None:
        """Complete a task through the owner's pet collection."""
        return self.owner.get_pet(pet_name).complete_task(description, completed_on)

    def daily_schedule(self, day: date) -> list[tuple[Pet, Task]]:
        """Return incomplete tasks due on a day, ordered by time and priority."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks = self.filter_tasks(completed=False, day=day)
        return sorted(tasks, key=lambda pair: (pair[1].time, priority_order[pair[1].priority]))

    def build_plan(self, day: date, available_minutes: int | None = None) -> tuple[list[ScheduleEntry], list[str]]:
        """Build a budget-aware daily plan and return selected tasks plus warnings."""
        budget = self.owner.daily_minutes if available_minutes is None else available_minutes
        selected: list[ScheduleEntry] = []
        used = 0
        for pet, task in self.daily_schedule(day):
            if used + task.duration_minutes > budget:
                continue
            selected.append(ScheduleEntry(pet, task))
            used += task.duration_minutes
        pairs = [(entry.pet, entry.task) for entry in selected]
        return selected, self.detect_conflicts(pairs)


def format_schedule(entries: Iterable[ScheduleEntry], day: date) -> str:
    """Format a human-readable schedule for the CLI."""
    lines = [f"Today's Schedule — {day:%A, %B %d, %Y}"]
    entries = list(entries)
    if not entries:
        return "\n".join(lines + ["  No tasks scheduled."])
    for entry in entries:
        lines.append(
            f"  {entry.task.time:%I:%M %p} — {entry.pet.name}: {entry.task.description} "
            f"({entry.task.duration_minutes} min, {entry.task.priority} priority)"
        )
    return "\n".join(lines)
