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

import os

from nicegui import run, ui

from appjail_gui.tools.notification import my_notify
from appjail_gui.tools.text import sansi

async def listfiles_window(directory):
    with ui.dialog() as dialog, ui.card().classes("w-10/12 h-4/6"):
        dialog.props("persistent")
        dialog.open()

        ui.label(f"{directory}:").props("header").classes("text-bold")

        with ui.list().classes("w-full"):
            for dirpath, _, filenames in os.walk(directory):
                for file in filenames:
                    pathname = os.path.join(dirpath, file)

                    with open(pathname) as fd:
                        content = await run.io_bound(fd.read)

                        display_name = os.path.join(
                            os.path.basename(dirpath), file
                        )

                        ui.item(display_name,
                            on_click=lambda e, c=content: open_consolelog(c)
                        ).classes("border-2")

        ui.separator()

        ui.button("Close",
            icon="close",
            color="white",
            on_click=lambda e: (dialog.close(), dialog.clear())
        )

def open_consolelog(text, after_close=lambda: None):
    text = sansi(text)

    if text == "":
        my_notify("This log has no content!", "warning")
        return

    with ui.dialog() as log_dialog, ui.card().classes("w-10/12 h-4/6"):
        log_dialog.props("persistent")
        log_dialog.open()

        ui.label("Console Log:").props("header").classes("text-bold")

        with ui.scroll_area().classes("w-full h-full border-2"):
            ui.label(text).style("white-space: pre-wrap")

        ui.button("Close",
            icon="close",
            color="white",
            on_click=lambda e: (log_dialog.close(), log_dialog.clear(), after_close())
        )
