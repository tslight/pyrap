import argparse
import curses
import os
import subprocess

from .ui import ask
from treepick.pick import pick

RSYNC_OPTS = [
    '--archive ',
    '--human-readable '
]

DEFAULT_EXCLUDES = [
    '--exclude=".localized" '
    '--exclude=".DS_Store" '
    '--exclude="desktop.ini" ',
    '--exclude="*.ost" ',
    '--exclude="*.pst" ',
    '--exclude="*spotify*" ',
    '--exclude="*Spotify*" '
]


def check_dir(path):
    """
    Check if a directory exists and if not try to create it.
    """
    if (not(os.path.isdir(path))):
        try:
            os.makedirs(path)
        except OSError:
            print("Could not create directory.")


def get_excludes(path, hidden):
    """
    Takes a path as an argument and returns a list of child paths that the user
    has selected.
    """
    excludes = curses.wrapper(pick, path, hidden)
    if len(excludes) > 0:
        print("\nSelected excludes:\n"+('\n'.join(excludes)))
        if ask("\nAccept and use excludes? "):
            return excludes
        else:
            excludes = get_excludes(path, hidden)
    else:
        if not(ask("\nNo excludes selected. Continue? ")):
            excludes = get_excludes(path, hidden)
    return excludes


def copy_skel(date, user, url):
    parent = "/tmp"
    skel = parent + "/Users/" + user + "/" + date
    check_dir(skel)
    cmd = "rsync " + ' '.join(RSYNC_OPTS) + " --quiet " + skel + " " + url
    subprocess.call(cmd, shell=True)


def pyrap(src, dest, automate_excludes):
    hidden = True
    if automate_excludes:
        cmd = "rsync " + " ".join(RSYNC_OPTS) + \
            " ".join(DEFAULT_EXCLUDES) + " " + src + " " + dest
        subprocess.call(cmd, shell=True)
    else:
        excludes = get_excludes(src, hidden)
        # list + set removes duplicates.
        excludes = excludes + list(set(excludes + DEFAULT_EXCLUDES))
        cmd = "rsync " + " ".join(RSYNC_OPTS) + \
            " ".join(excludes) + src + " " + dest
        subprocess.call(cmd, shell=True)
