import curses
import os
import subprocess
import time

from .ui import ask
from treepick.pick import pick


def check_dir(path):
    """
    Check if a directory exists and if not try to create it.
    """
    if (not(os.path.isdir(path))):
        try:
            os.makedirs(path)
        except OSError:
            print("Could not create directory.")


def get_last(path):
    if path.startswith('rsync://'):
        rsync = "rsync" + " " + path + "/ | "
        pipe = "awk '{print $5}' | sed '/\./d' | sort -nr | awk 'NR==2'"
        return subprocess.Popen(rsync + pipe,
                                shell=True, stdout=subprocess.PIPE,
                                universal_newlines=True).stdout.read()
    else:
        return sorted(os.listdir(path), reverse=True)[0]


def get_excludes(excludes, path, hidden):
    """
    Takes a path as an argument and returns a list of child paths that the user
    has selected.
    """
    # merge excludes, list + set removes duplicates.
    excludes = list(set(excludes + curses.wrapper(pick, path, hidden)))
    if len(excludes) > 0:
        print("\nSelected excludes:\n"+('\n'.join(excludes)))
        if ask("\nAccept and use excludes? "):
            return excludes
        else:
            excludes = list(set(excludes + curses.wrapper(pick, path, hidden)))
    else:
        if not(ask("\nNo excludes selected. Continue? ")):
            excludes = list(set(excludes + curses.wrapper(pick, path, hidden)))
    return excludes


def copy_skel(opts, date, user, url):
    parent = "/tmp"
    skel = parent + "/Users/" + user + "/" + date
    check_dir(skel)
    cmd = "rsync " + ' '.join(opts) + " --quiet " + skel + " " + url
    subprocess.call(cmd, shell=True)


def pyrap(opts, src, dest, automate_excludes):
    excludes = [
        '*.ost',
        '*.pst',
        '.DS_Store',
        '.localized',
        'desktop.ini',
        '*spotify*',
        '*Spotify*',
    ]

    hidden = True
    if not automate_excludes:
        excludes = get_excludes(excludes, src, hidden)
    rargs = "rsync " + " ".join(opts) + " ".join(excludes)
    cmd = rargs + " " + src + " " + dest
    subprocess.call(cmd, shell=True)


def process(args, users):
    opts = [
        '--archive ',
        '--human-readable ',
    ]

    if len(users) > 0:
        print("Users: "+(', '.join(users.keys())))
        for user, home in users.items():
            if args.backup:
                copytype = "backup"
                date = time.strftime("%Y-%m-%d")
                src = home + "/"
                dest = args.url + "/Users/" + user + "/" + date
                copy_skel(opts, date, user, args.url)
                opts.append('--link-dest=' +
                            get_last(args.url + "/Users/" + user) + ' ')
            elif args.restore:
                copytype = "restore"
                upath = (args.url + "/Users/" + user)
                date = get_last(upath)
                src = upath + "/" + date + "/"
                dest = home

            if args.users:
                pyrap(opts, src, dest, args.excludes)
            else:
                question = "\n" + copytype.title() + " " + user + "? "
                if ask(question):
                    pyrap(opts, src, dest, args.excludes)
    else:
        print("No users to %s" % copytype)
