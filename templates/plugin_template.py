import mcli.lib.settings as settings
import mcli.lib.logger as logger


__help__ = """

"""


def plugin(*args, **kwargs):
    show_help = kwargs.get("show_help", False)

    if show_help:
        print(__help__)
        return

    # your code here
