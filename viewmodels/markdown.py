# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
View-model for markdown.
"""

import logging
import re
import services.meta as m
import services.fileaccess as fa
from flask import session

def for_str(content:str, recess:bool=True) -> m.uielement:
    """ Convert a markdown string to a uielement. """
    fields = []
    lines = content.strip().split("\n")
    
    for line in lines:
        if line.startswith("#"):
            order = 0
            for char in line:
                if char == '#': order += 1
                else: break
            fields.append(m.title(line[order:].strip(), order))
        else:
            links = re.findall(r'\[(.*?)\]\((.*?)\)', line)
            prev_idx = 0
            for link in links:
                replace = f"[{link[0]}]({link[1]})"
                index = line.find(replace, prev_idx)
                if index != -1:
                    fields.append(m.label(line[prev_idx:index]))
                    fields.append(m.link(link[1].strip(), link[0].strip()))
                    prev_idx = index + len(replace)
            
            if prev_idx < len(line):
                fields.append(m.label(line[prev_idx:]))

        fields.append(m.space(1))
    
    return m.markdown(fields, recess)


def for_file(dir:str, file:str, recess:bool=True) -> m.uielement:
    """ Markdown fields from a file. """
    try:
        content = fa.read_file([dir, file])
        return for_str(content, recess)
    
    except Exception as e:
        logging.warning(f"File '{file}' in '{dir}' cannot be interpreted: {e}")
        return m.space(1)
