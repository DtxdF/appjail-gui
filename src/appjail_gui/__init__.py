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
import inspect
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

import commentjson
import starlette.exceptions

from appjail_gui.tools.constants import *
from appjail_gui.tools.director import check_project
from appjail_gui.tools.director import destroy_project
from appjail_gui.tools.director import destroy_workspace
from appjail_gui.tools.director import deploy_project
from appjail_gui.tools.director import down_project
from appjail_gui.tools.director import get_project_info
from appjail_gui.tools.director import get_projects
from appjail_gui.tools.files import listfiles_window
from appjail_gui.tools.files import open_consolelog
from appjail_gui.tools.notification import my_notify
from appjail_gui.tools.process import run_proc
from appjail_gui.tools.sysexits import *

if NATIVE_MODE:
    import multiprocessing

    multiprocessing.set_start_method("spawn", force=True)

from nicegui import app, Client, run, ui
from nicegui.logging import log
from nicegui.page import page

projects_refreshable = None

@ui.page("/", response_timeout=RESPONSE_TIMEOUT)
async def main():
    for program in REQUIREMENTS: 
        if shutil.which(program) is None:
            log.error(f"{program}: Program required but not found.")
            sys.exit(EX_UNAVAILABLE)

    ui.add_head_html("<link href=\"https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css\" rel=\"stylesheet\" />")

    with ui.card().classes("w-full items-center"):
        with ui.tabs() as tabs:
            tab_store = ui.tab("Store", icon="store")
            tab_workspace = ui.tab("Workspace", icon="workspaces")
            tab_plugins = ui.tab("Plugins", icon="extension")

    with ui.tab_panels(tabs, value="Store").classes("w-full items-center"):
        with ui.tab_panel("Store").classes("w-full items-center"):
            await write_store()

        with ui.tab_panel("Workspace").classes("w-full items-center"):
            await write_workspace()

        with ui.tab_panel("Plugins").classes("w-full items-center"):
            await write_plugins()

async def write_store():
    global applications
    global grid_applications

    applications = await get_applications()

    search = ui.input(placeholder="Search ...", on_change=add_applications)
    search.classes("w-full")

    grid_applications = ui.grid(columns=1).classes("w-full items-center")

    add_applications(None)

async def get_applications():
    result = {}

    if not os.path.isdir(PROJECTS):
        return result

    apps = os.listdir(PROJECTS)

    for app in apps:
        project = os.path.join(PROJECTS, app)
        director_file = os.path.join(project, DIRECTOR_FILE)
        info_file = os.path.join(project, INFO_FILE)

        if not os.path.isfile(info_file):
            log.warning(f"{project}: The project doesn't have an information file.")
            continue

        if not os.path.isfile(director_file):
            log.warning(f"{project}: The project doesn't have a director file.")
            continue

        with open(info_file) as fd:
            try:
                info = commentjson.loads(await run.io_bound(fd.read))
            except:
                log.exception(f"An exception occurred while parsing 'info.json' of '{app}'")
                continue
            
            appname = info.get("name", app)

            result[appname] = info

    return result

def add_applications(e):
    if e is None:
        match = None
    else:
        match = e.sender.value

    with grid_applications:
        grid_applications.clear()

        for app_name in applications:
            application = applications[app_name]
            projectdir = os.path.join(PROJECTS, app_name.lower())
            app_image = os.path.join(projectdir, application.get("image", NOIMAGE))
            app_descr = application.get("description", NODESCR)
            app_www = application.get("www", NOWWW)

            if match is not None \
                and match.lower() not in app_name.lower():
                    continue

            with ui.button(app_name, on_click=open_dialog).props("color=white no-caps").tooltip(app_name):
                ui.image(app_image)\
                    .props(f"width={IMAGE_WIDTH}px height={IMAGE_HEIGHT}")

                ui.separator().style("margin-top: 10px")

                ui.label(app_descr)\
                    .style("color: black")

async def open_dialog(e):
    appname = e.sender.text

    info = applications[appname]
    appdir = os.path.join(PROJECTS, appname.lower())
    director_file = os.path.join(appdir, DIRECTOR_FILE)
    env_file = os.path.join(appdir, ENV_FILE)
    director_file_code = None
    env_file_code = None
    extra_files = info.get("extra-files")
    extra_forms = {}

    async def deploy_app(e):
        project = project_name.value
        workspace = os.path.join(WORKSPACES, project)
        done_file = os.path.join(workspace, DONE_FILE)
        inprogress_file = os.path.join(workspace, INPROGRESS_FILE)

        if os.path.isfile(inprogress_file):
            my_notify(
                f"{project}: The project is currently being deployed.",
                "warning"
            )

            return

        project_deployed = await run.cpu_bound(check_project, project)

        if project_deployed == 0 \
                and os.path.isfile(done_file):
            my_notify(
                f"{project}: The project already exists!",
                "negative"
            )

            return
        elif project_deployed == EX_NOINPUT:
            pass
        else:
            await run.cpu_bound(destroy_project, project, workspace)

        loading_spinner.visible = True

        if os.path.isdir(workspace):
            shutil.rmtree(workspace)

        shutil.copytree(appdir, workspace,
            symlinks=True
        )

        director_file = os.path.join(workspace, DIRECTOR_FILE)

        with open(director_file, "w") as fd:
            await run.io_bound(fd.write, director_file_code.value)

        env_file = os.path.join(workspace, ENV_FILE)

        with open(env_file, "w") as fd:
            if env_file_code is not None:
                env_file_content = env_file_code.value
            else:
                env_file_content = ""

            await run.io_bound(fd.write, env_file_content)

        with open(inprogress_file, "w") as fd:
            await run.io_bound(fd.write, "")

        for extra_filename, extra_form in extra_forms.items():
            extra_outname = os.path.join(workspace, extra_filename)

            with open(extra_outname, "w") as fd:
                await run.io_bound(fd.write, extra_form.value)

        proc = await run.cpu_bound(deploy_project, project, workspace)

        loading_spinner.visible = False

        if proc.returncode == 0:
            shutil.move(inprogress_file, done_file)

            my_notify(
                f"{project}: Deployed!",
                "positive",
                timeout=8000
            )

            open_consolelog(proc.stdout, lambda: (dialog.close(), dialog.clear()))

            if projects_refreshable is not None:
                await projects_refreshable(None)
                projects_refreshable.refresh()
        else:
            my_notify(
                f"{project}: An error ocurred while deploying the project",
                "negative",
                timeout=8000
            )

            open_consolelog(proc.stdout)

            os.remove(inprogress_file)

    async def save_template(e):
        director_file = os.path.join(appdir, DIRECTOR_FILE)

        with open(director_file, "w") as fd:
            await run.io_bound(fd.write, director_file_code.value)

        if env_file_code is not None:
            env_file = os.path.join(appdir, ENV_FILE)

            with open(env_file, "w") as fd:
                await run.io_bound(fd.write, env_file_code.value)

        for extra_filename, extra_form in extra_forms.items():
            extra_outname = os.path.join(appdir, extra_filename)

            with open(extra_outname, "w") as fd:
                await run.io_bound(fd.write, extra_form.value)

        my_notify("Saved!", "positive")

    async def btn_destroy_project(e):
        shutil.rmtree(appdir)

        ui.navigate.reload()

    def close_dialog(d):
        if loading_spinner.visible:
            my_notify(
                "There is a project currently being deployed, please wait",
                "warning"
            )
            return

        d.close()
        d.clear()

    with ui.dialog() as dialog, ui.card().classes("w-11/12 h-5/6"):
        dialog.props("persistent")
        dialog.open()

        with ui.row().classes("w-full"):
            ui.label("Project Description").props("header").classes("text-lg")

            close_button = ui.button(
                icon="close",
                color="white",
                on_click=lambda e, d=dialog: close_dialog(d)
            )
            close_button.props("flat")
            close_button.classes("p-0 ml-auto")

        ui.separator()

        project_name = ui.input(
            value=appname,
            label="Project",
            placeholder="e.g.: web-server",
            validation=lambda v: "Invalid project name!" if re.match(r"^[a-zA-Z0-9._-]+$", v) is None else None
        )

        with ui.expansion("Advanced Settings") as advanced_settings:
            advanced_settings.classes("w-full")

            ui.label("Director File:").props("header").classes("text-bold")

            with open(director_file) as fd:
                director_file_code = ui.codemirror(await run.io_bound(fd.read),
                    language="yaml",
                    theme=EDITOR_THEME,
                    indent=EDITOR_INDENT
                )

            if env_file is not None \
                    and os.path.isfile(env_file):
                ui.label("Environment:").props("header").classes("text-bold")

                with open(env_file) as fd:
                    env_file_code = ui.codemirror(await run.io_bound(fd.read),
                        theme=EDITOR_THEME,
                        indent=EDITOR_INDENT
                    )

            if extra_files is not None:
                for name in extra_files:
                    extra_file = extra_files[name]
                    filename = extra_file.get("filename", name)
                    pathname = os.path.join(appdir, filename)

                    ui.label(f"{name}:").props("header").classes("text-bold")

                    with open(pathname) as fd:
                        extra_forms[filename] = ui.codemirror(await run.io_bound(fd.read),
                            language=extra_file.get("lang"),
                            theme=EDITOR_THEME,
                            indent=EDITOR_INDENT
                        )

        ui.separator()

        with ui.row():
            ui.button("Deploy",
                icon="eva-checkmark-outline",
                color="white",
                on_click=deploy_app
            )

            ui.button("Save",
                icon="save",
                color="white",
                on_click=save_template
            )

            ui.button("Destroy",
                icon="delete",
                color="white",
                on_click=btn_destroy_project
            )

            loading_spinner = ui.spinner("tail",
                color="black",
                size="2em"
            )

            loading_spinner.visible = False

async def write_workspace():
    global grid_projects
    global projects_refreshable

    search = ui.input(placeholder="Search ...", on_change=add_workspaces)
    search.classes("w-full")

    grid_projects = ui.grid(columns=1).classes("w-full border-2")

    projects_refreshable = ui.refreshable(add_workspaces)
    await projects_refreshable(None)

async def add_workspaces(e):
    if e is None:
        match = None
    else:
        match = e.sender.value

    projects = await run.cpu_bound(get_projects)

    async def up_project_window(project):
        await project_window(
            project,
            deploy_project
        )

    async def down_project_window(project):
        await project_window(
            project,
            down_project
        )

    async def destroy_project_window(project):
        await project_window(
            project,
            destroy_project
        )

    async def destroy_workspace_window(project):
        await project_window(
            project,
            destroy_workspace
        )

    async def project_window(project, cmd):
        workspace = os.path.join(WORKSPACES, project)

        proc = await run.cpu_bound(cmd, project, workspace)

        await projects_refreshable(None)
        projects_refreshable.refresh()

    async def logs_window(project):
        chk = await run.cpu_bound(check_project, project)

        if chk == EX_NOINPUT:
            my_notify(
                f"{project}: It has not been possible to read the log of this project",
                "warning"
            )
            return

        info = get_project_info(project)
        last_log = info["last_log"]

        await listfiles_window(last_log)

    with grid_projects:
        grid_projects.clear()

        for name in projects:
            if match is not None \
                and match.lower() not in name.lower():
                    continue

            status = projects[name]

            if status == "+":
                status = "DONE"
                color = "green"
            elif status == "-":
                status = "FAILED"
                color = "red"
            elif status == "!":
                status = "UNFINISHED"
                color = "brown"
            elif status == "x":
                status = "DESTROYING"
                color = "yellow"
            else:
                status = "UNKNOWN"
                color = "blue"

            with ui.row().classes("w-full pt-3 pl-3 pr-3 pb-3"):
                status_icon = ui.icon("circle",
                    color=color
                )
                status_icon.tooltip(status)
                status_icon.classes("text-2xl")

                ui.label(name).classes("text-xl")

                with ui.button(on_click=lambda e, p=name: destroy_workspace_window(p)) as button:
                    button.classes("p-0 ml-auto")
                    button.props("flat")
                    button.tooltip("destroy workspace")

                    ui.icon("close", color="black")

                with ui.expansion("options").classes("w-full border-2"):
                    with ui.row():
                        with ui.button(on_click=lambda e, p=name: up_project_window(p)) as button:
                            button.classes("p-0")
                            button.props("flat")
                            button.tooltip("start")

                            ui.icon("play_arrow", color="black")

                        with ui.button(on_click=lambda e, p=name: down_project_window(p)) as button:
                            button.classes("p-0")
                            button.props("flat")
                            button.tooltip("stop")

                            ui.icon("stop", color="black")

                        with ui.button(on_click=lambda e, p=name: destroy_project_window(p)) as button:
                            button.classes("p-0")
                            button.props("flat")
                            button.tooltip("destroy")

                            ui.icon("delete", color="black")

                        with ui.button(on_click=lambda e, p=name: logs_window(p)) as button:
                            button.classes("p-0")
                            button.props("flat")
                            button.tooltip("logs")

                            ui.icon("troubleshoot", color="black")

    if len(projects) == 0:
        ui.label("No project has been created ...").classes("text-lg italic")

async def write_plugins():
    os.makedirs(PLUGINS, exist_ok=True)

    plugins = os.listdir(PLUGINS)

    if len(plugins) == 0:
        ui.label("No plugin has been added ...").classes("text-lg italic")
        return

    with ui.list().classes("w-full"):
        for plugin in plugins:
            (plugin_name, _) = os.path.splitext(plugin)

            plugin_file = os.path.join(PLUGINS, f"{plugin_name}.py")

            if not os.path.isfile(plugin_file):
                continue

            mod_name = "appjail_gui.plugins.%s" % plugin_name
            spec = importlib.util.spec_from_file_location(
                mod_name,
                plugin_file
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)

            chk_attr_main = hasattr(mod, "main")
            chk_attr_descr = hasattr(mod, "descr")

            if not chk_attr_main:
                log.warning(f"Plugin '{plugin_file}' doesn't have the 'main' function.")
                continue

            if not chk_attr_descr:
                log.warning(f"Plugin '{plugin_file}' doesn't have the 'descr' attribute.")
                continue

            with ui.item(on_click=mod.main).classes("border-2"):
                with ui.row():
                    ui.label(f"{plugin_name}:").props("header").classes("text-bold")

                    ui.label(mod.descr)

@app.exception_handler(500)
@app.exception_handler(404)
async def exception_handler(request, exc):
    with Client(page(""), request=request) as client:
        if isinstance(exc, starlette.exceptions.HTTPException):
            status_code = exc.status_code
        else:
            status_code = 500

        if 400 <= status_code <= 499:
            title = "This page doesn't exist."
        elif 500 <= status_code <= 599:
            title = 'Server error'
        else:
            title = 'Unknown error'

        if isinstance(exc, str):
            message = exc
        else:
            message = exc.__class__.__name__
            if str(exc):
                message += ': ' + str(exc)

        with ui.dialog() as dialog, ui.card(align_items="center").classes("w-full h-4/5"):
            dialog.open()
            dialog.props("persist")

            with ui.column().style('width: 100%; padding: 1rem 0; align-items: center; gap: 0'):
                with ui.link(target="/"):
                    ui.image(IMAGOTYPE).classes("w-72")
                ui.separator()
                ui.label(str(status_code)).style('font-size: 3.75rem; line-height: 1; padding: 1.25rem 0')
                ui.label(title).style('font-size: 1.25rem; line-height: 1.75rem; padding: 1.25rem 0')
                ui.label(message).style('font-size: 1.125rem; line-height: 1.75rem; color: rgb(107 114 128)')

        return client.build_response(request, status_code)

def cli():
    try:
        ui.run(
            host=HOST_ADDR,
            port=HOST_PORT,
            favicon=PAGE_FAVICON,
            title=PAGE_TITLE,
            reload=False,
            native=NATIVE_MODE
        )
    except KeyboardInterrupt:
        pass
