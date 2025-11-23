from datetime import date
from utils.quotes import QUOTES
import random

def show_daily_summary(user):
    today = date.today()
    tasks = user.tasks_on_date(today)
    completed = sum(1 for t in tasks if t.completed)
    pending = sum(1 for t in tasks if not t.completed)
    total_hours = sum(t.hours for t in tasks)
    print(f"Today's summary ({today}): {len(tasks)} tasks, {completed} completed, {pending} pending, {total_hours}h total")
    if pending:
        print('You have unfinished tasks. Keep going!')
    print(random.choice(QUOTES))

