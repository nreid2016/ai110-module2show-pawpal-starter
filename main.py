from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task, format_schedule


def main() -> None:
    """Run a small CLI demonstration of PawPal+."""
    today = date.today()
    owner = Owner("Nas", daily_minutes=90)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", time(8, 0), "daily", 25, "high", due_date=today, category="exercise"))
    mochi.add_task(Task("Breakfast", time(8, 30), "daily", 10, "high", due_date=today, category="feeding"))
    luna.add_task(Task("Medication", time(9, 0), "once", 5, "high", due_date=today, category="medication"))

    scheduler = Scheduler(owner)
    entries, warnings = scheduler.build_plan(today)
    print(format_schedule(entries, today))
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
