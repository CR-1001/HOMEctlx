# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
OBSOLETE. Not used anymore, view-models are now called directly.
Calls view-model functions in a separate thread.
"""

import ast
import glob
import inspect
import json
import logging
import os
from threading import Lock, Thread
from queue import Queue
import services.meta as m


log = logging.getLogger(__file__)


class cmdexec:
    """ Executes commands."""


    def __init__(self):
        """ Loads the view-models."""
        self.dir     = os.path.realpath("viewmodels")
        self.mutex   = Lock()
        self.modules = dict()
        files = glob.glob(os.path.join(self.dir, "*.py"))
        for p in files:
            name = os.path.splitext(os.path.basename(p))[0]
            mdict = {}
            with open(p, 'r') as f:
                exec(f.read(), mdict)
            self.modules[name] = mdict


    def get_start_modules(self, 
            timeout, 
            filefilter=lambda _: True, 
            funcfilter=lambda _: True, 
            args={}) -> list[m.view]:
        """ Gets all view-model starting point modules. The files in the
        view-model directory are inspected. Filters the files and function
        with the passed filters. Enforces a timeout for the inspection."""
        filefilter = filefilter if filefilter != None else lambda _: True
        funcfilter = funcfilter if funcfilter != None else lambda _: True
        if metaargs == None: metaargs = {}
        self.moddescs = list()
        self._inspect_viewmodels(\
            timeout, filefilter, funcfilter, metaargs)
        with self.mutex:
            self.moddescs = sorted(self.moddescs, key=lambda m: m.order)
            return self.moddescs


    def _inspect_viewmodels(self, timeout, filefilter, funcfilter, metaargs):
        """ Inspects the view-models for starting point metadata."""
        files = [f for f in os.listdir(self.dir) if f.endswith(".py")]
        for f in files:
            t = Thread(
                target=self._inspect_viewmodel,
                args=[f, filefilter, funcfilter, metaargs])
            t.start()
            t.join(timeout=timeout)


    def _inspect_viewmodel(self, file, filefilter, funcfilter, args):
        """ Inspects the view-model for starting point metadata."""
        if filefilter(file) and self._has_start_modules(file):
            self._load_start_modules(file, funcfilter, args)


    def _has_start_modules(self, file):
        """ Checks whether the view-model offers a starting point."""
        path = os.path.join(self.dir, file)
        with open(path, "r") as text: code = text.read()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) \
                and node.name.startswith("ctl"):
                return True
        return False


    def _load_start_modules(self, file, args):
        """ Loads the view-model starting point meta data."""
        self.modules += self.invoke(file, "ctl", args)


    def invoke(self, file, func, params, timeout=None):
        """ Invokes a command. The function call with the passed arguments
         is executed in a separate thread to enforce a timeout."""
        queue = Queue(1)
        thread = Thread(
            target=self._invoke,
            args=[file, func, params, queue])
        thread.start()
        try:
            if timeout == None: return queue.get(block=True)
            else: return queue.get(block=True, timeout=timeout)
        except Exception as e: 
            log.error(f"{file}.{func}({json.dumps(params)}) failed: {str(e)}")
            raise Exception("Error in function or timeout.")


    def _invoke(self, file:str, func:str, params:dict, queue:Queue):
        """ Invokes a command. This means calling the function in the
        view-model with the parameters using the thread-safe queue for
        the return value."""
        log.debug(locals())
        function = self.modules[file].get(func)
        signature = inspect.signature(function)
        accepted_params = set(signature.parameters.keys())
        filtered_params = {key: value for key, value in params.items() \
                           if key in accepted_params}
        result = function(**filtered_params)
        queue.put(result)
