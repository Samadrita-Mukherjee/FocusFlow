from datetime import datetime

class Task:
    def __init__(self, name, category, hours, completed, date_str):
        self.name = name
        self.category = category
        self.hours = float(hours)
        self.completed = bool(completed)
        # expects date_str in YYYY-MM-DD
        self.date = datetime.strptime(date_str, "%Y-%m-%d").date()

    def to_csv_row(self):
        return [self.name, self.category, str(self.hours), str(int(self.completed)), self.date.isoformat()]

    @staticmethod
    def from_csv_row(row):
        # row: [name, category, hours, completed(0/1), date]
        return Task(row[0], row[1], float(row[2]), bool(int(row[3])), row[4])
