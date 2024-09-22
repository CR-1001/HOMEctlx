# HOMEctlx
HOMEctlx is a lean and modular smart home system.

## Modules and Functions
- **Files**: Share and edit files.
- **Light**: Control your Philips Hue light system.
- **Ambients**: Define static and dynamic scenes with a scripting language.
- **Alarms**: Schedule alarms and timers.
- **Telemetry**: Maintenance functions.

## Installation and Configuration
- `INSTALLATION` describes the requirements and setup process.
- Configuration is set in `config.json`.
- The `share` directory contains the files to be shared (and the landing page `start.md`). 

## Technical Background
Most user interface interactions in HOMEctlx are handled via a lean view-model framework. JavaScript on the client side, `cmdex.js`, reacts to events, collects data from input fields, calls the server, and updates the user interface. On the server side, HTTP requests are managed by `services/reqhandler.py`. Received arguments are passed to the view-models. These return metadata (`services/meta.py`) describing the new state of the user interface. The corresponding HTML is rendered and sent to the client.


# Disclaimer and Author
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License (GPL) version 3 as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful, but without any warranty; without even the implied warranty of merchantability or fitness for a particular purpose. 

Copyright (C) 2024 Christian Rauch.


# Impressions
![start](share/documents/preview/hc-start-1.jpeg)
![files](share/documents/preview/hc-files-1.jpeg)
![files](share/documents/preview/hc-files-2.jpeg)
![ambients](share/documents/preview/hc-ambients-1.jpeg)
![ambients](share/documents/preview/hc-ambients-2.jpeg)
![alarms](share/documents/preview/hc-alarms-1.jpeg)
![lights](share/documents/preview/hc-lights-1.jpeg)