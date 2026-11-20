"""Paths for the plotting scripts, read from the repo's .env file.

RES and DATA default to results/ and data/ inside the repo, so the graph
scripts work even without a .env file.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            if value:
                env[key.strip()] = os.path.expandvars(os.path.expanduser(value))
    return env


_env = _load_env(os.path.join(REPO, ".env"))
_env.update({k: os.environ[k] for k in ("RES", "DATA") if os.environ.get(k)})
RES = _env.get("RES", os.path.join(REPO, "results"))
DATA = _env.get("DATA", os.path.join(REPO, "data"))
os.makedirs(DATA, exist_ok=True)
