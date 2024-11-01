# AppJail (GUI)

AppJail GUI is the graphical user interface for [AppJail](https://github.com/DtxdF/AppJail) and [Director](https://github.com/DtxdF/director), designed to be minimalistic, clean and with a basic plugin system.

## Installation

**Bleeding-edge version**:

```sh
pkg install -y py311-pipx
pipx install https://github.com/DtxdF/appjail-gui
appjail-gui --help
```

**Note**: Remember to add `~/.local/bin` to `PATH`.

[AppJail](https://appjail.readthedocs.io/en/latest/install) and [Director](https://github.com/DtxdF/director#installation) must be installed before using AppJail GUI.

### Plugins

```sh
mkdir -p ~/.appjail-gui/plugins
git clone https://github.com/DtxdF/appjail-gui-plugins.git
cp -a appjail-gui-plugins/ ~/.appjail-gui/plugins
```

**Note**: Remember to restart AppJail GUI.

### Projects

```sh
mkdir -p ~/.appjail-gui/data/projects
git clone https://github.com/DtxdF/director-projects.git
cp -a director-projects/ ~/.appjail-gui/data/projects
```

**Note**: Remember to restart AppJail GUI.

## Screenshots

<details>
    <summary>Main window</summary>
    <p align="center">
        <img src="assets/img/screenshots/1.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Project window</summary>
    <p align="center">
        <img src="assets/img/screenshots/2.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Advanced settings</summary>
    <p align="center">
        <img src="assets/img/screenshots/3.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Deploying ...</summary>
    <p align="center">
        <img src="assets/img/screenshots/4.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Deployed!</summary>
    <p align="center">
        <img src="assets/img/screenshots/5.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Workspace</summary>
    <p align="center">
        <img src="assets/img/screenshots/6.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Logs</summary>
    <p align="center">
        <img src="assets/img/screenshots/7.png" width="80%" height="auto" />
    </p>
    <p align="center">
        <img src="assets/img/screenshots/8.png" width="80%" height="auto" />
    </p>
</details>

<details>
    <summary>Jails</summary>
    <p align="center">
        <img src="assets/img/screenshots/9.png" width="80%" height="auto" />
    </p>
    <p align="center">
        <img src="assets/img/screenshots/10.png" width="80%" height="auto" />
    </p>
</details>
