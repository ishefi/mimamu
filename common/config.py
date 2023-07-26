#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING

import os
import sys
from omegaconf import OmegaConf
from pathlib import Path

if TYPE_CHECKING:
    from typing import Any

thismodule = sys.modules[__name__]

conf = OmegaConf.create()
if (config_path := Path(__file__).parent.parent.resolve() / "config.yaml").exists():
    conf.merge_with(OmegaConf.load(config_path))
if yaml_str := os.environ.get("YAML_CONFIG_STR"):
    conf.merge_with(OmegaConf.create(yaml_str))
for k, v in conf.items():
    setattr(thismodule, str(k), v)


def __getattr__(name) -> Any:
    pass
