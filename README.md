# BACKUP & RESTORE SCRIPTS

Backup or restore all user profiles on a host.

## USAGE

```
usage: pyrap [-h] (-b | -r) [-u] [-x] [-v | -q] url

Backup or restore users to an rsync server.

positional arguments:
  url             A valid rsync url.

optional arguments:
  -h, --help      show this help message and exit
  -b, --backup    Backup users to rsync server or path.
  -r, --restore   Restore users on from last backup.
  -u, --users     Automate user selection.
  -x, --excludes  Automate excludes selection.
  -v, --verbose   Increase output verbosity.
  -q, --quiet     Run silently.
```

## ARGUMENTS

**[URL]**

Takes an rsync url as an argument:

`rsync://user@host:port/path/to/PARENT/of/Users`

Or alternatively, any mountpoint will work:

`/Volumes/Backups`

## PITFALLS & CAVEATS

**THE PATH ON THE REMOTE HOST MUST POINT TO PARENT OF USERS, NOT USERS!**

Once mounted the mountpoint should contain the Users directory underneath it.

The script backups to or restores from the following directory layout underneath
the mountpoint:

`/mountpoint/Users/user.name/date`

And logs to:

`/mountpoint/Logs/CopyType/user.name/date.log`

*Where CopyType equals either Backup or Restore.*

**If this layout does not exist it will be created under the mountpoint.**

User, group and permissions will be retained and each backup will be hard-linked
against the last to save space and mimic the functionality of Time Machine.

<https://blog.interlinked.org/tutorials/rsync_time_machine.html>

It's also worth pointing out that for the time being preserving extended
attributes is not supported.

## EXAMPLES

To backup from /Users to a rsync server, without prompting for each user:

`pyrap -bu rsync://user@host:port/backups`

To restore from /Users to a rsync server, with increased verbosity:

`pyrap -rv rsync://user@host:port/backups`
