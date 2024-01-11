import getpass
import time


def debug(s):
    print(f"[\033[96md\033[0m][{time.strftime('%H:%M:%S')}] {s}")


def info(s):
    print(f"[\033[92mi\033[0m][{time.strftime('%H:%M:%S')}] {s}")


def warn(s, is_bad=False):
    if not is_bad:
        print(f"[\033[33mw\033[0m][{time.strftime('%H:%M:%S')}] {s}")
    else:
        print(f"[\033[93mW\033[0m][{time.strftime('%H:%M:%S')}] {s}")


def error(s):
    print(f"[\033[31mE\033[0m][{time.strftime('%H:%M:%S')}] {s}")


def fatal(s):
    print(f"[\033[91m!\033[0m][{time.strftime('%H:%M:%S')}] {s}")


def prompt(s, hide=False, strip=True, semi_colon=True):
    if not hide:
        req = input(f"[?][{time.strftime('%H:%M:%S')}] {s}{':' if semi_colon else ''} ")
    else:
        req = getpass.getpass(f"[?][{time.strftime('%H:%M:%S')}] {s}: ")
    if strip:
        answer = req.strip()
    else:
        answer = req
    return answer


