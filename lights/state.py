# This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
# Distributed under terms of the GPL3 license.

import colorsys
import json
import re
from typing import Any


class State:

    def __init__(self, state_str):

        state_str_split = state_str.split()
        
        self.id = state_str_split[0]
        self.pwr = state_str_split[1]

        self.hue = state_str_split[2]
        self.sat = state_str_split[3]
        self.bri = state_str_split[4]

        self.has_hue = self.hue != "-"
        self.has_sat = self.sat != "-"
        
        self.rgb = colorsys.hsv_to_rgb(
            State._conv(self.hue) / 360, 
            State._conv(self.sat) / 100, 
            State._conv(self.bri) / 100)
        
        self.rgb_hsat = colorsys.hsv_to_rgb(
            State._conv(self.hue) / 360, 1.0, 1.0)
        
        self.rgb_lsat = colorsys.hsv_to_rgb(
            State._conv(self.hue) / 360, 0.0, 1.0)

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
            self.name = name_and_memids.group(1)
            self.memids = [str(i) for i in name_and_memids.group(2).split(",")]
            self.uid = f'grp-{self.id}'
        else:
            self.name = last_columns
            self.uid = f'dev-{self.id}'


    def str(self):

        return "%s %s %s %s %s" % (self.id, self.pwr, self.hue, self.sat, self.bri)


    def json(self):

        return json.dumps(self.__dict__)

    
    def set(self, attr, val):

        self.__dict__[attr] = val


    def _conv(value):

        if value == "-":
            value = 0
        return float(value)


class States:   

    def __init__(self, states_str = ""):

        self.items = list()
        for state_str in states_str.split("\n"):
            if state_str != "":
                self.items.append(State(state_str))


    def __getitem__(self, idx):
        return self.items[idx]


    def __setitem__(self, idx, val):
        self.items[idx] = val


    def get_subset(self, predicate):
        state_subset = States()
        state_subset.items = list(filter(predicate, self.items))

        return state_subset


    def json(self):

        return json.dumps(self.__dict__)


class Group:

        def __init__(self, state_group, states_members):
            self.head = state_group
            self.members = states_members

        def __getattr__(self, name):
            if hasattr(self.head, name):
                return getattr(self.head, name)
