import os
import json
import argparse

import mcli.lib.settings as settings


class Parser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()

    @staticmethod
    def write_config(opts):
        filename = settings.CURRENT_RUN_CONFIG
        if os.path.exists(filename):
            writer = 'w'
        else:
            writer = 'a+'
        if not opts.quickAnalysis:
            opts.runWizard = True
        if opts.quickAnalysis:
            opts.skip = True
        with open(filename, writer) as fh:
            json.dump(opts.__dict__, fh)

    @staticmethod
    def optparse():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--wizard", action="store_true", dest="runWizard", default=False,
            help="Drop into the mCLI terminal, this is default"
        )
        parser.add_argument(
            "-f1", "--filename1", default=None, dest="workingFile1",
            help="Set the working file filename1 to this file and continue"
        )
        parser.add_argument(
            "-q", "--quick-analysis", action="store_true", default=False, dest="quickAnalysis",
            help="Don't drop into the terminal and perform an analysis of the passed working file and exit"
        )
        parser.add_argument(
            "--external-path", default="/usr/bin,/usr/local/bin,/bin", dest="importExternal",
            help="Pass external paths to load external commands into the terminal. Must use a comma between paths"
        )
        parser.add_argument(
            "-f2", "--filename2", default=None, dest="workingFile2",
            help="Set the working file filename2 to this path"
        )
        parser.add_argument(
            "--group-by", default=5, type=int, dest="groupByIntReuse", choices=[5, 10, 15],
            help="Edit the group by integer for code reuse"
        )
        parser.add_argument(
            "--reload", default=False, action="store_true", dest="reloadApiKey",
            help="Reload your API key"
        )
        parser.add_argument(
            "--skip", default=False, action="store_true", dest="skip",
            help=argparse.SUPPRESS
        )
        parser.add_argument(
            "--hide", default=False, action="store_true", dest="hideBanner",
            help="Hide the welcome banner"
        )
        parser.add_argument(
            "--del-all", default=False, action="store_true", dest="delAllHome",
            help="Completely remove the mCLI home path"
        )
        parser.add_argument(
            "--version", default=False, action="store_true", dest="showVersion",
            help="Show program version and exit"
        )
        parser.add_argument(
            "--skip-ver-check", default=False, action="store_true", dest="skipVerCheck",
            help=argparse.SUPPRESS
        )
        parser.add_argument(
            "--delete-file", default=False, action="store_true", dest="deleteAfterAnalysis",
            help="Delete the file after it has been analyzed"
        )
        parser.add_argument(
            "--compile-plugins", default=False, action="store_true", dest="compileAllPlugins",
            help=f"Attempt to compile plugins that are located in the plugin directory "
                 f"(location: {settings.PLUGIN_PATH})"
        )
        parser.add_argument(
            "--list-plugins", default=False, action="store_true", dest="listAllPlugins",
            help="List all available loadable plugins"
        )
        parser.add_argument(
            "--load-plugin", nargs=1, default=None, dest="loadPluginName",
            help=f"Load a plugin by passing the name of the plugin to load"
        )
        parser.add_argument(
            "--plugin-args", type=str, default="{}", dest="pluginArgs",
            help="Pass plugin arguments to start the plugin. Must be JSON encodable"
        )
        return parser.parse_args()
