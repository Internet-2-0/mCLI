import os
import platform
import random
import re
import json
import readline
import shutil
import sys
import hashlib
import binascii

import tabulate

import mcli.lib.logger as logger
import mcli.api.mapi as mapi


class MalcoreCompleter(object):

    def __init__(self, opts):
        self.opts = sorted(opts)
        self.possible_matches = []

    def complete_text(self, text, state):
        if state == 0:
            if text:
                self.possible_matches = [m for m in self.opts if m and m.startswith(text)]
            else:
                self.possible_matches = self.opts[:]
        try:
            return self.possible_matches[state]
        except IndexError:
            return None


# the $HOME path
HOME = f"{os.path.expanduser('~')}/.mcli"
# where the UUID cache is stored
CURRENT_UUIDS = f"{HOME}/uuids.json"
# config file
CONFIG_FILE = f"{HOME}/mcli.json"
# current running config
CURRENT_RUN_CONFIG = f"{HOME}/run.conf"
# useful links
INSTRUCTION_LINKS = {
    "api_key_generation": "https://link.malcore.io/cli/key",
    "login_to_gui": "https://link.malcore.io/cli/login",
    "submit_ticket": "https://link.malcore.io/cli/support",
    "register_link": "https://link.malcore.io/cli/register",
    "settings_page": "https://link.malcore.io/cli/settings",
    "available_plans": "https://link.malcore.io/cli/pricing"
}


def init(reload=False, skip_overview=False):
    """
    initialize the program
    """
    if not reload:
        running_os = check_operating_system()
        if running_os == 'android':
            logger.fatal('this program cannot be run on a phone')
            exit(1)
        else:
            if not skip_overview:
                if running_os == "windows":
                    res = logger.prompt(
                        "according to your operating system (which is Windows btw) you don't know what you're doing "
                        "would you like a basic overview of Malware analysis? [y/n]"
                    )
                    if res == "y":
                        making_fun_of_windows_sayings = (
                            "did you Google it ..?",
                            "LOL THIS GUY WANTED US TO TEACH HIM MALWARE ANALYSIS !!!!",
                            "sorry this isn't a school",
                            "lol imagine using Windows .."
                        )
                        logger.debug(random.SystemRandom().choice(making_fun_of_windows_sayings))
                    else:
                        logger.debug("enabling easy mode for the 'Windows guy'")
                else:
                    logger.info(f'running OS: {running_os}')
            elif running_os == "unknown":
                logger.warn("your OS couldn't be determined, we'll try to run but can't promise anything")
            else:
                logger.info(f'running OS: {running_os}')
        if not os.path.exists(HOME):
            is_onboarded = do_onboarding()
            if not is_onboarded:
                logger.fatal(
                    "the above reasons have provided you with what to do next to continue onboarding. "
                    "Please finish the above tasks and try again"
                )
                exit(1)
            else:
                logger.info("you have successfully been onboarded")
            with open(CONFIG_FILE) as fh:
                api_key = json.load(fh)["api_key"]
        else:
            logger.info("loading API key")
            try:
                with open(CONFIG_FILE) as fh:
                    api_key = json.load(fh)['api_key']
                logger.info("API key loaded successfully")
            except:
                logger.fatal("unable to load API key for one or more reasons, run again with the `--reload` flag")
                exit(1)
        return api_key
    else:
        logger.warn(
            "reload has been initialized, you will not be able to login while reloading, so you need your API key. "
            f"You can find your API key here: {INSTRUCTION_LINKS['settings_page']}"
        )
        if os.path.exists(CONFIG_FILE):
            opener = "w"
        else:
            opener = "a+"
        with open(CONFIG_FILE, opener) as fh:
            api_key = logger.prompt("enter your API key")
            json.dump({"api_key": api_key}, fh)
        return api_key


def do_onboarding():
    """
    onboards the user and gets them signed in or signed up
    """
    api = mapi.ExtendedMalcoreApi("")
    try:
        os.makedirs(HOME)
    except:
        pass
    with open(CONFIG_FILE, "a+") as fh:
        # ignore this ...
        # api_key = logger.prompt("enter your API key (enter 'NA' if you don't have one)")
        api_key = "NA"
        if api_key == 'NA':
            has_account = logger.prompt("do you have a Malcore account? [y/n]")
            if has_account.lower() == "y":
                email = logger.prompt("enter the email you used to sign up with")
                password = logger.prompt("enter your password", hide=True)
                is_logged_in, access_token, plan_id = api.login(email, password)
                if is_logged_in is not None:
                    results = {"api_key": is_logged_in}
                    available_endpoints = api.get_endpoint_list(access_token, plan_id)
                    stats = logger.prompt("do you want to send statistics to Malcore? [y/n]")
                    if stats == "y":
                        results['stats'] = True
                    else:
                        results['stats'] = False
                    results['available_endpoints'] = available_endpoints
                    json.dump(results, fh)
                    return True
                else:
                    return False
            else:
                do_register = logger.prompt("do you want to register from here? [y/n]")
                if do_register.lower() == "y":
                    email_regex = re.compile('[\w+\.]+@([\w+]+\.)+[\w+]{2,25}')
                    email_done = False
                    while not email_done:
                        username = logger.prompt("enter your email address")
                        if email_regex.search(username) is not None:
                            email_done = True
                        else:
                            logger.warn("invalid email has been presented")
                    password_done = False
                    password_regex = re.compile(
                        '(?=.*[0-9])(?=.*[!?@#,.;()\[\]<>+\-\/$%^&*])[a-zA-Z0-9!?@;#,\[\]<>.()+\-\/$%;^&*]{6,99}'
                    )
                    while not password_done:
                        password = logger.prompt("enter the password you want to use", hide=True)
                        if password_regex.search(password) is not None:
                            password_done = True
                        else:
                            logger.warn(
                                "invalid password presented. Password must contain: at least 6 characters, "
                                "one digit, and one special character"
                            )
                    registered = api.register(username, password)
                    if registered:
                        logger.info(
                            "registration was successful, please check your email for a verification link from "
                            "Malcore. Once you have verified your account restart mCLI to login"
                        )
                        try:
                            shutil.rmtree(HOME)
                        except:
                            logger.warn(
                                "we were unable to remove the current configuration, run `mcli --del-all` before "
                                "logging in"
                            )
                        exit(1)
                    else:
                        logger.error(
                            f"something happened and we weren't able to register you, please register at: "
                            f"{INSTRUCTION_LINKS['register_link']}"
                        )
                    exit(1)
                else:
                    logger.warn(
                        f"you will need to signup at the web GUI here: {INSTRUCTION_LINKS['register_link']}", is_bad=True
                    )
            return False
        else:
            to_write = {"api_key": api_key.strip()}
            available_endpoints = []
            stats = logger.prompt("do you want to send anonymized statistics to Malcore? [y/n]")
            if stats == "y":
                to_write["stats"] = True
            else:
                to_write["stats"] = False
            to_write['available_endpoints'] = available_endpoints
            json.dump(to_write, fh)
            return True


def check_operating_system():
    """
    gathers the current OS this is being run on
    """
    _sys_platform = sys.platform
    env = os.environ
    for key in env.keys():
        if "ANDROID_ARGUMENT" in key:
            return "android"
        elif 'P4A_BOOTSTRAP' in key:
            return 'android'
        if _sys_platform in ('win32', 'cygwin'):
            return 'windows'
        if _sys_platform == 'darwin':
            return 'macos'
        if _sys_platform.startswith('linux'):
            return 'linux'
        elif _sys_platform.startswith('freebsd'):
            return 'freebsd'
        return 'unknown'


def uuid_cache(uuid, delete_uuid=False, show_all=False, search_all=False, count_all=False):
    """
    cache the uuid into a file so it can be used later
    """
    if not os.path.exists(CURRENT_UUIDS):
        data = {"uuids": []}
        open(CURRENT_UUIDS, "a+").close()
    else:
        try:
            data = json.load(open(CURRENT_UUIDS))
        except:
            data = {"uuids": []}
    if count_all:
        max_uuids = 10
        current_total = len(data["uuids"])
        if current_total >= max_uuids:
            logger.warn(
                "maximum amount of UUID's has been reached, check analysis of current UUID's before adding more"
            )
            return True
        return False
    if delete_uuid:
        try:
            data["uuids"].remove(uuid)
            logger.info(f"UUID: {uuid} removed successfully")
        except:
            logger.warn(f"unable to remove UUID: {uuid}", is_bad=True)
        with open(CURRENT_UUIDS, 'w') as fh:
            json.dump(data, fh)
        return
    if show_all:
        if len(data["uuids"]) != 0:
            logger.info(f"total of {len(data['uuids'])} UUID(s) found")
            for uuid in data["uuids"]:
                print(f"\t- {uuid}")
        else:
            logger.warn("no UUIDs cached")
        return
    if search_all:
        if uuid in data["uuids"]:
            return True
        return False
    with open(CURRENT_UUIDS, 'w') as fh:
        if uuid not in data["uuids"]:
            data["uuids"].append(uuid)
        json.dump(data, fh)


def file_type_pointer(filename):
    """
    pointer function for file type analysis
    """
    import mcli.common.check_file_type as ft

    is_pe = ft.is_pe(filename)
    is_elf = ft.is_elf(filename)
    is_doc = ft.is_ms_doc(filename)
    return is_pe, is_elf, is_doc


def convert_size(byte_size):
    """
    converts bytes to readable size
    """
    import math

    if byte_size == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(byte_size, 1024)))
    p = math.pow(1024, i)
    s = round(byte_size / p, 2)
    return "{}{}".format(s, size_names[i])


def build_agent():
    """
    builds the User-Agent for the app based on user system info
    :return:
    """
    import mcli.__version__ as ver
    _platform = platform.uname()
    return f"mCLI/{ver.VERSION} ({_platform.system};{_platform.version})"


def get_file_basic_info(filename):
    """
    provides basic file information
    """
    basename = os.path.basename(filename)
    path = os.path.dirname(filename)
    file_size = convert_size(os.path.getsize(filename))
    h = hashlib.sha256()
    h.update(open(filename, "rb").read())
    sha256 = h.hexdigest()
    with open(filename, "rb") as fh:
        first_10_bytes = fh.read(10)
        hexdump_first_10 = binascii.hexlify(first_10_bytes).decode()
    return {"sha256": sha256, "hexdump": hexdump_first_10, "path": path, "basename": basename, "size": file_size}


def integrate_external_commands(external_path):
    """
    integrate external commands for us to use in the terminal
    """
    commands = []
    if external_path is None:
        return []
    else:
        external_locations = external_path.split(",")
        for path in external_locations:
            if os.path.exists(path):
                commands.extend(os.listdir(path))
            else:
                logger.warn(f"path: '{path}' does not exist will not import")
    return commands


def compare_assembly_code(asm1, asm2, match_percent=None):
    """
    compare the assembly side by side
    """
    parts1 = asm1.split("\n")
    parts2 = asm2.split("\n")
    rows = []
    for i, item in enumerate(parts1, start=1):
        rows.append([f"#{i}", item, parts2[i-1]])
    print("\n")
    print(tabulate.tabulate(rows, tablefmt='outline', headers=['LINE', 'FILENAME1', 'FILENAME2']))
    if match_percent is not None:
        print(f"{match_percent} out of 0")
    print("\n")


def view_basic_threat_summary(summary):
    """
    basic threat summary
    """
    signatures = [item['info']['title'] for item in summary['threat_score']['signatures']]
    print("\nDiscovered signatures:")
    for sig in signatures:
        print(f"\t - {sig}")
    try:
        score = float(summary['threat_score']['score'].split("/")[0])
    except:
        score = 0.0
    rounded_score = round(score)
    if rounded_score < 20:
        score = f"\033[92m{score}\033[0m"
    elif rounded_score >= 20 and rounded_score < 40:
        score = f"\033[33m{score}\033[0m"
    elif rounded_score >= 40 and rounded_score < 60:
        score = f"\033[93m{score}\033[0m"
    else:
        score = f"\033[91m{score}\033[0m"
    print(f"\nCalculated score: {score}/100\n")


def view_exif_data(exif_results):
    """
    view the exif data of a file
    """
    misc_data = [
        [key, exif_results['misc_information'][key]] for key in exif_results['misc_information'].keys()
    ]

    print(f"""
File header information:
    Hexdump: {exif_results['file_information']['header_information']['file_header_hexdump']}
    ASCII:   {exif_results['file_information']['header_information']['file_header_ascii']}

File Code Signature: {exif_results['code_signature']}
""")
    for item in misc_data:
        print(f"{item[0].replace('_', ' ')}: {item[1]}")
    print()


def get_conf():
    """
    quick function to grab current config
    """
    with open(CONFIG_FILE) as fh:
        return json.load(fh)


def percent(part, whole):
    """
    gets the percentage of a number
    """
    try:
        return 100 * float(part) / float(whole)
    except ZeroDivisionError:
        return 0


def check_api(speak=False, check_amount=5, ping_test=False):
    """
    checks if the API is up or not using a variety of methods
    """
    import requests, time

    searcher = re.compile("\<pre\>Cannot.GET.\/api\/\<\/pre\>")
    url = "https://api.malcore.io/api/"
    if ping_test:
        responded = []
        failed = []
        for _ in range(check_amount):
            try:
                start_time = time.time()
                req = requests.get(url, timeout=2)
                end_time = time.time()
                if req.status_code == 404:
                    if searcher.search(req.text) is not None:
                        responded.append(end_time - start_time)
                else:
                    failed.append(None)
            except:
                failed.append(None)
        try:
            average_response_time = sum(responded) / len(responded)
        except ZeroDivisionError:
            average_response_time = 'N/A'
        total_successes = percent(len(responded), check_amount)
        total_failures = percent(len(failed), check_amount)
        if speak:
            logger.info(
                f"API success rate: {total_successes}% ({len(responded)}/{check_amount}), "
                f"API failure rate: {total_failures}% ({len(failed)}/{check_amount}) "
                f"average response time: {average_response_time} seconds"
            )
    else:
        try:
            req = requests.get(url, timeout=3)
            if req.status_code == 404:
                if searcher.search(req.text) is not None:
                    return True
        except:
            return False


def version_display():
    """
    display the current program version
    """
    import mcli.__version__ as ver

    print(ver.VERSION)


def check_for_updates():
    """
    check for updates
    """
    import requests
    import mcli.__version__ as ver

    logger.debug("checking for updates")
    url = "https://raw.githubusercontent.com/Internet-2-0/mCLI/master/mcli/__version__.py"
    try:
        req = requests.get(url)
    except Exception as e:
        import traceback
        traceback.print_exc()
        req = None
    if req is not None:
        searcher = re.compile("\d+\.\d+\.\d+\.\d+")
        results = searcher.findall(req.text)
        if len(results) != 0:
            version = results[0]
            if version != ver.VERSION_NUM:
                logger.warn(
                    "there is a new version available, please download the newest version, "
                    "automated issue creation will not work anymore"
                )
                logger.prompt("press enter to continue ...", semi_colon=False)
        else:
            logger.warn("there was no version found to check against")
    else:
        logger.warn("unable to check for updates")


def colorize_short_hands(usage_menu):
    new_menu = []
    for line in usage_menu.split("\n"):
        end = line.find("[")
        start = 0
        if end == -1:
            new_menu.append(line)
        else:
            new_menu.append(f"\033[97m{line[start:end]}\033[0m" + line[end:])
    print("\n".join(new_menu))
    print()


def complete(keywords):
    self_completer = MalcoreCompleter(keywords)
    readline.set_completer(self_completer.complete_text)
    readline.parse_and_bind('tab: complete')
