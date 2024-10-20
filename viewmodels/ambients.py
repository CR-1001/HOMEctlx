# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for ambients.
"""

from datetime import datetime
from random import choice
import time
import services.lightctlwrapper as lw
import services.ambinterpreter as ami
from services.lightstates import State, States
import services.meta as m


def ctl() -> list[m.view]:
    """ Starting point."""
    
    ambients = ami.all()
    ambients_and_macros = ami.all(True)

    forms = []

    forms_running = running()
    forms.append(forms_running[0])

    if len(ambients) > 0:
        forms.append(m.form("a-run", "run", [
            m.triggers("ambients/run", "name", m.choice.makelist(ambients))
        ], True, False))

    if len(ambients_and_macros) > 0:
        forms.append(m.form("a-edit", "edit", [
            m.triggers("ambients/edit", "name", m.choice.makelist(ambients_and_macros))
        ]))

    forms.append(
        m.form("a-create", "create", [
            m.text("name", _name_suggestion()),
            m.execute("ambients/edit", "create"),
        ]))
    
    forms += forms_running[1:]

    return [
        m.view("_body", "ambients", forms), 
        m.header([m.applink("/lights/ctl", "💡 lights")])]


def running():
    """ Current states."""
    running = ami.running()
    if len(running) > 0:
        def _desc(a):
            started = datetime.fromisoformat(a['start'])\
                .strftime('%Y-%m-%d %H:%M')
            return f"{a['desc']} (started: {started})" 
        triggers = [m.choice(a['id'], _desc(a)) \
            for a in running]
        field = m.triggers("ambients/stop", "name", triggers)
    else:
        field = m.label("no running ambients")
    udpate_delay = 5000 if len(running) == 0 else 2000
    return [
        m.form("a-stop", "running", 
            [field, m.autoupdate("ambients/running", udpate_delay)], 
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
        fields.append(m.light("ambients/set_state", grp))

    if len(fields_on) == 0: fields_on.append(m.label("no active devices"))

    if len(fields_off) == 0: fields_off.append(m.label("all devices active"))
    else: 
        fields_off.insert(0, m.title("inactive"))
        fields_off.insert(0, m.space(1))

    fields_off.append(m.space(1))
    
    return [m.form("a-states", "active", 
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


def edit(name:str, tokens:str=None):
    """ Edit an ambient."""
    content = ami.single(name)
    forms = [
        m.form(None, None, [
            m.text("name", name, "name"),
            m.text_big("content", content, "ambiscript"),
            m.execute_params("ambients/change", "save and validate", 
                {'run': False, 'check': True}),
            m.execute_params("ambients/change", "save and run", 
                {'run': True, 'check': True}),
        ], table=False),
        m.form(None, None, [
            m.execute("ambients/ctl", "go back"),
            m.space(1)
        ], table=False),
        m.form(None, "built-in", _builtin()),
        m.form(None, "delete", [
            m.hidden("name", name),
            m.execute("ambients/delete", "delete"),
        ])]
    if tokens != None:
        forms.insert(2, m.form(None, 'validation', [
            m.execute_params("ambients/edit", "clear", 
                {'name': name}),
            m.label("the ambiscript produced the following instructions:"),
            m.text_big_ro(None, tokens)]))

    return [m.view("_body", f"edit ambient: {name}", forms)]


def change(name:str, content:str, run:bool=False, check:bool=False):
    """ Changes the ambient."""
    ami.change(name, content)
    tokens = None
    if run in ['True', True]: ami.run(name)
    if check in ['True', True]:
        try: tokens = '\n'.join(ami.prepare(content))
        except Exception as e: tokens = f'{e}'
    return edit(name, tokens)


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
    keys = predefined.keys()
    padding = len(max(keys, key=lambda k: len(k))) + 1
    builtin = "\n".join(
        [f"{k.rjust(padding)}\t= {predefined[k]}" for k in keys])
    return [
        m.label("base syntax: ID PWR HUE SAT BRI"),
        m.label("predefined variables:"),
        m.text_big_ro('', builtin),
        m.label("preprocessed macros:"),
        m.text_big_ro('', macros),
        m.space(2)]


def _name_suggestion():
    """ Suggestes a name for the ambient."""
    now = datetime.now()
    name_suggestion = \
        "morning" if now.hour > 4 and now.hour < 12 \
        else "afternoon" if now.hour >= 12 and now.hour < 19 \
        else "night"
    return f'{name_suggestion} {choice("🍌🍉🍇🍓🍔🍕🍦🍷🍬🍭")}'