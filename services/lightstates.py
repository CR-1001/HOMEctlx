# This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Device states.
"""

import colorsys
import json
import re
from typing import Any, Callable


class State:
    """ A single device state (hue, saturation, brightness) with helpful conversions (HSB with max/min saturation, RGB, ...)."""

    def __init__(self, state_str:str):
        """ Parses a state string."""

        state_str_split = state_str.split()
        
        self.id = state_str_split[0]
        self.pwr = state_str_split[1]

        self.hue = state_str_split[2]
        self.sat = state_str_split[3]
        self.bri = state_str_split[4]

        self.has_hue = self.hue != "-"
        self.has_sat = self.sat != "-"

        def conv(value, default): 
            return default if value == "-" else float(value)
        
        # it looks better when 
        # 1) single-colored lights have a warm tone
        # 2) the brightness is scaled

        bri_scaled = (30 + (0.7 * conv(self.bri, 0))) / 100

        self.rgb = colorsys.hsv_to_rgb(
            conv(self.hue, 45) / 360, 
            conv(self.sat, 25) / 100, 
            bri_scaled)
        
        self.rgb_hsat = colorsys.hsv_to_rgb(
            conv(self.hue, 45) / 360, 1.0, bri_scaled)
        
        self.rgb_lsat = colorsys.hsv_to_rgb(
            conv(self.hue, 45) / 360, 0.0, bri_scaled)

        self.red = self.rgb[0] * 255
        self.gre = self.rgb[1] * 255
        self.blu = self.rgb[2] * 255

        self.red_lsat = self.rgb_lsat[0] * 255
        self.gre_lsat = self.rgb_lsat[1] * 255
        self.blu_lsat = self.rgb_lsat[2] * 255

        self.red_hsat = self.rgb_hsat[0] * 255
        self.gre_hsat = self.rgb_hsat[1] * 255
        self.blu_hsat = self.rgb_hsat[2] * 255
        
        # groups have member IDs as last column
        # (comma-separated list in squared brackets)
        last_columns = " ".join(state_str_split[5:])
        name_and_memids = re.search(r"(.*)\[(.*)\]", last_columns)

        self.group = name_and_memids is not None

        if self.group:
            self.name = name_and_memids.group(1).strip()
            self.memids = [str(i) for i in name_and_memids.group(2).split(",")]
            self.uid = f'grp-{self.id}'
        else:
            self.name = last_columns.strip()
            self.uid = f'dev-{self.id}'

    def str(self):
        """ String."""
        return "%s %s %s %s %s" % (self.id, self.pwr, self.hue, self.sat, self.bri)

    def json(self):
        """ JSON."""
        return json.dumps(self.__dict__)
    
    def set(self, attr, val):
        """ Set attribute."""
        self.__dict__[attr] = val


class States:
    """ Many states."""

    def __init__(self, states_str = ""):
        """ Parses a state string."""
        self.items = list()
        for state_str in states_str.split("\n"):
            if state_str != "":
                self.items.append(State(state_str))

    def get_subset(self, predicate:Callable):
        """ Gets a member subset"""
        state_subset = States()
        state_subset.items = \
            list(sorted(filter(predicate, self.items), key=lambda d: d.name))
        return state_subset


    def json(self):
        """ JSON."""
        return json.dumps(self.__dict__)


class Group:
    """ Device groups."""

    def __init__(self, state_group, states_members):
        """ Sets the states of the group and its members."""
        self.head = state_group
        self.members = states_members

    def __getattr__(self, name):
        """ Gets the attribute."""
        if hasattr(self.head, name):
            return getattr(self.head, name)
