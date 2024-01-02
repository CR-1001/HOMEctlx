# This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
# Distributed under terms of the GPL3 license.

import json
from flask import Flask

from lights.lightctl import lightctl, light_pb
from media.mediactl import mediactl, media_pb
from home.start import start_pb


app = Flask(__name__)

def create_app(app):
    
    # Load the configuration
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        app.config.update(config)

    # Initialize the modules
    lightctl.init(app)
    mediactl.init(app)
    app.register_blueprint(start_pb)
    app.register_blueprint(light_pb)
    app.register_blueprint(media_pb)

    return app

create_app(app)

if __name__ == "__main__":

    app.run()
    