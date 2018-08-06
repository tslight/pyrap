import curses
import os
import re
import subprocess
import time

from yorn import ask
from treepick import pick


def chkdir(path):
    """
    Check if a directory exists and if not try to create it.
    """
    if (not(os.path.isdir(path))):
        try:
            os.makedirs(path)
        except OSError:
            print("Could not create directory.")


def get_last(path):
    """
    Find the last backup given a directory with dated child directories.
    """
    if path.startswith('rsync://'):
        rsync = "rsync" + " " + path + "/ | "
        pipe = "awk '{print $5}' | sed '/\./d' | sort -nr | awk 'NR==2'"
        return subprocess.Popen(rsync + pipe,
                                shell=True, stdout=subprocess.PIPE,
                                universal_newlines=True).stdout.read().strip()
    else:
        return sorted(os.listdir(path), reverse=True)[0]


def get_excludes(old_excludes, path):
    """
    Takes a path as an argument and returns a list of child paths that the user
    has selected.
    """
    os.system('cls') if os.name == 'nt' else os.system('clear')
    # merge excludes, list + set removes duplicates.
    new_excludes = curses.wrapper(
        pick, path, hidden=True, relative=True, picked=old_excludes)
    excludes = list(set(old_excludes + new_excludes))
    if excludes:
        print("\nSelected excludes:\n\n"+('\n'.join(sorted(excludes))))
    else:
        print("\nNo excludes selected.")
    if ask("Accept and continue? "):
        return excludes
    else:
        excludes = get_excludes(excludes, path)
    return excludes


def mkexcludes(automate_excludes, src):
    from textwrap import dedent
    """
    Create valid rsync exclude arguments from a list of paths.
    """
    excludes = [
        '.*',
        '*.ost',
        '*.pst',
        '.DS_Store',
        '.localized',
        'Applications',
        'Library',
        'Downloads',
        'desktop.ini',
    ]
    xargs = []

    if not automate_excludes:
        while True:
            os.system('cls') if os.name == 'nt' else os.system('clear')

            head = "Default Excludes:"
            msg = """
            Please select from the following options:

            (c)ontinue using default excludes listed above.
            (a)dd to excludes listed above using treepick.
            (d)elete all excludes and continue with no excludes.
            (r)emove all excludes and select different excludes.
            """
            msg = dedent(msg).strip()
            print("\n{}\n\n{}\n\n{}\n".format(head, "\n".join(excludes), msg))
            ans = input("\n----> ")
            al = ans.lower()
            if re.match('^c(ontinue)?$', al):
                break
            elif re.match('^a(dd)?$', al):
                excludes = get_excludes(excludes, src)
                break
            elif re.match('^d(elete)?$', al):
                excludes = []
                break
            elif re.match('^r(emove)?$', al):
                excludes = []
                excludes = get_excludes(excludes, src)
                break
            else:
                print("%s is invalid. Enter (y)es, (n)o or (q)uit." % ans)

    for x in excludes:
        if x.startswith(src):
            x = x.replace(src, '')
        xargs.append('--exclude="' + x + '"')
    return xargs


def run(type_, user, automate_excludes, opts, src, dest):
    excludes = mkexcludes(automate_excludes, src)
    rargs = " ".join(opts) + " ".join(excludes)
    cmd = "rsync" + " " + rargs + " " + src + " " + dest
    print("\nStarting %s of %s..." % (type_, user))
    subprocess.call(cmd, shell=True)
    print("\rFinished %s of %s." % (type_, user))


def cpskel(opts, date, user, url):
    """
    Create and sync skeleton directory structure. Necessary for first run to
    rsync server as there's no way to run mkdir -p on the remote.
    """
    parent = "/tmp/rsync/"
    skel = parent + "Users/" + user + "/" + date
    chkdir(skel)
    cmd = "rsync " + ' '.join(opts) + " --quiet " + parent + " " + url
    subprocess.call(cmd, shell=True)


def process(args, users):
    if len(users) > 0:
        print("\nUsers: "+(', '.join(users.keys())))
        for user, home in users.items():
            opts = [
                '--archive',
                '--human-readable',
                '--info=progress2',
                '--no-inc-recursive',
            ]
            if args.backup:
                type_ = "backup"
                date = time.strftime("%Y-%m-%d")
                src = home + "/"
                dest = args.url + "/Users/" + user + "/" + date
                cpskel(opts, date, user, args.url)
                lastbkup = get_last(args.url + "/Users/" + user)
                opts.append('--link-dest="../' + lastbkup + '" ')
            elif args.restore:
                type_ = "restore"
                upath = (args.url + "/Users/" + user)
                date = get_last(upath)
                src = upath + "/" + date + "/"
                dest = home
            if args.users:
                run(type_, user, args.excludes, opts, src, dest)
            else:
                question = type_.title() + " " + user + "? "
                if ask(question):
                    run(type_, user, args.excludes, opts, src, dest)
    else:
        print("No users to %s" % type_)
