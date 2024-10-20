# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Application entry point.
"""

import json
import logging
import secrets
from flask import Flask, redirect

import services.fileaccess as fa
import services.dbaccess as dba
import services.lightctlwrapper as lw
import services.ambinterpreter as ami
import services.routines as rou
import services.scheduler as sch
from services.reqhandler import cmdex_pb


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
log = logging.getLogger(__file__)


def create_app(app):
    """ Initialize components, set dependencies (Inversion of Control)."""
    
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        app.config.update(config)
    
    fa.init(app.config["share_dir"])

    log.info("System initializing.")

    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] [%(module)s.%(funcName)s:%(lineno)d]: %(message)s",
        handlers=[
            logging.FileHandler(fa.share_path(["temp", "logs"]), mode="w"),
            logging.StreamHandler()
        ])
    
    dba.init()
    lw.init(app.config["lightctl_exec"])
    sch.init(dba)
    ami.init(fa, dba, lw)
    rou.init(app.config["routines"])
    
    app.register_blueprint(cmdex_pb)

    @app.route('/')
    def index(): return redirect('start/ctl')

    log.warning("System initialized.")

    return app


@app.teardown_request
def after_request(exception):
    """ Free resources after the request."""
    dba.close_cached()
    if exception != None: log.error(e)


@app.before_request
def before_request():
    """ Acquire resources before the request."""
    dba.connect_cached()


create_app(app)

if __name__ == "__main__": app.run()