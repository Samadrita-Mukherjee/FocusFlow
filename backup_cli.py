def backup_cli(user):
    print('Creating backup...')
    path = user.backup()
    if path:
        print('Backup created at', path)
    else:
        print('No backup created')

def restore_cli(user):
    print('Enter path to backup CSV:')
    p = input('Path: ').strip()
    if not p:
        print('No path')
        return
    try:
        user.restore(p)
        print('Restored')
    except Exception as e:
        print('Failed to restore:', e)

