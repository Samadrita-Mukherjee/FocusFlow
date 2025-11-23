import argparse
from gui import run_gui
from user_system import register, login

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', action='store_true', help='Run CLI mode (text)')
    args = parser.parse_args()

    if args.cli:
        # simple CLI flow
        while True:
            print('\n1) Login\n2) Register\n3) Exit')
            c = input('Choose: ').strip()
            if c=='1':
                user = login()
                if user:
                    from cli.summary_cli import show_daily_summary
                    from cli.task_cli import add_task_cli, view_tasks_cli, update_task_cli, delete_task_cli
                    from cli.analytics_cli import analytics_cli
                    from cli.visualize_cli import visualize_cli
                    from cli.backup_cli import backup_cli, restore_cli

                    show_daily_summary(user)
                    while True:
                        print('\n--- Menu ---')
                        print('1. Add Task\n2. View Tasks\n3. Update Task\n4. Delete Task\n5. Analytics\n6. Visualize\n7. Backup\n8. Restore\n9. Logout\n0. Exit')
                        ch = input('Choose: ').strip()
                        if ch=='1': add_task_cli(user)
                        elif ch=='2': view_tasks_cli(user)
                        elif ch=='3': update_task_cli(user)
                        elif ch=='4': delete_task_cli(user)
                        elif ch=='5': analytics_cli(user)
                        elif ch=='6': visualize_cli(user)
                        elif ch=='7': backup_cli(user)
                        elif ch=='8': restore_cli(user)
                        elif ch=='9': break
                        elif ch=='0': exit(0)
                        else: print('Invalid')
            elif c=='2':
                register()
            elif c=='3':
                break
            else:
                print('Invalid')
    else:
        # default: launch GUI
        run_gui()

if __name__ == '__main__':
    main()
