def analytics_cli(user):
    print('--- Analytics ---')
    total = user.total_hours()
    completed = user.total_productive_hours()
    completion = user.completion_rate()
    avg_cat = user.average_time_per_category()
    score = user.productivity_score()
    print(f'Total hours: {total}')
    print(f'Completed hours: {completed}')
    print(f'Completion rate: {completion:.2f}%')
    print('Average per category:')
    for k,v in avg_cat.items():
        print(f' - {k}: {v:.2f}h')
    print(f'Productivity score: {score:.2f}%')
    if score>80:
        print('Excellent')
    elif score>50:
        print('Good')
    else:
        print('Keep improving')

