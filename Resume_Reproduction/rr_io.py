"""Writing results: every table carries its sample statement and a JSON sidecar.

The CSV opens with '# key: value' lines (read back with pandas.read_csv(path, comment='#')) so
the instruments, dates and conventions travel with the numbers; the sidecar adds the git commit
and the run time.
"""
import datetime
import json
import os
import subprocess

import config as C


def git_hash():
    try:
        return subprocess.check_output(["git", "-C", C.ROOT, "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


def write_result(df, name, meta=None, index=True):
    """Write results/<name>.csv with a header block, plus results/<name>.json."""
    os.makedirs(C.RESULTS, exist_ok=True)
    meta = dict(meta or {})
    meta.setdefault("sample", C.SAMPLE_STATEMENT)
    path = os.path.join(C.RESULTS, f"{name}.csv")
    with open(path, "w") as fh:
        for k, v in meta.items():
            fh.write(f"# {k}: {v}\n")
        df.to_csv(fh, index=index)
    side = dict(meta, git=git_hash(), written=datetime.datetime.now().isoformat(timespec="seconds"),
                rows=int(len(df)))
    with open(os.path.join(C.RESULTS, f"{name}.json"), "w") as fh:
        json.dump(side, fh, indent=2, default=str)
    return path
