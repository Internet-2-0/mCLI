import os
import sys
import shutil

from setuptools import find_packages, setup
from mcli.__version__ import VERSION_NUM


PLUGIN_PATH = f"{os.path.expanduser('~')}/.mcli_plugins"


def monkey_patch():
    """
    msdk has an issue in it where it fails to install the requests package. This work around makes
    it so that we can install and continue on
    """
    import pip, pkg_resources

    installed_packages = sorted([f"{p.key}" for p in pkg_resources.working_set])
    if "wheel" not in installed_packages:
        pip.main(["install", "wheel"])
    if "tabulate" not in installed_packages:
        pip.main(["install", "tabulate"])
    if "win" in sys.platform:
        pip.main(["install", "pyreadline3"])
    pip.main(["install", "msdk==0.1.6.8"])


def move_plugins():
    current_plugin_path = f"{os.getcwd()}/mcli/plugins"
    if not os.path.exists(PLUGIN_PATH):
        os.makedirs(PLUGIN_PATH)
    for file_ in os.listdir(current_plugin_path):
        try:
            shutil.copy(f"{current_plugin_path}/{file_}", PLUGIN_PATH)
        except:
            print(f"file: {file_} failed to move, skipping")


if __name__ == "__main__":
    move_plugins()
    setup(
        name="mcli",
        packages=find_packages(),
        version=VERSION_NUM,
        description="mCLI is a CLI application used to analyze malware using Malcore directly from your terminal",
        author="Thomas Perkins",
        author_email="contact@malcore.io",
        install_requires=["requests", "tabulate"],
        long_description=open("README.md").read(),
        long_description_content_type='text/markdown',
        url='https://github.com/Internet-2-0/mCLI',
        entry_points={
            'console_scripts': [
                'mcli=mcli.cli_tool:run'
            ]
        }
    )

    monkey_patch()
