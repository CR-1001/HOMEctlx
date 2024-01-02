# This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
# Distributed under terms of the GPL3 license.

from datetime import datetime
import socket
from flask import Blueprint, jsonify, render_template, request

from lights.lightctl import lightctl, light_pb
from media.mediactl import mediactl, media_pb


start_pb = Blueprint("start", __name__)


@start_pb.route("/")
def start():
    """ Welcome."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    address = request.remote_addr

    return render_template("start.html", **locals())


@start_pb.route("/health")
def health():
    """ Server status. To be extended."""

    values = dict()

    values["network.hostname"] = socket.gethostname()
    values["network.address"] = socket.gethostbyname(values["network.hostname"])

    return jsonify(values)
