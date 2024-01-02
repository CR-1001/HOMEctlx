# This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
# Distributed under terms of the GPL3 license.

import subprocess
import copy
import time
from flask import Blueprint, render_template, request, redirect, url_for

from lights.state import States, State, Group


light_pb = Blueprint("light", __name__)


class lightctl:
    """ Allows you to control your lamps."""

    def init(app): 
        """ Initialization. Gets the LightCtl command (configured with address and user) to call."""
        lightctl.lightctl_exec = app.config["lightctl_exec"]


    def exec(cmd, type = "", parameters = ""):
        """ Executes the LightCtl command."""

        if type == "grp":    cmd += "-group"
        if parameters != "": cmd += " " + parameters

        exec = str(lightctl.lightctl_exec)

        result = subprocess.check_output(
            f"{exec} {cmd} --brief", shell = True) \
            .decode("utf-8")

        return result


    @light_pb.route("/lights/ctl")
    def control_grp(): 
        """ Starting point (control) for device groups."""
        return lightctl.control("grp")

        
    @light_pb.route("/lights/ctl-<type>")
    def control(type):
        """ Starting point (control)."""

        if type not in ["dev", "grp"]: raise Exception("Not supported")
        other_type = "dev" if type == "grp" else "grp"

        return render_template("lights/control.html", **locals())


    @light_pb.route("/lights/state-<type>/<id>")
    def state_id(id, type):
        """ Get the state of a device or group."""

        state = State(lightctl.exec("state", type, id))

        return state.json()


    @light_pb.route("/lights/set-<type>/<id>", methods = ["POST"])
    def set_id(id, type):
        """ Changes the state of a device or group."""

        json = request.get_json(force=True) 

        attr = json["attr"]
        val = json["val"]

        if type != 'grp': ids = [id]
        else: ids = State(lightctl.exec("state", type, id)).memids

        for i in ids: lightctl.set_dev_attr(i, attr, val)

        return ""

    
    def set_dev_attr(id, attr, val):
        """ Sets an attribute of a device or group."""

        state = State(lightctl.exec("state", 'dev', id))

        if attr not in ["pwr", "hue", "sat", "bri"]:
            raise Exception("Invalid attribute")

        if attr == "pwr":
            if val != "on" and val != "off": raise Exception("Invalid value")
            setattr(state, "pwr", val)

        else:
            pwr = "off" if attr == "bri" and int(val) < 1 else "on"
            setattr(state, attr, int(val))
            setattr(state, "pwr", pwr)

        state_str = state.str()

        lightctl.exec("set", type, state_str)

        return ""


    @light_pb.route("/lights/set_all_off/<type>")
    def set_all_off(type):
        """ Turns all lights off."""

        states = States(lightctl.exec("state"))

        for state in states:
            if state.pwr != "off":
                state.pwr = "off"
                lightctl.exec("set", "", state.str())

        return redirect(url_for("light.control", type=type))


    @light_pb.route("/lights/set_alarm/<type>")
    def set_alarm(type):
        """ Alarm: all lights will blink (in red)."""

        states = States(lightctl.exec("state"))

        for state in states:
            pwr = state.pwr
            state_alarm = copy.deepcopy(state)
            state_alarm.pwr = "on"
            state_alarm.sat = 100
            state_alarm.bri = 100
            if state.hue != "-":
                state_alarm.hue = 0

            # set alarm state temporarily
            lightctl.exec("set", "", state_alarm.str())
            time.sleep(1)

            # reset device (pwr needs to be on)
            state.pwr = "on"
            lightctl.exec("set", "", state.str())

            # reset device pwr
            time.sleep(0.1)
            state.pwr = pwr
            lightctl.exec("set", "", state.str())

        return redirect(url_for("light.control", type=type))


    @light_pb.route("/lights/states-<type>")
    def states(type):
        """ Gets the device or group states."""

        groups = list()

        states_dev = States(lightctl.exec("state", "dev"))

        if type == "grp":
            states_grp = States(lightctl.exec("state", "grp"))

            for state_grp in states_grp:

                states_mem = states_dev.get_subset(
                    lambda s: (s.id in state_grp.memids))

                for attr in ["bri", "sat", "hue"]:

                    values = map(lambda s: s.__dict__[attr], states_mem)
                    values = [int(v) for v in values if v != "-"]

                    value = "-" if len(values) == 0 \
                                else str(int(sum(values) / len(values)))

                    state_grp.__dict__[attr] = value

                state_grp.has_sat = any(m.has_sat for m in states_mem)
                state_grp.has_hue = any(m.has_hue for m in states_mem)

                state_grp.pwr = "on" if any(m.pwr == "on" for m in states_mem) \
                                     else "off"
                
                groups.append(Group(state_grp, states_mem))

        else:
            head = dict()
            head["name"] = ""
            groups.append(Group(head, states_dev))

        active = str(request.args.get("active", ""))

        return render_template("lights/states.html", **locals())