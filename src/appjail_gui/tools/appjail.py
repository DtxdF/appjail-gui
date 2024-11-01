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

import subprocess

from nicegui import run

from appjail_gui.tools.process import run_proc

async def start_jail(jail):
    cmd = [
        "appjail",
        "start",
        "--",
        jail
    ]

    proc = await run.cpu_bound(run_proc, cmd)

    return proc

async def stop_jail(jail):
    cmd = [
        "appjail",
        "stop",
        "--",
        jail
    ]

    proc = await run.cpu_bound(run_proc, cmd)

    return proc

async def restart_jail(jail):
    cmd = [
        "appjail",
        "restart",
        jail
    ]

    proc = await run.cpu_bound(run_proc, cmd)

    return proc

async def destroy_jail(jail):
    cmd = [
        "appjail",
        "jail",
        "destroy",
        "-Rf",
        jail
    ]

    proc = await run.cpu_bound(run_proc, cmd)

    return proc

async def status_jail(jail):
    cmd = [
        "appjail",
        "status",
        "-q",
        jail
    ]

    proc = await run.cpu_bound(run_proc, cmd, stderr=subprocess.DEVNULL)

    return proc.returncode

async def get_jails(keywords):
    jails = await run.cpu_bound(list_jails)

    table = []

    for jail in jails:
        attrs = await get_jail(jail, keywords)

        table.append(attrs)

    return table

async def get_jail(jail, keywords):
    attrs = {}

    for keyword in keywords:
        if keyword == "name":
            value = jail
        else:
            value = await run.cpu_bound(get_jail_attr, jail, keyword)

        if value == "":
            continue

        attrs[keyword] = value

    return attrs

def list_jails():
    cmd = ["appjail", "jail", "list", "-eHIpt", "name"]

    jails_proc = run_proc(cmd, stderr=subprocess.DEVNULL)
    jails = jails_proc.stdout
    jails = jails.splitlines()

    return jails

def get_jail_attr(jail, attr):
    cmd = ["appjail", "jail", "get", jail, attr]

    value = run_proc(cmd, stderr=subprocess.DEVNULL)
    value = value.stdout

    return value.strip()
