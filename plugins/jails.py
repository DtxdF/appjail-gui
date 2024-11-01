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
import subprocess

from nicegui import run, ui

from appjail_gui.tools.appjail import destroy_jail
from appjail_gui.tools.appjail import get_jail
from appjail_gui.tools.appjail import get_jail_attr
from appjail_gui.tools.appjail import get_jails
from appjail_gui.tools.appjail import list_jails
from appjail_gui.tools.appjail import restart_jail
from appjail_gui.tools.appjail import start_jail
from appjail_gui.tools.appjail import status_jail
from appjail_gui.tools.appjail import stop_jail
from appjail_gui.tools.files import open_consolelog
from appjail_gui.tools.notification import my_notify
from appjail_gui.tools.process import run_proc
from appjail_gui.tools.sysexits import *

descr = "Start, stop, destroy and list jails and their information"

DEFAULT_KEYWORDS = "status name type version ports network_ip4"

async def main(e):
    async def display_table(e):
        jail = e.sender.text

        with ui.dialog() as dialog, ui.card().classes("w-11/12 h-3/5"):
            dialog.props("persistent")
            dialog.open()

            with ui.row().classes("w-full"):
                button = ui.button(
                    icon="close",
                    color="white",
                    on_click=lambda e: (dialog.close(), dialog.clear())
                )
                button.props("flat")
                button.classes("p-0")

                loading_spinner = ui.spinner("tail",
                    color="black",
                    size="2em"
                )
                loading_spinner.classes("ml-auto")

            keywords = search.value
            keywords = keywords.strip()

            if keywords == "":
                keywords = DEFAULT_KEYWORDS

            keywords = keywords.split(" ")

            _keywords = []

            for keyword in keywords:
                keyword = keyword.strip()

                if keyword == "":
                    continue

                _keywords.append(keyword)

            keywords = _keywords

            rows = await get_jail(jail, keywords)

            loading_spinner.visible = False

            if rows == []:
                ui.label("No information to display. Be sure to type existing columns.").classes("text-lg italic")
                return

            with ui.list().classes("w-full").props("dense separator"):
                for name, value in rows.items():
                    with ui.item():
                        with ui.item_section():
                            ui.label(name).props("header").classes("text-bold")

                        with ui.item_section():
                            ui.label(value)

    async def btn_start_jail(jail):
        status = await status_jail(jail)

        if status == 0:
            my_notify(f"{jail} is running", "warning")
            return

        await btn_jail(
            jail,
            "Started!",
            f"Error while starting the jail '{jail}'",
            start_jail
        )

    async def btn_stop_jail(jail):
        status = await status_jail(jail)

        if status == 1:
            my_notify(f"{jail} is not running", "warning")
            return

        await btn_jail(
            jail,
            "Stopped!",
            f"Error while stopping the jail '{jail}'",
            stop_jail
        )

    async def btn_restart_jail(jail):
        await btn_jail(
            jail,
            "Restarted!",
            f"Error while restarting the jail '{jail}'",
            restart_jail
        )

    async def btn_destroy_jail(jail):
        status = await status_jail(jail)

        if status == 0:
            my_notify(f"{jail} is currently running", "warning")
            return

        await btn_jail(
            jail,
            "Destroyed!",
            f"Error while destroying the jail '{jail}'",
            destroy_jail
        )

    async def btn_jail(jail, good_msg, bad_msg, callback):
        proc = await callback(jail)

        if proc.returncode == 0:
            my_notify(
                good_msg,
                "positive",
                timeout=8000
            )
        else:
            my_notify(
                bad_msg,
                "negative",
                timeout=8000
            )

        if proc.stdout.strip() == "":
            return

        open_consolelog(proc.stdout)

    with ui.dialog() as dialog, ui.card().classes("w-11/12 h-5/6"):
        dialog.props("persistent")
        dialog.open()

        button = ui.button(
            icon="close",
            color="white",
            on_click=lambda e: (dialog.close(), dialog.clear())
        )
        button.props("flat")
        button.classes("p-0")

        search = ui.input(
            label="Columns",
            value=DEFAULT_KEYWORDS,
            placeholder="Type columns ..."
        )
        search.classes("w-full")

        jails = await get_jails(["name"])

        if jails == []:
            ui.label("There are currently no jails created...").classes("text-lg italic")
            return

        with ui.list().classes("w-full").props("dense separator"):
            for jail in jails:
                jail_name = jail["name"]

                with ui.item().classes("w-full"):
                    ui.button(jail_name, on_click=display_table)\
                        .classes("w-full p-0")\
                        .props("flat color=black no-caps")

                    with ui.expansion("options").classes("w-full border-2"):
                        with ui.row():
                            with ui.button(on_click=lambda e, j=jail_name: btn_start_jail(j)).classes("p-0").props("flat"):
                                start_icon = ui.icon("circle",
                                    color="green"
                                )
                                start_icon.tooltip("start")
                                start_icon.classes("text-2xl")

                            with ui.button(on_click=lambda e, j=jail_name: btn_stop_jail(j)).classes("p-0").props("flat"):
                                stop_icon = ui.icon("circle",
                                    color="red"
                                )
                                stop_icon.tooltip("stop")
                                stop_icon.classes("text-2xl")

                            with ui.button(on_click=lambda e, j=jail_name: btn_restart_jail(j)).classes("p-0").props("flat"):
                                restart_icon = ui.icon("circle",
                                    color="yellow"
                                )
                                restart_icon.tooltip("restart")
                                restart_icon.classes("text-2xl")

                            with ui.button(on_click=lambda e, j=jail_name: btn_destroy_jail(j)).classes("p-0").props("flat"):
                                restart_icon = ui.icon("circle",
                                    color="black"
                                )
                                restart_icon.tooltip("destroy")
                                restart_icon.classes("text-2xl")
