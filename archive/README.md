# Backup archive

The `backup` branch shares its active files with `main`. Only this directory
is extra; public inference, tests, paper results, and the online demo use the
files outside it.

[`mirex-submission/`](mirex-submission/) preserves the complete tracked tree
of the former `mirex_submission` branch at
`04ea2db` (including its existing figure archive, submission weights,
training scripts, experiment results, and handoff notes). Its original Git
history is also retained by this branch's merge commit. Historical documents
and configurations in the snapshot describe that submission, not the current
public interface.

Make shared maintenance changes outside `archive/`, verify them on `backup`,
and cherry-pick those commits onto `main`. Keep archive-only commits on
`backup`. To check synchronization:

```sh
git diff main backup -- . ':!archive'
```

To run the original figure archive checker against its preserved snapshot:

```sh
python archive/mirex-submission/archive/verify_archive.py
```
