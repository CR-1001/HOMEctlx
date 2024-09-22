# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Interprets ambiscript and sets device states.
"""

from ast import Module
from functools import partial
from jinja2 import Environment, nodes, select_autoescape
from datetime import datetime
import logging
import random
import re
from threading import Thread
from time import sleep
from services.lightstates import State


log = logging.getLogger(__file__)


def init(fileaccess, lightctlwrapper):
    """ Sets fileaccess and lightctlwrapper."""
    global lw
    global fa 
    lw = lightctlwrapper
    fa = fileaccess
    tasks = running()
    if len(tasks) > 0: log.warning(\
        f"Incomplete running ambients deleted: {', '.join(tasks)}")
    fa.clean_file(["temp", "running-ambients"], lambda _: True)


def all(include_macros:bool=False):
    """ Lists the ambients."""
    ambients, _ = fa.list_share_files(["ambients"], True)
    if not include_macros:
        ambients = [a for a in ambients if not a.startswith('macros/')]
    return ambients

def single(name):
    """ Returns a single ambient."""
    return fa.read_file(["ambients", name])


def create(name, content):
    """ Creates an ambient."""
    fa.create_file(["ambients", name], content)


def change(name, content):
    """ Changes an ambient."""
    fa.update_file(["ambients", name], content, True)


def delete(name):
    """ Deletes an ambient."""
    fa.delete_file(["ambients", name])


def running() -> list[str]:
    """ Returns the currently running ambients."""
    return fa.clean_lines(
        fa.read_file(["temp", "running-ambients"]))


def terminate(id:str):
    """ Removes the running ambient from the list (either to stop it or 
    because it has regularly finished.)"""
    id = id.strip("\n")
    fa.clean_file(["temp", "running-ambients"], lambda l: l == id)


def terminated(id:str):
    """ Checks whether an ambient was terminated."""
    id = id.strip("\n")
    return id not in running()


def run(name):
    """ Restores an ambient."""
    started = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
    id = f"{name} / started: {started}\n"
    fa.update_file(["temp", "running-ambients"], id, False)
    Thread(target=_run, args=[id, name]).start()


def _run(id, name, states_old:list[State]=None, changed_ids:set[str]=set(), delay_seconds:int=0, context:dict={}):
    """ Restores an ambient by processing line for line."""
    if delay_seconds > 0:  sleep(delay_seconds)
    if states_old == None: states_old = lw.states()
    script = fa.read_file(["ambients", name])
    tokens = prepare(script)
    if len(context) == 0: predefined(context)
    _interpret_tokens(id, tokens, states_old, changed_ids, context)
    terminate(id)


def prepare(template):
    template = f'{macros()}\n{template}'
    env = Environment(autoescape=select_autoescape())
    for m in [Common, random]: 
        _map_methods(env.globals, m)
    tokens_str = env.from_string(template).render()
    tokens = fa.clean_lines(tokens_str)
    def _clean_token(t:str):
        while '  ' in t: t = t.replace('  ', ' ')
        return t
    tokens = [_clean_token(t) for t in tokens]
    log.debug(f"template:\n{template}")
    def join(ts): return ('\n'.join(ts))
    log.debug(f"instructions:\n{join(tokens)}")
    return tokens


def _map_methods(mappings:dict, module:Module) -> dict:
    methods = [m for m in dir(module) \
        if callable(getattr(module, m)) and not m.startswith('_')]
    for m in methods:
        mappings[m] = partial(_invoke, None, module, m)
    return mappings


def _invoke(cast, module, method, *args, **kwargs):
    method = getattr(module, method)
    value = method(*args, **kwargs)
    if cast != None: value = cast(value)
    return value


class Common:
    def s(value) -> str:   return str(value)
    def i(value) -> int:   return int(value)
    def f(value) -> float: return float(value)


def _interpret_tokens(id:str, tokens:list[str], states_old:list[State], changed_ids:set[str], context:dict={}):
    """ Interprets the script."""
    for token in tokens:
        if terminated(id): 
            lw.set_states(states_old, changed_ids)
            return
        if token.startswith(("ID", "#")) or token == "":
            continue
        if token.startswith("$") and token.find("=") > 0: 
            _add_variable(token, context)
            continue
        token = _substitute(token, context)
        _interpret_token(id, token, states_old, changed_ids, context)


def _interpret_token(id:str, token:str, states_old:list[State], changed_ids:set[str], context:dict={}):
        """ Interprets a single token."""
        log.debug(token)
        # check if terminated
        if terminated(id): return
        # repetitions
        if token.startswith("repeat"):
            repeat = token.partition(" ")[2]
            times, _, repeat = repeat.partition(" ")
            repeat = repeat.strip()
            for _ in range(int(times)):
                _interpret_token(id, repeat, states_old, changed_ids)
            return
        # process asterisk "for all devices"
        if token.startswith("*"):
            for i in [s.id for s in states_old]:
                _interpret_token(id, token.replace("*", str(i)), states_old, changed_ids)
            return
        # process comma-separated list
        parts = token.partition(" ")
        if parts[0].find(",") > 0:
            for i in parts[0].split(","):
                _interpret_token(id, f"{i} {parts[2]}", states_old, changed_ids)
            return
        # multiple instructions in a single line
        if token.find("\\") > 0:
            for part in token.split("\\"):
                _interpret_token(id, part.strip(), states_old, changed_ids, context)
            return
        # sleep
        elif token.startswith("sleep"): _sleep(token)
        # reset
        elif token.startswith("reset"):
            lw.set_states(states_old, changed_ids)
            changed_ids.clear()
        # call
        elif token.startswith("call"):
            _run(id, token.partition(" ")[2], states_old, changed_ids, 0, context)
        # set
        else: _set(token, states_old, changed_ids)


def _add_variable(assignment:str, context:dict):
    """ Adds a variable."""
    parts = assignment.partition("=")
    value = _substitute(parts[2].strip(), context)
    context[parts[0].strip()] = value


def _substitute(token:str, context:dict):
    """ Substitutes the variables."""
    pattern = r'\$[\w0-9_]+'
    matches = re.findall(pattern, token)
    for m in matches:
        # ignore variable assignment
        if token.partition("=")[0].strip() == m: continue
        if m in context: token = token.replace(m, context[m])
        else: raise Exception(f"'{m}' cannot be replaced: {context}")
    # variables might contain variables, we replace them recursivly
    if token.find("$") > 2: token = _substitute(token, context)
    return token


def _set(instruction:str, states_old:list[State], changed_ids:set[str]):
    """ Processes a single instruction and sets the values."""
    instr_interpolated = _interpolate_instruction(instruction, states_old)
    log.debug(f"Interpolated:\n{instruction}\n{instr_interpolated}")
    state = State(instr_interpolated)
    changed_ids.add(state.id)
    lw.set_state(state)


def _interpolate_instruction(instr:str, states_old:list[State]):
    """ Replaces instructions with random values."""
    # find old value
    id = instr.partition(" ")[0]
    # sanitize values (6 columns)
    values = [c for c in instr.split(" ") if c != "" and not c.isspace()]
    values += ["-"] * (6 - len(values))
    # current state needed for calculations if any value is an incremental value
    state_now = lw.state("dev", id)
    # interpolate
    values_interpolated = []
    for idx, value in enumerate(values):
        type = "id"  if idx == 0 else \
               "pwr" if idx == 1 else \
               "hue" if idx == 2 else \
               "sat" if idx == 3 else \
               "bri" if idx == 4 else \
               "name"
        if type in ["hue", "sat", "bri"]:
            # tanslate
            interpolated = str(_interpolate_value(value, type, state_now))
            values_interpolated.append(interpolated)
        else: values_interpolated.append(value)
    instr_interpolated = " ".join(values_interpolated)
    return instr_interpolated


def _interpolate_value(val:str, attr:str=None, state:State=None) -> str:
    """ interpolates a single value (such as '+ru(0,30)')."""
    if val == "-": return val
    # integer found, sanitze it
    if type(val) == int or re.match("^[0-9]*$", str(val)): 
        val = int(val)
        if   attr == "hue":          val %= 360
        elif attr in ["bri", "sat"]: val = min(100, max(0, val))
        elif attr == "sleep":        val = max(0, val)
        return val
    # increment/decrement, requires calculation
    if val.startswith(("+", "-")):
        if attr not in ["hue", "sat", "bri"]: return int(val)
        assert state != None
        assert attr != None
        now   = int(getattr(state, attr))
        delta = int(_interpolate_value(val[1:], attr, state))
        if val[0] == "+": new = now + delta
        else:             new = now - delta
        return _interpolate_value(new, attr, state)
    # random.uniform
    if val.startswith("ru(") and val.endswith(")"):
        match = re.match(r'ru\(([-+]?\d+),\s*([-+]?\d+)\)', val)
        lower = int(_interpolate_value(match.group(1), None, state))
        upper = int(_interpolate_value(match.group(2), None, state))
        new   = int(random.uniform(lower, upper))
        return _interpolate_value(new, attr, state)
    # random.choice
    if val.startswith("rc(") and val.endswith(")"):
        choices = map(lambda v: int(_interpolate_value(v, attr, state)), \
            val[3:-1].split(","))
        new = random.choice(list(choices))
        return _interpolate_value(new, attr, state)
    raise Exception(f"'{val}' ({attr}) cannot be processed")


def _sleep(timeout:str):
    """ Pause execution."""
    time = _interpolate_value(timeout.partition(" ")[2], "sleep", None)
    time = int(time)
    sleep(time)


def predefined(variables:dict={}) -> dict:
    """ Colors."""
    # colors
    variables["$red"]     = "0"
    variables["$orange"]  = "30"
    variables["$yellow"]  = "60"
    variables["$lime"]    = "90"
    variables["$green"]   = "120"
    variables["$mint"]    = "150"
    variables["$cyan"]    = "180"
    variables["$azure"]   = "210"
    variables["$blue"]    = "240"
    variables["$violet"]  = "270"
    variables["$magenta"] = "300"
    variables["$rose"]    = "330"
    # approximate colors
    variables["$randomhue"]  = "ru(0,360)"
    variables["$redish"]     = "ru(-15,15)"
    variables["$orangeish"]  = "ru(15,45)"
    variables["$yellowish"]  = "ru(45,75)"
    variables["$limeish"]    = "ru(75,105)"
    variables["$greenish"]   = "ru(105,135)"
    variables["$mintish"]    = "ru(135,165)"
    variables["$cyanish"]    = "ru(165,195)"
    variables["$azureish"]   = "ru(195,225)"
    variables["$blueish"]    = "ru(225,255)"
    variables["$violetish"]  = "ru(255,285)"
    variables["$magentaish"] = "ru(285,315)"
    variables["$roseish"]    = "ru(315,345)"
    # saturation/brightness
    variables["$full"]       = "100"
    variables["$high"]       = "75"
    variables["$half"]       = "50"
    variables["$low"]        = "25"
    variables["$zero"]       = "0"
    # approximate saturation/brightness
    variables["$randomsat"]  = "ru(0,100)"
    variables["$randombri"]  = "ru(0,100)"
    variables["$fullish"]    = "ru(85,100)"
    variables["$highish"]    = "ru(60,90)"
    variables["$halfish"]    = "ru(35,65)"
    variables["$lowish"]     = "ru(10,40)"
    variables["$zeroish"]    = "ru(0,15)"
    # increments
    variables["$ixs"]      = "+ru(0,4)"
    variables["$is"]       = "+ru(0,8)"
    variables["$im"]       = "+ru(4,16)"
    variables["$il"]       = "+ru(8,32)"
    variables["$ixl"]      = "+ru(16,64)"
    variables["$ixxl"]     = "+ru(32,128)"
    # decrements
    variables["$dxs"]      = "-ru(0,4)"
    variables["$ds"]       = "-ru(0,8)"
    variables["$dm"]       = "-ru(4,16)"
    variables["$dl"]       = "-ru(8,32)"
    variables["$dxl"]      = "-ru(16,64)"
    variables["$dxxl"]     = "-ru(32,128)"
    # flicker
    variables["$fxs"]      = "+ru(-4,4)"
    variables["$fs"]       = "+ru(-8,8)"
    variables["$fm"]       = "+ru(-16,16)"
    variables["$fl"]       = "+ru(-32,32)"
    variables["$fxl"]      = "+ru(-64,64)"
    variables["$fxxl"]     = "+ru(-128,128)"
    # name-id mapping
    def _clean(name): return "$" + re.sub(r'[^\w0-9]', '_', name.lower())
    # devices
    for s in sorted(lw.states(), key=lambda x: x.name):
        k = _clean(s.name)
        if k in variables: continue
        variables[k] = s.id
    # groups
    for s in sorted(lw.states(True), key=lambda x: x.name):
        k = _clean(s.name)
        if k in variables: continue
        variables[k] = ",".join(s.memids)
    return variables


def macros() -> str:
    macros = ''
    macro_files, _ = fa.list_share_files(['ambients', 'macros'])
    for m in macro_files:
        path = fa.sanitize(['ambients', 'macros', m])
        macro = fa.read_file([path])
        macros = f'{macros}\n\n# {path}\n\n{macro.strip()}\n'
    return macros