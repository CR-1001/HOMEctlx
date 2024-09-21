# This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for ambients.
"""

from datetime import datetime
import time
import services.lightctlwrapper as lw
import services.ambinterpreter as ami
from services.lightstates import State, States
import services.meta as m


def ctl(args:dict={}) -> list[m.view]:
    """ Starting point."""
    
    states_now_str_devs = lw.exec(f"state", brief=False).split('\n')[1:]
    all = ami.all()

    forms = []

    forms_running = running()
    forms.append(forms_running[0])

    if len(all) > 0:
        forms.append(m.form("a-run", "set ambient", [
            m.triggers("ambients", "run", "name", m.choice.makelist(all)),
            m.space(1)
        ], True, False))

    forms += forms_running[1:]

    if len(all) > 0:
        forms.append(m.form("a-edit", "edit ambient", [
            m.select("name", m.choice.makelist(all)),
            m.execute("ambients", "edit", "edit")
        ]))

    forms.append(
        m.form("a-create", "create ambient", [
            m.text("name", _name_suggestion()),
            m.execute("ambients", "edit", "create")
        ]))

    return [
        m.view("_body", "ambients", forms), 
        m.header([m.applink("/lights/ctl", "💡 lights")])]


def running():
    """ Current states."""
    running = ami.running()
    if len(running) > 0:
        field = m.triggers("ambients", "stop", "name", m.choice.makelist(running))
    else:
        field = m.label("no running ambients")
    udpate_delay = 5000 if len(running) == 0 else 2000
    return [
        m.form("a-stop", "running ambients", 
            [field, m.autoupdate("ambients", "running", udpate_delay)], 
            True, False),
        *states()]


def states():
    """ Current states."""
    states = lw.states_grouped("grp")
    sorted_groups = sorted(states, key=lambda g: (g.head.pwr == "off", g.head.name))
    
    fields_on = []
    fields_off = []

    for grp in sorted_groups:
        fields = fields_on if grp.head.pwr != "off" else fields_off
        fields.append(m.light("ambients", "set_state", grp))

    if len(fields_on) == 0: fields_on.append(m.label("no devices turned on"))

    if len(fields_off) == 0: fields_off.append(m.label("all devices turned on"))
    else: 
        fields_off.insert(0, m.title("inactive devices"))
        fields_off.insert(0, m.space(1))

    fields_off.append(m.space(1))
    
    return [m.form("a-states", "active devices", 
        [*fields_on, *fields_off], True, False)]


def set_state(type:str, id:str, value:str, attr:str) -> list[m.view]:
    """ Set states."""
    ids = [id] if type != "grp" else lw.get_ids_in_group(id)
    lw.set_attributes(ids, attr, value)
    return running()


def set(names, pwr="off", hue:int=-1, sat:int=-1, bri:int=-1):
    """ Sets the device values."""

    if pwr not in ["on", "off"]: raise Exception()

    hue = "-" if hue in [-1, "-1"] else int(hue)
    sat = "-" if sat in [-1, "-1"] else int(sat)
    bri = "-" if bri in [-1, "-1"] else int(bri)

    states = lw.states()

    if names == "*": ids = [int(s.id) for s in states]
    else:            ids = [int(s.id) for s in states if s.name in names]

    values = f"{pwr} {hue} {sat} {bri}"
    for id in ids: lw.set_state(State(f"{id} {values}"))

    states_new = lw.exec(f'state', brief=False)
    return [m.text_big_ro("s-resp", f"FOR {ids}\nSET {values}\n\n{states_new}")]


def create(states, name):
    """ Creates an ambient list, device states that can be restored."""
    ami.create(name, states)
    return ctl()


def edit(name):
    """ Edit an ambient."""
    content = ami.single(name)
    return [
        m.view("_body", f"edit ambient: {name}", [
            m.form(None, None, [
                m.text("name", name, "name"),
                m.label("ID PWR HUE SAT BRI"),
                m.text_big("content", content, "script"),
                m.execute("ambients", "change", "change ambient"),
            ], table=False),
            m.form(None, None, [
                m.hidden("name", name),
                m.execute("ambients", "delete", "delete ambient"),
            ], table=False),
            m.form(None, None, [
                m.execute("ambients", "ctl", "go back"),
            ], table=False),
            m.form(None, "built-in", _builtin(), True, False)])]


def change(name:str, content:str):
    """ Changes the ambient."""
    ami.change(name, content)
    return edit(name)


def delete(name:str):
    """ Deletes the ambient."""
    ami.delete(name)
    return ctl()


def stop(name):
    """ Stops a running ambient."""
    ami.terminate(name)
    return ctl()


def run(name):
    """ Restores an ambient."""
    ami.run(name)
    return ctl()


def _builtin():
    """ Returns the built-in variables."""
    predefined = ami.predefined()
    macros = ami.macros()
    builtin = "\n".join([f"{k}\t=\t{predefined[k]}" for k in predefined.keys()])
    return [m.text_big_ro('', builtin), m.text_big_ro('', macros)]


def _name_suggestion():
    """ Suggestes a name for the ambient."""
    current_hour = datetime.now().hour
    name_suggestion = \
        "morning" if current_hour > 4 and current_hour < 12 \
        else "afternoon" if current_hour >= 12 and current_hour < 19 \
        else "night"
    return name_suggestion