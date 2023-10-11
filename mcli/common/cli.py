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
        with open(filename, writer) as fh:
            json.dump(opts.__dict__, fh)

    @staticmethod
    def optparse():
        parser = argparse.ArgumentParser()
        parser.add_argument("--wizard", action="store_true", dest="runWizard", default=False)
        parser.add_argument("-f1", "--filename1", default=None, dest="workingFile1")
        parser.add_argument("-q", "--quick-analysis", action="store_true", default=False, dest="quickAnalysis")
        parser.add_argument("--external-path", default="/usr/bin,/usr/local/bin,/bin", dest="importExternal")
        parser.add_argument("-f2", "--filename2", default=None, dest="workingFile2")
        parser.add_argument("--group-by", default=5, type=int, dest="groupByIntReuse", choices=[5, 10, 15])
        parser.add_argument("--reload", default=False, action="store_true", dest="reloadApiKey")
        parser.add_argument("--skip", default=False, action="store_true", dest="skip")
        return parser.parse_args()

