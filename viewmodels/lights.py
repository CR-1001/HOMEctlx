# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for lights.
"""

from datetime import datetime, timedelta
import services.lightctlwrapper as lw
from services.lightstates import States
import services.meta as m


def ctl() -> list[m.view]:
    """ Starting point."""
    forms = [m.form(None, "lights", [
        m.execute("lights/all_off", "turn all off"),
        m.space(1)], True, False)]
    states = lw.states_grouped("grp")
    for grp in states:
        fields = []
        fields.append(m.light("lights/set", grp))
        key = f"lights-group-{grp.head.id}-{grp.head.name}"
        forms.append(m.form(key, grp.head.name, fields, grp.head.pwr == "on"))
    return [
        m.view("_body", "", forms), 
        m.header([m.applink("/ambients/ctl", "🌴 ambients")])]


def set(type:str, id:str, value:str, attr:str) -> list[m.view]:
    """ Set states."""
    ids = [id] if type != "grp" else lw.get_ids_in_group(id)
    lw.set_attributes(ids, attr, value)
    return ctl()


def all_off():
    """ All off."""
    lw.set_all_off()
    return ctl()