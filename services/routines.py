# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Manages start-up routines.
"""

import logging
import subprocess
from typing import Generator


log = logging.getLogger(__file__)


def init(routines_config:dict):
    """ Sets the routines."""
    global cmds
    cmds = routines_config
    for key, _ in get("init"): exec(key)


def get(exec_flags:list=None) -> Generator:
    """ Gets the routines by execution flag."""
    for key, cmd in cmds.items():
        exec_info = cmd.get("exec", {})
        if exec_flags == None:
            yield key, cmd
        else:
            for ef in exec_flags:
                if exec_info.get(ef):
                    yield key, cmd
                    break


def exec(key:str):
    """ Executes the routine."""
    try:
        cmd = cmds[key]
        command = [cmd["command"]]
        result = subprocess.run(
            command, capture_output=True, text=True, shell=True)
        out = result.stdout.strip()
        err = result.stderr.strip()
        if err not in ['', None] and out in ['', None]:
            log.warning(f"Executed:\n{command}\nResult:\n{out}")
            return err
        return out
    except Exception as e:
        log.error(e)
        return f"An error occurred: {e}"
