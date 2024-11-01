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

import json
import os
import shutil
import subprocess

from appjail_gui.tools.constants import WORKSPACES
from appjail_gui.tools.process import run_proc

def get_project_info(project):
    cmd = [
        "appjail-director",
        "describe",
        "-p",
        project
    ]

    proc = run_proc(cmd)

    info = json.loads(proc.stdout)

    return info

def get_projects():
    cmd = "appjail-director ls | tail -n +2 | cut -d' ' -f2-"

    proc = subprocess.run(cmd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    lines = []

    projects = {}

    if os.path.isdir(WORKSPACES):
        for project in os.listdir(WORKSPACES):
            lines.append(f"? {project}")

    lines.extend(proc.stdout.splitlines())

    for line in lines:
        (status, name) = line.split(" ", 1)

        projects[name] = status

    return projects

def destroy_project(project, workspace):
    cmd = [
        "appjail-director",
        "down",
        "--ignore-failed",
        "-d",
        "-p",
        project
    ]

    proc = run_proc(cmd, workspace)

    return proc

def deploy_project(project, workspace):
    cmd = ["appjail-director", "up", "-p", project]

    proc = run_proc(cmd, workspace)

    return proc

def check_project(project):
    cmd = ["appjail-director", "check", "-p", project]

    proc = run_proc(cmd)

    return proc.returncode

def down_project(project, workspace):
    cmd = [
        "appjail-director",
        "down",
        "-p",
        project
    ]

    proc = run_proc(cmd, workspace)

    return proc

def destroy_workspace(project, workspace):
    proc = destroy_project(project, workspace)

    workspace = os.path.join(WORKSPACES, project)

    shutil.rmtree(workspace)

    return proc
