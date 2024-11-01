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

import asyncio
import os
import zipfile

from nicegui import run, ui
from nicegui.logging import log
from starlette.formparsers import MultiPartParser

from appjail_gui.tools.constants import *
from appjail_gui.tools.notification import my_notify

descr = "Upload a zipped file with a project"

MultiPartParser.max_file_size = 2**20 * 16

async def main():
    def handle_reject(e):
        my_notify(
            "Can't upload the selected files, please be sure to choose only ZIP files",
            "negative"
        )

    async def handle_multi_upload(e):
        try:
            zip_files = await get_files_from_zip(e.contents, e.names)
        except (zipfile.BadZipFile, zipfile.LargeZipFile) as err:
            log.exception("Error caused while opening the ZIP content:")
            my_notify("Bad ZIP file or invalid format", "negative")
            return

        if zip_files is None:
            return

        for zip_filename, files in zip_files.items():
            (project, _) = os.path.splitext(zip_filename)

            rootdir = os.path.join(PROJECTS, project)

            os.makedirs(rootdir, exist_ok=True)

            for filename, content in files.items():
                pathname = os.path.join(rootdir, filename)

                if content is None:
                    os.makedirs(pathname, exist_ok=True)
                else:
                    with open(pathname, "wb") as fd:
                        await run.io_bound(fd.write, content)

        ui.navigate.reload()

    async def get_files_from_zip(contents, names):
        index = 0
        zip_contents = {}

        for content in contents:
            zip_filename = names[index]
            index += 1
            files = {}

            with zipfile.ZipFile(content) as zip_obj:
                for file in zip_obj.namelist():
                    if file.endswith("/"):
                        file_content = None
                    else:
                        file_content = await run.io_bound(zip_obj.read, file)

                    files[file] = file_content

            if files.get("appjail-director.yml") is None \
                    or files.get("info.json") is None:
                my_notify(
                    f"'appjail-director.yml' and 'info.json' are required but one of them are not included in the ZIP file '{zip_filename}'",
                    "negative"
                )
                return

            zip_contents[zip_filename.lower()] = files

            return zip_contents

    with ui.dialog() as dialog, ui.card(align_items="center").classes("w-11/12 h-2/4"):
        dialog.props("persistent")
        dialog.open()

        button = ui.button(
            icon="close",
            color="white",
            on_click=lambda e: (dialog.close(), dialog.clear())
        )
        button.props("flat")
        button.classes("p-0 mr-auto")

        upload = ui.upload(
            label="Projects",
            multiple=True,
            on_multi_upload=handle_multi_upload,
            auto_upload=True,
            on_rejected=handle_reject
        )
        upload.props("accept=.zip")
        upload.classes("w-full h-full")
