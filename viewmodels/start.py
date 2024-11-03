# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for landing page.
"""

import logging
import re
from threading import Thread
import services.meta as m
import services.fileaccess as fa
import services.routines as rou
import services.scheduler as sd
from viewmodels import markdown


def ctl() -> list[m.view]:
    """ Starting point."""
    forms = []
    forms.append(m.form(None, None, [m.space(14)], True, False))
    _add_md(forms)
    _add_cmds(forms)
    _add_tasks(forms)
    _add_help(forms)
    return [m.view("_body", "", forms)]


def _add_help(forms):
    """ Add help."""
    forms.append(
        m.form(None, 'Help', [
            markdown.for_str("""
# HOMEctlx

## Help 
See README file.

## License 
Copyright (C) 2024 Christian Rauch.
Distributed under terms of the GPL3 license.""", False)
        ], False, True))
    

def _add_tasks(forms):
    tasks = sd.all()
    tasks_str = sorted([f"{t['type']}: {t['desc']}" for t in tasks])
    fields = [m.label(t) for t in tasks_str]
    forms.append(m.form(None, "Tasks", fields, len(tasks) > 0, True, details=f"⚙️ running tasks: {len(tasks)}"))


def _add_md(forms):
    """ Add single markdown."""
    try:
        files_md, _ = fa.list_files(['start/'], True)
        files_md = [f for f in files_md if f.endswith('.md')]
        files_md = sorted(files_md)
        for f in files_md: _load_md(forms, f, False)
    except Exception as e:
        logging.warning(f"Error processing start markdown files: {e}")


def _load_md(forms:list, file:str, open:bool):
    """ Load markdown."""
    try:
        md = markdown.for_file('start', file)
        name = file[:-3]
        name = re.sub(r'^\d+[_ ]+', '', name)
        name = name.replace('/', ' / ')
        if not isinstance(md, m.space):
            #md.summary = name
            fields = [
                m.applink(
                    f"/files/ctl?dir=start&file={file}", 
                    "edit",
                    f"markdown",
                    "small"),
                md]
            forms.append(m.form(None, name, fields, open, True, 
                                details=f"📝 start/{file}"))
    except Exception as e: logging.error(f"Error processing '{file}': {e}")


def _add_cmds(forms:list):
    """ Add routines."""
    for key, cmd in rou.get():
        msg = cmd["desc"] if "desc" in cmd else ""
        fields = [
            #m.label(f'command: {key}', 'small'),
            m.label(msg, "", f"exec_result:{key}")
        ]
        forms.append(m.form(None, key.title(), fields, details='⚡ command'))
        if cmd["exec"]["auto"]:
            fields.append(m.autoupdate("start/exec", 0, { "key": key }))
        if cmd["exec"]["manual"]:
            fields.append(m.execute_params("start/exec", params={ "key": key }))


def exec(key:str):
    """ Execute routines."""
    msg = rou.exec(key)
    return [m.label(msg, "", f"exec_result:{key}")]