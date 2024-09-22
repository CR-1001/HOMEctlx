# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Generic processing of view-model meta data. Renders the HTML and receives 
the client calls.
"""

from collections.abc import Iterable
from flask import Blueprint, jsonify, render_template, request, send_from_directory
import services.meta as m
import services.fileaccess as fa
from viewmodels import files, start, alarms, ambients, lights, telemetry


cmdex_pb = Blueprint("cmd", __name__)


class reqhandler:
    """ Renders the view models."""

    modules = {}
    for m in [start, files, alarms, ambients, lights, telemetry]:
        modules[m.__name__.replace('viewmodels.', '')] = m

    @cmdex_pb.route("/<vm>/ctl")
    def control(vm:str):
        """ Starting point."""
        return render_template("control.html", vm=vm)


    @cmdex_pb.route("/<vm>/<func>", methods=["POST"])
    def run(vm:str, func:str):
        """ Executes a command."""
        args = request.get_json()
        return reqhandler.exec(vm, func, args)
    

    def exec(vm:str, func:str, args:dict):
        """ Executes the command."""
        try:
            if func in ['', None, 'undefined']: func = 'ctl'
            method = getattr(reqhandler.modules[vm], func)
            elements = method(**args)
            if not isinstance(elements, Iterable): elements = [elements]
            
            payload = {}
            for e in elements:
                if e.type() == "view":
                    html = render_template(f"view.html", view=e)
                elif e.type() in ["form", "header"]:
                    html = render_template(f"form.html", form=e)
                else:
                    html = render_template(f"field.html", field=e)
                payload[e.key] = html
            if not "_error" in payload:
                payload["_error"] = render_template(\
                    f"field.html", field=m.error())
        
        except Exception as e:
            payload = {"_error": render_template(\
                "field.html", field=m.error(str(e))) }
            
        return jsonify(payload) 
    

    @cmdex_pb.route("/files/share/<path:file>")
    def get_file(file:str):
        """ Sends the file."""
        return send_from_directory(fa.share_dir, file)