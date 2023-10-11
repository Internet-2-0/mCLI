import json

from mcli.lib.settings import init, CURRENT_RUN_CONFIG, integrate_external_commands
from mcli.common.banner import banner_choice
from mcli.common.cli import Parser
from mcli.lib.terminal_view import McliTerminal


def main():
    banner_choice()
    init()
    opts = Parser().optparse()
    Parser().write_config(opts)
    current_running_conf = json.load(open(CURRENT_RUN_CONFIG))
    if not current_running_conf["quickAnalysis"]:
        external_commands = integrate_external_commands(opts.importExternal)
        exit(1)
        McliTerminal(external_commands).terminal_main()

