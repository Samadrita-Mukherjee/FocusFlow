import os
import csv
import shutil
from datetime import datetime
from .task import Task
from utils.paths import DATA_DIR

class User:
    def __init__(self, username):
        self.username = username
        self.tasks_file = os.path.join(DATA_DIR, f"tasks_{username}.csv")
        self.tasks = []
        self.load_tasks()

    # ---------- persistence ----------
    def load_tasks(self):
        self.tasks = []
        if not os.path.exists(self.tasks_file):
            return
        try:
            with open(self.tasks_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        self.tasks.append(Task.from_csv_row(row))
        except Exception as e:
            print('Error loading tasks:', e)

    def save_all_tasks(self):
        with open(self.tasks_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for t in self.tasks:
                writer.writerow(t.to_csv_row())

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.save_all_tasks()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_all_tasks()
            return True
        return False

    def update_task(self, index, **kwargs):
        if 0 <= index < len(self.tasks):
            t = self.tasks[index]
            t.name = kwargs.get('name', t.name)
            t.category = kwargs.get('category', t.category)
            t.hours = float(kwargs.get('hours', t.hours))
            t.completed = bool(kwargs.get('completed', t.completed))
            if 'date' in kwargs:
                t.date = datetime.strptime(kwargs['date'], '%Y-%m-%d').date()
            self.save_all_tasks()
            return True
        return False

    # ---------- analytics ----------
    def tasks_on_date(self, d):
        return [t for t in self.tasks if t.date == d]

    def tasks_in_range(self, start, end):
        s = datetime.strptime(start, '%Y-%m-%d').date()
        e = datetime.strptime(end, '%Y-%m-%d').date()
        return [t for t in self.tasks if s <= t.date <= e]

    def total_productive_hours(self, start=None, end=None):
        tasks = self.tasks_in_range(start, end) if (start and end) else self.tasks
        return sum(t.hours for t in tasks if t.completed)

    def total_hours(self, start=None, end=None):
        tasks = self.tasks_in_range(start, end) if (start and end) else self.tasks
        return sum(t.hours for t in tasks)

    def completion_rate(self, start=None, end=None):
        tasks = self.tasks_in_range(start, end) if (start and end) else self.tasks
        if not tasks:
            return 0.0
        completed = sum(1 for t in tasks if t.completed)
        return (completed / len(tasks)) * 100

    def average_time_per_category(self, start=None, end=None):
        tasks = self.tasks_in_range(start, end) if (start and end) else self.tasks
        sums = {}
        counts = {}
        for t in tasks:
            sums[t.category] = sums.get(t.category, 0.0) + t.hours
            counts[t.category] = counts.get(t.category, 0) + 1
        return {k: (sums[k] / counts[k]) for k in sums}

    def productivity_score(self, start=None, end=None):
        completed_hours = self.total_productive_hours(start, end)
        total = self.total_hours(start, end)
        if total == 0:
            return 0.0
        return (completed_hours / total) * 100

    # ---------- backup / restore ----------
    def backup(self):
        if not os.path.exists(self.tasks_file):
            return None
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(DATA_DIR, f'backup_{self.username}_{ts}.csv')
        shutil.copy2(self.tasks_file, dest)
        return dest

    def restore(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError('Backup not found')
        shutil.copy2(path, self.tasks_file)
        self.load_tasks()

