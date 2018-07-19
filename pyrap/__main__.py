import argparse
import pwd
import re
import time

from pyrap.pyrap import copy_skel
from pyrap.pyrap import pyrap
from pyrap.ui import ask


def get_users():
    """
    Return a dictionary of users. User name is the key, home directory path is
    the value.
    """
    users = {}
    for p in pwd.getpwall():
        user = p[0]
        home = p[5]
        regex = "^_|admin|daemon|guest|local|nobody|root"
        if not(re.match(regex, user, re.IGNORECASE)):
            users[user] = home

    return users


def get_args():
    """
    Return a list of valid arguments.
    """
    parser = argparse.ArgumentParser(description='\
    Backup or restore users to an rsync server.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-b", "--backup", action="store_true",
                       help="Backup users to rsync server or path.")
    group.add_argument("-r", "--restore", action="store_true",
                       help="Restore users on from last backup.")
    parser.add_argument("-u", "--users", action="store_true",
                        help="Automate user selection.")
    parser.add_argument("-x", "--excludes", action="store_true",
                        help="Automate excludes selection.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="Increase output verbosity.")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="Run silently.")
    parser.add_argument("url", type=str, help="A valid rsync url.")
    return parser.parse_args()


def main():
    users = get_users()
    args = get_args()

    if len(users) > 0:
        print("Users: "+(', '.join(users.keys())))
        for user, home in users.items():
            if args.backup:
                copytype = "backup"
                date = time.strftime("%Y-%m-%d")
                src = home + "/"
                dest = args.url + "/Users/" + user + "/" + date
                copy_skel(date, user, args.url)
            elif args.restore:
                copytype = "restore"
                upath = (args.url + "/Users/" + user)
                date = sorted(os.listdir(upath), reverse=True)[0]
                src = upath + "/" + date + "/"
                dest = home

            if args.users:
                pyrap(src, dest, args.excludes)
            else:
                question = "\n" + copytype.title() + " " + user + "? "
                if ask(question):
                    pyrap(src, dest, args.excludes)
    else:
        print("No users to %s" % copytype)


if __name__ == '__main__':
    main()
