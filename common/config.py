#!/usr/bin/env python
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from omegaconf import OmegaConf

if TYPE_CHECKING:
    from typing import Any

thismodule = sys.modules[__name__]

conf = OmegaConf.create()
if (config_path := Path(__file__).parent.parent.resolve() / "config.yaml").exists():
    conf.merge_with(OmegaConf.load(config_path))
if yaml_str := os.environ.get("YAML_CONFIG_STR"):
    conf.merge_with(OmegaConf.create(yaml_str))
for var, val in os.environ.items():
    if var.startswith("MMM_"):
        conf[var[4:]] = val
for k, v in conf.items():
    setattr(thismodule, str(k), v)


def __getattr__(name: str) -> Any:
    pass
