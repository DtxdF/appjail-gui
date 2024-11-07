from setuptools import setup, find_packages

VERSION = "0.0.1"

def get_description():
    return "\
AppJail GUI is the graphical user interface for AppJail and Director, \
designed to be minimalistic, clean and with a basic plugin system. \
It can be used as a desktop application thanks to pywebview or \
simply through the web browser like any other NiceGUI application."

setup(
    name="appjail-gui",
    version=VERSION,
    description="Graphical User Interface for AppJail",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    author="Jesús Daniel Colmenares Oviedo",
    author_email="DtxdF@disroot.org",
    url="https://github.com/DtxdF/appjail-gui",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    package_dir={"" : "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    license="BSD 3-Clause",
    license_files="LICENSE",
    install_requires=[
        "nicegui",
        "commentjson"
    ],
    entry_points={
        "console_scripts" : [
            "appjail-gui = appjail_gui.__init__:cli"
        ]
    }
)
