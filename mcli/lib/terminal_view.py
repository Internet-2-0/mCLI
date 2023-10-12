import os
import json
import random

import mcli.lib.logger as log
import mcli.lib.settings as settings
import mcli.api.mapi as mcli_api


class McliTerminal(object):

    terminal_commands = (
        "search", "analyze", "hashsum",
        "status", "quit", "help", "?",
        "analysis", "check", "uuid",
        "hashes", "hash", "exit",
        "cache", "show", "newfile",
        "showfile", "info", "information",
        "anal", "external", "ca", "sho",
        "ex", "qu", "ext", "sea", "new",
        "uu", "re", "reuse", "groupby",
        "ex", "exif", "key", "apikey",
        "del", "delete", "vi", "view",
        "sw", "swap", "fileswap", "ping",
        "ver", "version"
    )
    loaded_external_commands = []

    def __init__(self, external_commands):
        self.terminal_start = "\033[94mroot\033[0m@\033[93mmcli\033[0m:\033[91m~/.malcore\033[0m# "
        self.quit_terminal = False
        self.external_commands = external_commands

    def load_external(self):
        self.loaded_external_commands = self.external_commands

    def get_choice(self):
        original_choice = input(f"{self.terminal_start}")
        try:
            check_choice = original_choice.split(" ")[0]
        except:
            check_choice = original_choice
        if check_choice in self.terminal_commands:
            return "local", original_choice
        elif check_choice in self.loaded_external_commands:
            return "external", original_choice
        else:
            return "unknown", original_choice

    @staticmethod
    def no_working_file(secondary=False):
        if not secondary:
            log.warn(
                "there is currently no working file, load the file with `newfile 1 filename` "
                "see `help` for more information"
            )
        else:
            log.warn(
                "there is not secondary working file processed, to add a secondary working file "
                "run `newfile 2 filename`. See `help for more info"
            )

    def help_menu(self):
        print("""\n
Available Commands:             Description:
------------------              ------------\n
help|?                          Print this help
sea[rch]|check|uu[id] [UUID]    Provide a UUID to check the status of your upload
anal[ysis|yze]                  Start full analysis on the current working file
hash[sum|es]                    Gather hashsums of the current working file
ca[che]|sho[w]                  Show the current stored UUID's
new[file] [*1|2] [FILE]         Pass to change the current working files
showfile                        Pass to show the current working files
ext[ernal]                      View integrated external commands
re[use]                         Pass to perform code reuse analysis on two files
groupby [*5|10|15]              Pass to change the 'group_by' integer for code reuse analysis
ex[if]                          Gather exif data from the current working file
[api]key                        View your current saved API key
ex[it]|qu[it]                   Pass this to exit the terminal
del[ete] UUID                   Manually remove a UUID from the cache list
vi[ew]                          List your available endpoints with your plan and your scans per month
[file]sw[ap]                    Swap working files, filename1 -> filename2; filename2 -> filename1
ping                            Ping the Malcore API to see if it's online
ver[sion]                       Show current program version
\n""")

    def do_exit(self):
        import time
        exit_sayings = (
            "fine we didn't wanna hangout with you anyways!!",
            "you don't have to go home, but you can't stay here ...",
            "every exit is the entry to somewhere else, or something like that?",
            "if you don't find what you're looking for you can always come back here!",
            "remember it's all fun and games until the toaster sends encrypted messages!",
            "exiting mCLI, remember reality is overrated ...",
            "farewell hexidecimal detective, go decode some sunshine!",
            "exiting RE mode: hope you didn't leave any breadcrumbs for the AI overlords!",
            "reversing files is easier than deciphering human behavior ...",
            "leaving the Matrix ...", "`shutdown -t now -r`", "shutting down mCLI"
        )
        saying = random.SystemRandom().choice(exit_sayings)
        print(f"[::][{time.strftime('%H:%M:%S')}] {saying}")
        self.quit_terminal = True

    def perform_external_command(self, command):
        import subprocess

        subprocess.call(command, shell=True)

    def terminal_main(self):
        conf_file = settings.CONFIG_FILE
        passed_config = settings.CURRENT_RUN_CONFIG
        api = mcli_api.ExtendedMalcoreApi(json.load(open(conf_file))["api_key"])
        data = json.load(open(passed_config))
        filename = data["workingFile1"]
        if filename is not None:
            if not os.path.exists(filename):
                log.warn(f"filename1=@{filename} does not exist, defaulting to `None`")
                filename = None
        secondary_filename = data["workingFile2"]
        if secondary_filename is not None:
            if not os.path.exists(secondary_filename):
                log.warn(f"filename2=@{secondary_filename} does not exist, defaulting to `None`")
                secondary_filename = None
        if filename is None and secondary_filename is not None:
            log.warn("cannot set filename2 without filename1 defaulting to `None`")
            secondary_filename = None
        group_by_int = data['groupByIntReuse']
        self.load_external()
        log.info(f"current working files: filename1=@{filename} filename2=@{secondary_filename}")
        log.debug("checking API connection")
        is_available = settings.check_api()
        if is_available:
            log.info("API is running as expected")
        else:
            log.warn("API is not available currently, use the `ping` command to test connection")
        log.debug("to see the help menu type `help` or `?`")
        try:
            while not self.quit_terminal:
                try:
                    choice_type, choice = self.get_choice()
                    if choice_type == "unknown":
                        log.warn(f"unknown choice: '{choice}' passed, for help type `help`")
                    elif choice_type == "external":
                        self.perform_external_command(choice)
                    elif choice in ("ver", "version"):
                        settings.version_display()
                    elif choice in ("ping",):
                        log.info("checking if API is online")
                        settings.check_api(speak=True, ping_test=True)
                    elif choice in ("sw", "fileswap", "swap"):
                        filename, secondary_filename = secondary_filename, filename
                        log.info(f"filename1=@{filename}; filename2=@{secondary_filename}")
                    elif choice in ("vi", "view"):
                        conf = settings.get_conf()
                        print("Endpoint name,Monthly limit\n---------------------------")
                        for endpoint in conf['available_endpoints']:
                            print(f"{endpoint['endpoint_name']},{endpoint['monthly_limit']}")
                    elif any(c in choice for c in ("del", "delete")):
                        uuid_to_remove = choice.split(" ")
                        if uuid_to_remove == "" or len(uuid_to_remove) == 1:
                            log.warn("no UUID passed, you must pass a UUID to remove one manually")
                        else:
                            uuid = uuid_to_remove[-1]
                            settings.uuid_cache(uuid, delete_uuid=True)
                    elif choice in ("ex", "exif"):
                        log.info(f"gathering exif data out of current working file (filename1=@{filename})")
                        results = api.parse_exif_data(filename)['data']
                        settings.view_exif_data(results)
                    elif choice in ("key", "apikey"):
                        file_ = settings.CONFIG_FILE
                        data = json.load(open(file_))["api_key"]
                        log.info(f"current loaded API key: {data}")
                        log.warn(
                            "you cannot change your API key from the terminal view. To reset your API key restart mCLI "
                            "with the `--reload` flag."
                        )
                    else:
                        if choice in ("?", "help"):
                            self.help_menu()
                        elif any(c in choice for c in ["groupby",]):
                            choices = (5, 10, 15)
                            integer_passed = choice.split(" ")[-1]
                            try:
                                integer_passed = int(integer_passed)
                                if integer_passed in choices:
                                    group_by_int = integer_passed
                                    log.info(f"group_by integer changed to: {integer_passed}")
                                else:
                                    log.warn(
                                        f"integer is not in choice list of "
                                        f"{','.join([str(i) for i in choices])}, will not change"
                                    )
                            except Exception as e:
                                log.error(f"unable to change group_by integer, received error: '{str(e)}'")
                                pass
                        elif choice in ("re", "reuse"):
                            if filename is None:
                                self.no_working_file()
                            elif secondary_filename is None:
                                self.no_working_file(secondary=True)
                            else:
                                log.info(
                                    f"performing code reuse: filename1=@{filename}"
                                    f" filename2=@{secondary_filename}"
                                )
                                results = api.code_reuse(filename, secondary_filename)
                                log.info(
                                    f"defaulting to group by integer: {group_by_int} "
                                    f"(pass --group-by INT to change or change with `groupby INT`)"
                                )
                                if group_by_int == 5:
                                    to_show = results['data']['group_by_5']
                                elif group_by_int == 10:
                                    to_show = results['data']['group_by_10']
                                elif group_by_int == 15:
                                    to_show = results['data']['group_by_15']
                                else:
                                    log.warn("we're not sure how you got here, so we're defaulting to 5")
                                    to_show = results['data']['group_by_5']
                                for key in to_show['results'].keys():
                                    log.info(f"results that are: {key.replace('_', ' ')}")
                                    for item in to_show['results'][key]:
                                        if not item == 'no code reuse discovered':
                                            settings.compare_assembly_code(item[0], item[1], match_percent=item[-1])
                                            input("Press enter to continue ...")
                                        else:
                                            log.warn("no results for associated key")
                        elif choice in ("info", "information"):
                            if filename is None:
                                self.no_working_file()
                            else:
                                results = settings.get_file_basic_info(filename)
                                log.info(f"basic file information for working file: '{filename}'")
                                for key in results.keys():
                                    try:
                                        print(f"\t- {key}: {results[key]}")
                                    except:
                                        print(f"\t- {key}: {results[key]}")
                        elif choice in ("external", "ext"):
                            log.info(f"total of {len(self.loaded_external_commands)} external command(s) integrated")
                            question = log.prompt("print all external commands")
                            if question.lower() == "y":
                                print(",".join(self.loaded_external_commands))
                        elif choice in ("analyze", "analysis", "anal"):
                            too_many_uuids = settings.uuid_cache(None, count_all=True)
                            if not too_many_uuids:
                                if filename is None:
                                    self.no_working_file()
                                else:
                                    file_type = settings.file_type_pointer(filename)
                                    if file_type[0] and not file_type[1] and not file_type[2]:
                                        log.info("file appears to be a Windows PE file, analyzing as such")
                                        results = api.executable_file_analysis(filename)
                                    elif not file_type[0] and file_type[1] and not file_type[2]:
                                        log.info("file appears to be a ELF file, analyzing as such")
                                        results = api.executable_file_analysis(filename)
                                    elif not file_type[0] and not file_type[1] and file_type[2]:
                                        log.info("file appears to be a MS Doc file, analyzing as such")
                                        results = api.document_file_analysis(filename)
                                    else:
                                        log.warn("file type can't be reliably determined, not analyzing")
                                        results = None
                                    if results is not None:
                                        if results['data'] is not None:
                                            log.info(
                                                f"current status of uploaded file: '{results['data']['status']}' "
                                                f"(uuid: {results['data']['uuid']})"
                                            )
                                            settings.uuid_cache(results['data']['uuid'])
                                        else:
                                            log.warn(
                                                "it appears you have exceeded your monthly limit, to upgrade your plan "
                                                f"please see our available plans here: "
                                                f"{settings.INSTRUCTION_LINKS['available_plans']}. If these plans do "
                                                f"not fit your particular needs, please create a support ticket at: "
                                                f"{settings.INSTRUCTION_LINKS['submit_ticket']} and "
                                                "explain your needs to us so we can further assist you."
                                            )
                        elif any(x in choice for x in ["status", "check", "uuid", "uu", "sea", "search"]):
                            try:
                                uuid = choice.split(" ")[-1].strip()
                                searched = settings.uuid_cache(uuid, search_all=True)
                                if searched:
                                    results = api.status_check(uuid)
                                    threat_score = results["threat_score"]
                                    if "status" not in results.keys():
                                        log.info("file is done being processed, overview:")
                                        settings.view_basic_threat_summary({"threat_score": threat_score['results']})
                                        settings.uuid_cache(uuid, delete_uuid=True)
                                    else:
                                        log.warn("UUID is not done being processed yet, try again later")
                                else:
                                    log.error("UUID does not exist in cached UUID's use `cache` to see cached UUID's")
                            except IndexError:
                                log.warn(
                                    "did you forget to add your UUID? Find it using `cache` and use it with "
                                    "`status UUID`"
                                )
                            except KeyError:
                                log.info("it appears the file is not done being analyzed, please wait and try again")
                        elif choice in ("hashes", "hashsum", "hash"):
                            if filename is not None:
                                log.info("gathering hashes for current working file")
                                try:
                                    results = api.hashsum(filename)
                                    for key in results['data']['hashes']:
                                        print(f"{str(key).upper()}: {results['data']['hashes'][key]}")
                                except Exception as e:
                                    log.error(f"got error while gathering hashes: {str(e)}")
                            else:
                                log.warn("there is not current working file to generate hashsums with")
                        elif choice in ("cache", "show", "ca", "sho"):
                            settings.uuid_cache(None, show_all=True)
                        elif any(x in choice for x in ["newfile", "new"]):
                            try:
                                choice_data = choice.split(" ")
                                if len(choice_data) > 2:
                                    try:
                                        file_delim = int(choice_data[1])
                                    except Exception as e:
                                        log.warn(
                                            f"hit error: {str(e)} while trying to add to file, defaulting to filename1"
                                        )
                                        file_delim = 1
                                else:
                                    file_delim = 1
                                if file_delim == 2 and filename is None:
                                    log.warn(
                                        "cannot set filename2 until filename1 has been set, defaulting to filename1"
                                    )
                                    file_delim = 1
                                passed_filename = choice_data[-1]
                                if file_delim == 1:
                                    filename = passed_filename
                                else:
                                    secondary_filename = passed_filename
                            except IndexError:
                                log.warn("you didn't pass  file to reload")
                            if not os.path.exists(filename):
                                log.warn("provided filename does not exist, or you did not pass a file")
                                filename = None
                        elif choice in ("showfile",):
                            log.info(f"current working files: filename1=@{filename} filename2=@{secondary_filename}")
                        elif choice in ("quit", "exit", "ex", "qu"):
                            self.do_exit()
                except KeyboardInterrupt:
                    print("^C")
                    log.warn("use the `exit` command to exit the terminal")
        except Exception:
            pass
