import os
import json
import random

import mcli.lib.logger as log
import mcli.lib.settings as settings
import mcli.api.mapi as mcli_api
import mcli.common.check_file_type as file_type_check


class McliTerminal(object):

    terminal_commands = (
        "search", "analyze", "hashsum",
        "status", "quit", "help", "?", "he",
        "analysis", "check", "uuid",
        "hashes", "hash", "exit",
        "cache", "newfile",
        "showfile", "info", "information",
        "anal", "external", "ca", "sho",
        "exi", "qui", "ext", "sea", "new",
        "uu", "re", "reuse", "groupby",
        "ex", "exif", "apikey", "api",
        "del", "delete", "vi", "view",
        "sw", "swap", "fileswap", "ping",
        "ver", "version", "ch", "gro", "pi",
        "pcap", "pc", "hi", "history"
    )
    loaded_external_commands = []

    def __init__(self, external_commands):
        self.terminal_start = f"\033[92mroot\033[0m@\033[91mmcli\033[0m:~/.malcore# "
        self.quit_terminal = False
        self.external_commands = external_commands
        self.history = []

    def load_external(self):
        self.loaded_external_commands = self.external_commands

    def reflect_memory(self):
        if os.path.exists(settings.HISTORY_FILE):
            with open(settings.HISTORY_FILE) as fh:
                for item in fh.readlines():
                    item = item.strip()
                    self.history.append(item)

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
        """
        help function
        """
        print("""
Available Commands:             Description:
------------------              ------------""")
        usage_menu = """
he[lp]                          Print this help
?                          

sea[rch] UUID                   Provide a UUID to check the status of your upload
ch[eck]  UUID
uu[id]   UUID

anal[ysis|yze]                  Start full analysis on the current working file
hash[sum|es]                    Gather hashsums of the current working file
ca[che]                         Show the current stored UUID's
show  

new[file] [*1|2] [FILE]         Pass to change the current working files
sho[wfile]                      Pass to show the current working files
ext[ernal]                      View integrated external commands
re[use]                         Pass to perform code reuse analysis on two files
gro[upby] [*5|10|15]            Pass to change the 'group_by' integer for code reuse analysis
ex[if]                          Gather exif data from the current working file
api[key]                        View your current saved API key
exi[t]                          Pass this to exit the terminal
qui[t] 

del[ete] UUID                   Manually remove a UUID from the cache list
vi[ew]                          List your available endpoints with your plan and your scans per month
sw[ap]                          Swap working files, filename1 -> filename2; filename2 -> filename1
pi[ng]                          Ping the Malcore API to see if it's online
ver[sion]                       Show current program version

hi]story]                       View mCLI command history"""
        settings.colorize_short_hands(usage_menu)

    def do_exit(self, api):
        """
        exit the terminal
        """
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
        for command in self.history:
            settings.history(command)
        api.send_statistics(is_shutdown=True)
        saying = random.SystemRandom().choice(exit_sayings)
        print(f"[::][{time.strftime('%H:%M:%S')}] {saying}")
        self.quit_terminal = True

    def perform_external_command(self, command):
        """
        perform an externally loaded command
        """
        import subprocess

        self.add_to_history(command)
        subprocess.call(command, shell=True)

    def reflect_history(self):
        if os.path.exists(settings.HISTORY_FILE):
            with open(settings.HISTORY_FILE) as fh:
                for item in fh.readlines():
                    if item != '':
                        self.history.append(item.strip())

    def add_to_history(self, command):

        self.history.append(command)

    def terminal_main(self):
        """
        main terminal function
        """
        self.reflect_history()
        conf_file = settings.CONFIG_FILE
        passed_config = settings.CURRENT_RUN_CONFIG
        api = mcli_api.ExtendedMalcoreApi(json.load(open(conf_file))["api_key"])
        api.send_statistics(is_start=True)
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
                settings.complete(self.terminal_commands)
                try:
                    choice_type, choice = self.get_choice()
                    if choice_type == "unknown":
                        log.warn(f"unknown choice: '{choice}' passed, for help type `help`")
                    elif choice_type == "external":
                        self.perform_external_command(choice)
                    elif choice in ("ver", "version"):
                        self.add_to_history(choice)
                        settings.version_display()
                    elif choice in ("pc", "pcap"):
                        self.add_to_history(choice)
                        if filename is None:
                            log.warn("must at least have filename1 filled to analyze PCAP")
                        else:
                            log.info("launching PCAP analysis")
                            if secondary_filename is not None:
                                do_diff = log.prompt("are you wanting to perform a PCAP diff? [y/n]")
                                if do_diff == "y":
                                    do_pcap_diff = True
                                else:
                                    do_pcap_diff = False
                            else:
                                do_pcap_diff = False
                            if do_pcap_diff:
                                log.debug("will be performing PCAP diff")
                                filename1_good = file_type_check.is_pcap(filename)
                                filename2_good = file_type_check.is_pcap(secondary_filename)
                                if filename1_good and filename2_good:
                                    res = api.pcap_diff(filename, secondary_filename)
                                    settings.display_pcap(res, diff=True)
                                else:
                                    log.warn("one or more of your files are not a PCAP file, check and try again")
                            else:
                                log.debug("will be performing single PCAP file analysis")
                                filename1_good = file_type_check.is_pcap(filename)
                                if filename1_good:
                                    res = api.pcap_analysis(filename)
                                    print(res)
                                else:
                                    log.warn("filename1 is not a PCAP file, check and try again")
                    elif choice in ("ping", "pi"):
                        self.add_to_history(choice)
                        log.info("checking if API is online")
                        settings.check_api(speak=True, ping_test=True)
                    elif choice in ("sw", "fileswap", "swap"):
                        self.add_to_history(choice)
                        if filename is not None:
                            filename, secondary_filename = secondary_filename, filename
                            log.info(f"filename1=@{filename}; filename2=@{secondary_filename}")
                        else:
                            log.warn("no working files are currently loaded, load with `newfile PATH`")
                    elif choice in ("vi", "view"):
                        self.add_to_history(choice)
                        conf = settings.get_conf()
                        print("Endpoint name,Monthly limit\n---------------------------")
                        for endpoint in conf['available_endpoints']:
                            print(f"{endpoint['endpoint_name']},{endpoint['monthly_limit']}")
                    elif any(c in choice for c in ("del", "delete")):
                        self.add_to_history(choice)
                        uuid_to_remove = choice.split(" ")
                        if uuid_to_remove == "" or len(uuid_to_remove) == 1:
                            log.warn("no UUID passed, you must pass a UUID to remove one manually")
                        else:
                            uuid = uuid_to_remove[-1]
                            settings.uuid_cache(uuid, delete_uuid=True)
                    elif choice in ("ex", "exif"):
                        self.add_to_history(choice)
                        log.info(f"gathering exif data out of current working file (filename1=@{filename})")
                        results = api.parse_exif_data(filename)['data']
                        settings.view_exif_data(results)
                    elif choice in ("apikey", "api"):
                        self.add_to_history(choice)
                        file_ = settings.CONFIG_FILE
                        data = json.load(open(file_))["api_key"]
                        log.info(f"current loaded API key: {data}")
                        log.warn(
                            "you cannot change your API key from the terminal view. To reset your API key restart mCLI "
                            "with the `--reload` flag."
                        )
                    else:
                        if choice in ("?", "help", "he"):
                            self.add_to_history(choice)
                            self.help_menu()
                        elif any(c in choice for c in ["groupby", "gro"]):
                            self.add_to_history(choice)
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
                            self.add_to_history(choice)
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
                            self.add_to_history(choice)
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
                            self.add_to_history(choice)
                            log.info(f"total of {len(self.loaded_external_commands)} external command(s) integrated")
                            question = log.prompt("print all external commands")
                            if question.lower() == "y":
                                print(",".join(self.loaded_external_commands))
                        elif choice in ("analyze", "analysis", "anal"):
                            self.add_to_history(choice)
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
                            self.add_to_history(choice)
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
                            self.add_to_history(choice)
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
                        elif choice in ("cache", "ca"):
                            self.add_to_history(choice)
                            settings.uuid_cache(None, show_all=True)
                        elif any(x in choice for x in ["newfile", "new"]):
                            self.add_to_history(choice)
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
                        elif choice in ("showfile", "sho"):
                            self.add_to_history(choice)
                            file_added_color = "\033[92m"
                            file_not_added_color = "\033[91m"
                            end_color = "\033[0m"
                            log_str = "current working files: "
                            if filename is not None:
                                log_str += f"{file_added_color}filename1{end_color}=@{filename}"
                            else:
                                log_str += f"{file_not_added_color}filename1{end_color}=@NUL"
                            if secondary_filename is not None:
                                log_str += f" {file_added_color}filename2{end_color}=@{secondary_filename}"
                            else:
                                log_str += f" {file_not_added_color}filename2{end_color}=@NUL"
                            log.debug(log_str)
                        elif choice in ("quit", "exit", "exi", "qui"):
                            self.add_to_history(choice)
                            self.do_exit(api)
                        elif choice in ("hi", "history"):
                            for item in self.history:
                                print(item)
                except KeyboardInterrupt:
                    print("^C")
                    log.warn("use the `exit` command to exit the terminal")
        except Exception:
            pass
