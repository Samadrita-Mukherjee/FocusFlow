from models.task import Task
from datetime import datetime

def add_task_cli(user):
    print('--- Add Task ---')
    name = input('Task name: ').strip()
    category = input('Category: ').strip() or 'General'
    hours = input('Hours spent: ').strip()
    try:
        hours = float(hours)
    except:
        hours = 0.0
    completed = input('Completed? (y/n): ').strip().lower() == 'y'
    date_in = input('Date (YYYY-MM-DD) [default today]: ').strip() or datetime.now().date().isoformat()
    try:
        datetime.strptime(date_in, '%Y-%m-%d')
    except:
        date_in = datetime.now().date().isoformat()
    t = Task(name, category, hours, completed, date_in)
    user.add_task(t)
    print('Task added')

def view_tasks_cli(user):
    if not user.tasks:
        print('No tasks')
        return
    for i, t in enumerate(user.tasks):
        status = 'Done' if t.completed else 'Pending'
        print(f"{i}. [{status}] {t.date.isoformat()} - {t.name} ({t.category}) - {t.hours}h")

def update_task_cli(user):
    view_tasks_cli(user)
    idx = input('Index to update: ').strip()
    try:
        idx = int(idx)
    except:
        print('Invalid')
        return
    if idx<0 or idx>=len(user.tasks):
        print('Out of range')
        return
    t = user.tasks[idx]
    name = input(f'Name [{t.name}]: ').strip() or t.name
    category = input(f'Category [{t.category}]: ').strip() or t.category
    hours = input(f'Hours [{t.hours}]: ').strip() or str(t.hours)
    try:
        hours = float(hours)
    except:
        hours = t.hours
    completed = input(f'Completed (y/n) [{"y" if t.completed else "n"}]: ').strip().lower()
    completed = t.completed if completed=='' else (completed=='y')
    date = input(f'Date [{t.date.isoformat()}]: ').strip() or t.date.isoformat()
    user.update_task(idx, name=name, category=category, hours=hours, completed=completed, date=date)
    print('Updated')

def delete_task_cli(user):
    view_tasks_cli(user)
    idx = input('Index to delete: ').strip()
    try:
        idx = int(idx)
    except:
        print('Invalid')
        return
    if user.delete_task(idx):
        print('Deleted')
    else:
        print('Failed')

