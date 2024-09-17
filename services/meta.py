# This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model meta data to describe the UI.
"""

from dataclasses import dataclass, field
from typing import Iterator
from services.lightstates import State


class uielement:
    key:str
    desc:str=None
    def type(self): return type(self).__name__
    def haskey(self): return hasattr(self, "key") and self.key != None


@dataclass
class view(uielement):
    key:str
    name:str
    forms:list


@dataclass
class form(uielement):
    key:str
    name:str
    fields:list
    open:bool=False
    table:bool=True


@dataclass
class header(uielement):
    fields:list
    name:str=None
    key:str="_header"


@dataclass
class execute(uielement):
    vm:str
    func:str
    text:str="execute"
    important:bool=False
    key:str=None


@dataclass
class execute_params(uielement):
    vm:str
    func:str
    text:str="execute"
    params:dict=None
    important:bool=False
    key:str=None


@dataclass
class autoupdate(uielement):
    vm:str
    func:str
    delay:int=1000
    params:dict=None


@dataclass
class choice(uielement):
    value:str
    text:str=None
    important:bool=False
    def makelist(items:Iterator, important:bool=False) -> list: 
        return list(map(lambda i: choice(i, important=important), items))


@dataclass
class triggers(uielement):
    vm:str
    func:str
    param:str
    values:list[choice]
    desc:str=None


@dataclass
class pager(uielement):
    vm:str
    func:str
    param:str
    st_idx:int
    page_sz:int
    all_sz:int
    container:str
    focus:bool=False
    params:dict=None
    #params:dict=field(default_factory=dict)


@dataclass
class path(uielement):
    vm:str
    func:str
    param:str
    values:list[choice]
    desc:str=None


@dataclass
class input(uielement):
    param:str


@dataclass
class hidden(input):
    param:str
    value:str


@dataclass
class integer(input):
    param:str
    value:int


@dataclass
class text(input):
    param:str
    text:str
    desc:str=None
    key:str=""


@dataclass
class text_big(input):
    param:str
    text:str
    desc:str=None


@dataclass
class text_ro(input):
    text:int
    desc:str=None


@dataclass
class text_big_ro(uielement):
    text:str
    desc:str=None


@dataclass
class response(uielement):
    key:str
    text:str=""
    desc:str=None


@dataclass
class select(uielement):
    param:str
    values:list[choice]
    default:choice=None
    desc:str=None


@dataclass
class select_many(uielement):
    param:str
    values:list[choice]
    defaults:list[choice]
    desc:str=None


@dataclass
class upload(uielement):
    param:str
    desc:str=None


@dataclass
class download(uielement):
    file:str
    text:str="download"
    desc:str=None


@dataclass
class media(uielement):
    file:str
    format:str


@dataclass
class link(uielement):
    link:str
    text:str


@dataclass
class applink(uielement):
    link:str
    text:str


@dataclass
class markown(uielement):
    content:list


@dataclass
class title(uielement):
    text:str


@dataclass
class label(uielement):
    text:str


@dataclass
class space(uielement):
    rows:int


@dataclass
class dir(uielement):
    dir_parent:str
    dir:str
    readonly:bool
    files:int
    vm:str
    func:str
    def path(self) -> str:
        if self.dir == '..': return self.dir_parent
        return f'{self.dir_parent}/{self.dir}'


@dataclass
class file(uielement):
    dir:str
    file:str
    readonly:bool
    link:str
    vm:str
    func:str


@dataclass
class placeholder(uielement):
    key:str


@dataclass
class error(uielement):
    text:str=None
    key:str="_error"


@dataclass
class light(uielement):
    vm:str
    func:str
    state:State
