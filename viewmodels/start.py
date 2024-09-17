# This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for landing page.
"""

import services.meta as m


def ctl(args:dict={}) -> list[m.view]:
    """ Starting point."""

    forms = []
    forms.append(
        m.form(None, None, [m.space(20)], table=False))
    forms.append(
        m.form("overview", "usage and license", [
            m.title("HomeCtl."),
            m.label("Copyright (C) 2024 Christian Rauch."),
            m.label("Distributed under terms of the GPL3 license.")
        ]))
    
    return [m.view("_body", "", forms)]

