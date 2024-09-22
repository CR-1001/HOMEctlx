# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for landing page.
"""

import logging
import services.meta as m
from viewmodels import markdown


def ctl() -> list[m.view]:
    """ Starting point."""

    forms = []

    forms.append(m.form(None, None, [m.space(10)], True, False))

    try:
        md = markdown.for_file('', 'start.md', False)
        if not isinstance(md, m.space):
            forms.append(m.form(None, None, [md, m.space(2)], True, False))
    except: pass

    forms.append(
        m.form(None, None, [
            markdown.for_str("# HOMEctlx\nCopyright (C) 2024 Christian Rauch.\nDistributed under terms of the GPL3 license.", False)
        ], True, False))
    
    return [m.view("_body", "", forms)]

