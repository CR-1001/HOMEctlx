# This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
# Distributed under terms of the GPL3 license.

import datetime
import os
import random
import re
import sys
import zipfile
from flask import Blueprint, render_template, send_from_directory, jsonify
from pathlib import Path


media_pb = Blueprint("media", __name__)


class mediactl:
    """ Serves files and directories."""

    def init(app): 
        """ Initialization. Gets the media directory to serve."""
        mediactl.media_dir = app.config["media_dir"]


    @media_pb.route("/media/srv-file/<path:file>")
    def get_file(file: str):
        """ Sends the file."""

        file = file.strip("$/")

        path_base = mediactl.get_path_base()
        
        return send_from_directory(path_base, file)


    @media_pb.route("/media/ctl")
    def control():
        """ Renders the control. Directory content is loaded using client code."""

        return render_template("media/control.html", **locals())


    @media_pb.route("/media/srv-dir/<path:dir>")
    def get_dir(dir: str):
        """ Sends the directory as JSON. Path, sub-directories and files 
        are listed."""

        dir = dir.strip("$/")

        path = mediactl.get_path(dir)

        files = list()
        dirs = list()

        # iterate over entries in directory
        for entry in path.iterdir():
            if entry.is_dir():
                dirs.append(entry.name)
            elif entry.is_file():
                if not entry.name.startswith("."):
                    files.append(entry.name)

        # build dictinary for client-side processing
        values = dict()
        dirs.sort()
        files.sort()
        values["dirs"] = dirs
        values["files"] = files
        values["path"] = dir.split("/")
        
        return jsonify(values)


    def get_path(sub: str):
        """ Gets the path, checks for directory traversal attacks."""

        path_base = mediactl.get_path_base()

        if not os.path.exists(path_base):
            raise Exception("Base directory cannot be found")

        path_requested = Path(os.path.join(path_base, sub))

        if os.path.commonprefix(
            (os.path.realpath(path_requested), 
            path_base)) != path_base: 
            raise Exception("Path not within base directory")

        if not path_requested.exists():
            raise Exception("Path does not exist")

        return path_requested


    def get_path_base():
        """ Gets the base path as set during initialization."""

        return Path(mediactl.media_dir).absolute().__str__()


    @media_pb.route("/media/srv-dir-archive/<path:dir>")
    def get_dir_archive(dir: str):
        """ Sends the directory as archive."""

        # get directory to archive
        path_dir = mediactl.get_path(dir.strip("$/"))

        # compose archive name: time stamp + random number
        time = f"{datetime.datetime.now():%Y%m%d%H%M%S}"
        number = random.randint(0, sys.maxsize)
        dir_name = re.sub(r"[^\w_. -]", "_", dir)
        archive_file = f".archive-{dir_name}-{time}-{number}.zip"

        # archive files are stored in the root directory
        path_base = mediactl.get_path_base()
        path_archive = os.path.join(path_base, archive_file)
    
        # iterate over files and add them to archive
        with zipfile.ZipFile(path_archive,"w") as archive:
            for root, dirs, files in os.walk(path_dir):
                for file in files:
                    if file.startswith("."): continue
                    filepath = os.path.join(root, file)
                    filepath_archive = filepath[path_dir.__str__().__len__():]
                    archive.write(filepath, filepath_archive)

        path_archive_relative = path_archive.lstrip(path_base)

        # send the file and delete it afterwards
        try: return mediactl.get_file(path_archive_relative)
        finally: os.remove(path_archive)