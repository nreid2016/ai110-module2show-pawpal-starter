from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_changes_status():
    task = Task("Give medicine", time(8, 0))
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", time(8, 0)))
    assert pet.task_count() == 1


def test_scheduler_sort_by_time_returns_chronological_order():
    owner = Owner("Nas")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Breakfast", time(9, 0)))
    pet.add_task(Task("Walk", time(7, 30)))
    ordered = Scheduler(owner).sort_by_time()
    assert [task.description for _, task in ordered] == ["Walk", "Breakfast"]


def test_daily_completion_creates_next_day_task():
    today = date(2026, 11, 8)
    task = Task("Walk", time(8, 0), "daily", due_date=today)
    next_task = task.mark_complete(today)
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)


def test_weekly_completion_creates_next_week_task_on_pet():
    today = date(2026, 11, 8)
    pet = Pet("Mochi", "dog", [Task("Grooming", time(10, 0), "weekly", due_date=today)])
    pet.complete_task("Grooming", today)
    assert pet.task_count() == 2
    assert pet.tasks[-1].due_date == today + timedelta(days=7)


def test_scheduler_flags_duplicate_times_across_pets():
    owner = Owner("Nas")
    dog = Pet("Mochi", "dog", [Task("Walk", time(8, 0))])
    cat = Pet("Luna", "cat", [Task("Breakfast", time(8, 0))])
    owner.add_pet(dog)
    owner.add_pet(cat)
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Conflict" in warnings[0]


def test_filtering_by_pet_and_completion_status():
    owner = Owner("Nas")
    dog = Pet("Mochi", "dog", [Task("Walk", time(8, 0))])
    cat = Pet("Luna", "cat", [Task("Feed", time(9, 0))])
    cat.tasks[0].completed = True
    owner.add_pet(dog)
    owner.add_pet(cat)
    results = Scheduler(owner).filter_tasks(pet_name="Luna", completed=True)
    assert [(pet.name, task.description) for pet, task in results] == [("Luna", "Feed")]


def test_invalid_frequency_is_rejected():
    with pytest.raises(ValueError):
        Task("Walk", time(8, 0), "monthly")
