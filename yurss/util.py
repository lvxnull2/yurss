import runpy
from datetime import datetime, timezone

from . import config


def load_config(path):
    vars = runpy.run_path(path)

    for k, v in vars.items():
        if k.startswith("_"):
            continue
        setattr(config, k, v)

    return config

def now():
    return datetime.now(timezone.utc)
