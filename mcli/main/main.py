import json
import os
import random
import shutil
import time

from mcli.lib.settings import init, CURRENT_RUN_CONFIG, integrate_external_commands, get_conf, check_api, \
    view_basic_threat_summary, HOME, version_display, check_for_updates, list_plugins, compile_plugin, load_plugin
from mcli.common.banner import banner_choice
from mcli.common.cli import Parser
from mcli.lib.terminal_view import McliTerminal
from mcli.api.mapi import ExtendedMalcoreApi
from mcli.lib.logger import info, fatal, error, debug, prompt, warn
from mcli.common.check_file_type import is_elf_file, is_windows_pe_file, is_ms_doc


def main():
    opts = Parser().optparse()
    if opts.showVersion:
        version_display()
        exit(1)
    if opts.delAllHome:
        are_you_sure = prompt(
            f"this will remove the $HOME path ({HOME}) and force you to log back in, If you're trying to reset your "
            f"API key use the `--reload` flag. Are you sure you want to delete everything? [y/n]"
        )
        if are_you_sure == "y":
            try:
                shutil.rmtree(HOME)
                warn("$HOME completely removed")
            except Exception as e:
                error(f"caught error while attempting to remove home, remove manually (error: {str(e)})")
        exit(1)
    if opts.listAllPlugins:
        plugin_list = list_plugins()
        for item in plugin_list:
            print(item)
        return
    if opts.compileAllPlugins:
        compile_plugin()
        return
    if opts.loadPluginName is not None:
        name = opts.loadPluginName[0]
        args = ()
        kwargs = json.loads(opts.pluginArgs)
        loaded = load_plugin(name)
        return loaded.plugin(*args, **kwargs)
    if not opts.hideBanner:
        banner_choice()
    if opts.quickAnalysis:
        opts.skip = True
    init(reload=opts.reloadApiKey, skip_overview=opts.skip)
    if not opts.skipVerCheck:
        check_for_updates()
    Parser().write_config(opts)
    current_running_conf = json.load(open(CURRENT_RUN_CONFIG))
    if not current_running_conf["quickAnalysis"]:
        external_commands = integrate_external_commands(opts.importExternal)
        McliTerminal(external_commands).terminal_main()
    else:
        if opts.workingFile1 is None:
            error("need a working file to perform quick analysis pass the `-f` flag")
        else:
            filename1 = opts.workingFile1
            mcli_conf = get_conf()
            api = ExtendedMalcoreApi(mcli_conf['api_key'])
            if is_windows_pe_file(filename1) or is_elf_file(filename1):
                endpoint = api.executable_file_analysis
            elif is_ms_doc(filename1):
                endpoint = api.document_file_analysis
            else:
                endpoint = None
            if endpoint is None:
                error("filetype is unknown cannot perform quick analysis on unknown file type")
            else:
                debug("checking API connection")
                is_available = check_api()
                if is_available:
                    info("API connection is available starting file upload")
                    try:
                        results = endpoint(filename1)
                        if results['data'] is not None:
                            info(
                                f"current UUID to process: {results['data']['uuid']}, "
                                f"and file status: {results['data']['status']}"
                            )
                            is_done = False
                            attempt = 0
                            while not is_done:
                                current_results = api.status_check(results['data']['uuid'])
                                if "status" in current_results.keys():
                                    attempt += 1
                                    # 0.4, 1.6, 6.4, ...
                                    sleep_time = random.uniform(0, 4 ** attempt * 100 / 1000.0)
                                    debug(f"file is not done processing, sleeping for {round(sleep_time, 2)} seconds")
                                    time.sleep(sleep_time)
                                else:
                                    info("file is done processing, dumping threat summary")
                                    threat_data = current_results['threat_score']
                                    view_basic_threat_summary({"threat_score": threat_data['results']})
                                    is_done = True
                            if opts.deleteAfterAnalysis:
                                debug("file deletion requested after quick analysis")
                                try:
                                    os.remove(filename1)
                                    info("file deleted successfully")
                                except Exception as e:
                                    error(f"caught an error trying to delete the file: {str(e)}")
                    except Exception as e:
                        fatal(f"caught error: {str(e)} while analyzing file: {filename1}")
