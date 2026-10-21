# Backup archive

This directory is retained only on `backup`. The public code, paper results,
and online demo live outside it. Release cleanup is staged on `backup` before
the public files are synchronized to `main`.

[`figure-sources/`](figure-sources/) holds editable figure sources and earlier
exports. The currently displayed system diagram is
[`../experiments/figures/fig0-main.jpg`](../experiments/figures/fig0-main.jpg).

[`mirex-submission/`](mirex-submission/) preserves the complete tracked tree
of the former `mirex_submission` branch at
`04ea2db` (including its existing figure archive, submission weights,
training scripts, experiment results, and handoff notes). Its original Git
history is also retained by this branch's merge commit. Historical documents
and configurations in the snapshot describe that submission, not the current
public interface.

Make shared maintenance changes outside `archive/` and verify them on
`backup`. When promoting a cleanup, synchronize only paths outside `archive/`
to `main`; do not merge archive additions into the public branch. A commit
that also changes the archive must not be cherry-picked wholesale. To check
public-file synchronization:

```sh
git diff main backup -- . ':!archive'
```

To run the original figure archive checker against its preserved snapshot:

```sh
python archive/mirex-submission/archive/verify_archive.py
```
