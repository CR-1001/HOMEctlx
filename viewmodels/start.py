# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for landing page.
"""

import logging
import re
import services.meta as m
import services.fileaccess as fa
from viewmodels import markdown


def ctl() -> list[m.view]:
    """ Starting point."""

    forms = []
    forms.append(m.form(None, None, [m.space(10)], True, False))
    
    try:
        files_md, _ = fa.list_files(['start/'], True)
        files_md = [f for f in files_md if f.endswith('.md')]
        files_md = sorted(files_md)
        for f in files_md: _load_md(forms, f, False)
    except Exception as e:
        logging.warning(f"Error processing start mark-down files: {e}")

    forms.append(
        m.form(None, 'License', [
            markdown.for_str(
                """# HOMEctlx
                Copyright (C) 2024 Christian Rauch.
                Distributed under terms of the GPL3 license.""", False)
        ], False, True))
    
    return [m.view("_body", "", forms)]


def _load_md(forms:list, file:str, open:bool):
    try:
        md = markdown.for_file('start', file, False)
        name = file[:-3]
        name = re.sub(r'^\d+[_ ]+', '', name)
        name = name.replace('/', ' / ').title()
        if not isinstance(md, m.space):
            #md.summary = name
            fields = [
                m.applink(
                    f"/files/ctl?dir=start&file={file}", 
                    "edit",
                    f"start/{file}",
                    "small"),
                md]
            forms.append(m.form(None, name, fields, open, True))

    except Exception as e: logging.error(f"Error processing '{file}': {e}")