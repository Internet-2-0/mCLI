import json
import os
import shutil
import zipfile
import platform
import subprocess
import tempfile

import requests

import mcli.lib.settings as settings
import mcli.lib.logger as logger


__help__ = """
This plugin is designed to install radare2 on the users system. It does not require any arguments.

Available Arguments:
    show_help   -> show this help menu and exit
"""


def plugin(*args, **kwargs):
    show_help = kwargs.get("show_help", False)

    if show_help:
        print(__help__)
        return

    conf = settings.get_conf()
    if 'disasm_info' in conf.keys():
        if conf['disasm_info']['is_r2_installed']:
            logger.warn("r2 is already installed, uninstall it first")
            return
        elif conf['disasm_info']['did_install_fail']:
            logger.warn('it appears we already tried to install r2 and it failed, will not try again')
    else:
        data = {
            'r2_install_path': None, 'is_r2_installed': None,
            'did_install_fail': None, 'use_capstone': None,
            'use_r2': None
        }
        current_platform = platform.platform()
        if "Win" in current_platform:
            logger.warn("will not attempt to install r2 on Windows, defaulting to capstone disassembly")
            data['did_install_fail'] = True
            data['use_r2'] = False
            data['use_capstone'] = True
            data['is_r2_installed'] = False
        else:
            install_found = False
            install_path = None
            search_path = ("/usr/bin/r2", "/usr/local/bin/r2", "/bin/r2")
            for path in search_path:
                if os.path.exists(path):
                    logger.info('found r2 installation saving information')
                    install_path = path
                    install_found = True
                    break
            if not install_found:
                zip_file_location = 'https://github.com/radareorg/radare2/archive/refs/heads/master.zip'
                zip_file_download_name = tempfile.NamedTemporaryFile(
                    prefix="r2-install__", suffix=".zip", delete=False
                ).name
                unzip_path = tempfile.TemporaryDirectory().name
                try:
                    with requests.Session() as session:
                        with session.get(zip_file_location, stream=True) as req:
                            with open(zip_file_download_name, 'wb') as fh:
                                shutil.copyfileobj(req.raw, fh)
                    with zipfile.ZipFile(zip_file_download_name) as zh:
                        zh.extractall(unzip_path)
                    os.chdir(f"{unzip_path}/radare2-master")
                    command = "bash sys/install.sh"
                    try:
                        subprocess.call(command, shell=True)
                    except Exception as e:
                        logger.error(f'unable to successfully install radare2 defaulting to capstone: {str(e)}')
                        data['did_install_fail'] = True
                        data['is_r2_installed'] = False
                        data['use_capstone'] = True
                        data['use_r2'] = False
                except Exception as e:
                    logger.error(
                        f"an unexpected error occurred and we could not install r2, deafulting to capstone ({str(e)})"
                    )
                    data['did_install_fail'] = True
                    data['is_r2_installed'] = False
                    data['use_capstone'] = True
                    data['use_r2'] = False
            else:
                data['did_install_fail'] = False
                data['is_r2_installed'] = True
                data['r2_install_path'] = install_path
                data['use_capstone'] = False
                data['use_r2'] = True
        current_conf = conf
        current_conf['disasm_info'] = data
        with open(settings.CONFIG_FILE, 'w') as fh:
            json.dump(current_conf, fh)
        logger.info("new config written to configuration file")



