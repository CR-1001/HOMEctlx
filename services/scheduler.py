# This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Schedules tasks, will spawn threads and handles cancellation.
"""

from datetime import datetime
import logging
import sched
from threading import Thread
import time
from typing import Callable


log = logging.getLogger(__file__)


def init(fileaccess):
    """ Sets the fileaccess."""
    global fa
    fa = fileaccess
    tasks = running()
    if len(tasks) > 0: log.warning(\
        f"Incomplete scheduled tasks deleted: {', '.join(tasks)}")
    fa.clean_file(["temp", "scheduled-tasks"], lambda _: True)


def execute_delayed_background(datetime:datetime, func:Callable, id:str):
    """ Delays an execution (not blocking)."""
    Thread(target=execute_delayed, args=[datetime, func, id]).start()


def execute_delayed(datetime:datetime, func:Callable, id:str):
    """ Delays an execution (blocking)."""
    def _run():
        if terminated(id): 
            log.info(f"Task '{id}' got terminated before it run.")
            return
        try:    func()
        except: log.error(f"Task '{id}' not successfully completed.")
        terminate(id)
        log.info(f"Task '{id}' marked as terminated.")
    append(id)
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enterabs(datetime.timestamp(), 1, _run)
    scheduler.run(blocking=True)
    log.info(f"Task '{id}' got scheduled for {datetime}.")


def append(id):
    """ Appends the ID to the list of scheduled tasks."""
    fa.update_file(["temp", "scheduled-tasks"], id + "\n", False)


def running():
    """ Returns the currently scheduled tasks."""
    return fa.clean_lines(fa.read_file(["temp", "scheduled-tasks"]))


def terminate(id):
    """ Removes the scheduled task from the list (either to stop it or 
    because it has regularly finished.)"""
    id = id.strip("\n")
    fa.clean_file(["temp", "scheduled-tasks"], lambda l: l == id)


def terminated(id):
    """ Checks whether a task was terminated."""
    id = id.strip("\n")
    return id not in running()