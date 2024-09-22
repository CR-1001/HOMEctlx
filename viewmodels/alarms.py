# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for alarms and timers.
"""

from datetime import datetime, timedelta
import services.lightctlwrapper as lw
import services.scheduler as sd
from services.lightstates import States
import services.meta as m


def ctl(args:dict={}) -> list[m.view]:
    """ Starting point."""

    states_txt = lw.exec(f"state", brief=False)
    states = States('\n'.join(states_txt.split('\n')[1:]))
    names = sorted([s.name for s in states.items])

    default = datetime.now() + timedelta(hours=8)

    select_devices = m.select_many("devices", \
        list(map(lambda d: m.choice(d), names)), [], "devices")

    now = f"Server time:\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"

    forms = [*scheduled()]
    
    # timer
    mins = [*range(1, 20, 1), *range(20, 60, 5), *range(60, 241, 10)]
    forms.append(
        m.form("timer", "set timer", [
            m.select("mins", list(map(lambda i: m.choice(i), mins)),\
                None, "minutes"),
            select_devices,
            m.execute("alarms/timer", "set")
        ]))
    
    # alarm
    hours   = list(map(lambda h: str(h).zfill(2), range(0, 24)))
    hour    = str(default.hour).zfill(2)
    minutes = list(map(lambda h: str(h).zfill(2), range(0, 60, 5)))
    minute  = str(int(default.minute / 10) * 10).zfill(2)
    
    forms.append(
        m.form("alarmhm", "set alarm", [
            m.select("hour", 
                list(map(lambda h: m.choice(h), hours)),
                m.choice(hour), "hour"), 
            m.select("minute",  
                list(map(lambda i: m.choice(i), minutes)), 
                m.choice(minute), "minute"),
            select_devices,
            m.execute("alarms/alarmhm", "set")
        ]))
    
    return [m.view("_body", "timer and alarm", forms)]


def alarmhm(hour, minute, devices):
    """ Alarm."""
    return alarm(f"{hour}:{minute}", devices)


def alarm(time, devices:list[str]):
    """ Alarm."""
    current_time = datetime.now().time()
    target_time = datetime.strptime(time, "%H:%M").time()
    today = datetime.today()
    target_datetime = datetime.combine(today, target_time)
    # next day
    if target_time < current_time: target_datetime += timedelta(days=1)
    time_difference = target_datetime \
        - datetime.combine(today, current_time)
    minutes = time_difference.total_seconds() / 60
    return timer(minutes, devices)


def timer(mins:int, devices:list[str]):
    """ Timer."""
    if len(devices) == 0: return [m.error("Select at least one device.")]
    mins = int(mins)
    now = datetime.now()
    target = now + timedelta(minutes=mins)
    names_str = ", ".join((sorted(devices)))
    id = f"{target.strftime('%Y-%m-%d %H:%M')} on {names_str}"
    def _blink(): lw.blink(devices)
    sd.execute_delayed_background(target, _blink, id)
    return scheduled()


def scheduled(stop:str=None):
    """ Schedules a timer."""
    if stop != None: sd.terminate(stop)
    running = list(map(lambda r: m.choice(r), sd.running()))
    scheduled = m.triggers("alarms/scheduled", "stop", running)\
        if len(running) > 0 else m.label("nothing scheduled")
    return [m.form("scheduled", "running alarms and timers", [
        scheduled], True)]