import matplotlib.pyplot as plt
import numpy as np

def visualize_cli(user):
    if not user.tasks:
        print('No data to visualize')
        return
    categories = {}
    dates = {}
    completed = 0
    pending = 0
    for t in user.tasks:
        categories[t.category] = categories.get(t.category, 0) + t.hours
        dates.setdefault(t.date.isoformat(), 0)
        if t.completed:
            dates[t.date.isoformat()] += t.hours
            completed += 1
        else:
            pending += 1

    print('1)Hours per category')
    print('2)Productivity over days')
    print('3)Completed vs Pending')
    ch = input('Choice: ').strip()

    if ch in ('1','3'):
        # bar
        cats = list(categories.keys())
        hours = np.array([categories[k] for k in cats])
        plt.figure(); plt.bar(cats, hours); plt.title('Hours by Category'); plt.xticks(rotation=45); plt.show()

    if ch in ('2','3'):
        # line
        if not dates:
            print('Not enough data')
        else:
            sd = sorted(dates.items())
            xs = [d for d,_ in sd]; ys=[h for _,h in sd]
            plt.figure(); plt.plot(xs, ys, marker='o'); plt.title('Productivity Over Days'); plt.xticks(rotation=45); plt.show()

    if ch=='3':
        plt.figure(); plt.pie([completed,pending], labels=['Completed','Pending'], autopct='%1.1f%%'); plt.title('Completed vs Pending'); plt.show()

