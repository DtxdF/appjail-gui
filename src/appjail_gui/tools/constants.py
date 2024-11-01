# BSD 3-Clause License
#
# Copyright (c) 2024, Jesús Daniel Colmenares Oviedo <DtxdF@disroot.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import os

from appjail_gui import dummy

_homedir = os.getenv("HOME", "/tmp")
_datadir = os.path.join(_homedir, ".appjail-gui")
_rootdir = os.path.dirname(dummy.__file__)

_parser = argparse.ArgumentParser(
    description="Graphical User Interface for AppJail"
)

_parser.add_argument("--host-addr",
    default="0.0.0.0",
    help="host address to listen to")
_parser.add_argument("--host-port",
    default=8080,
    help="port to listen on for connections"
)
_parser.add_argument("--projects-dir",
    default=os.path.join(_datadir, "data/projects"),
    help="location of projects"
)
_parser.add_argument("--workspaces-dir",
    default=os.path.join(_datadir, "data/workspaces"),
    help="location of workspaces"
)
_parser.add_argument("--native",
    default=False,
    action="store_true",
    help="enable 'Native Mode'. (Experimental)"
)

_args = _parser.parse_args()

IMAGE_WIDTH = 240
IMAGE_HEIGHT = 280
PROJECTS = _args.projects_dir
WORKSPACES = _args.workspaces_dir
EDITOR_THEME = "githubLight"
EDITOR_INDENT = " " * 4
NODESCR = "No description ..."
NOIMAGE = os.path.join(_rootdir, "files/img/noimage.png")
PLUGINS = os.path.join(_datadir, "plugins")
NOWWW = None
DONE_FILE = ".done"
INPROGRESS_FILE = ".progress"
DIRECTOR_FILE = "appjail-director.yml"
ENV_FILE = ".env"
INFO_FILE = "info.json"
PAGE_TITLE = "Graphical User Interface for AppJail"
PAGE_FAVICON = os.path.join(_rootdir, "files/img/favicon.ico")
HOST_ADDR = _args.host_addr
HOST_PORT = _args.host_port
REQUIREMENTS = ("appjail", "appjail-director")
RESPONSE_TIMEOUT = 60 * 60 * 24
IMAGOTYPE = os.path.join(_rootdir, "files/img/Imagotype.png")
NATIVE_MODE = _args.native
