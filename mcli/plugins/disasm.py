import os
import re
import subprocess

import capstone

import mcli.lib.settings as settings
import mcli.lib.logger as logger


def plugin(*args, **kwargs):
    filename = kwargs.get("filename", None)
    arch = kwargs.get("arch", None)
    offset = kwargs.get("offset", 0x0)
    out_file = kwargs.get("out_file", None)

    if filename is None:
        logger.warn("is there a current working file opened?")
    else:
        if out_file is not None:
            logger.info(f"will write to outfile: {out_file} instead of displaying results")
            try:
                out_file = open(out_file, "a+")
            except Exception as e:
                logger.error(f"unable to process requested outfile got error: {str(e)}, defaulting to display")
                out_file = None
        conf = settings.get_conf()
        if 'disasm_info' not in conf.keys():
            logger.warn('you have no attempted to install r2 using the `install_r2` plugin, will default to capstone')
            use_capstone = True
        else:
            use_capstone = conf['disasm_info']['use_capstone']
        if use_capstone:
            logger.info("starting disassembly with capstone")
            if arch is None:
                logger.warn("no arch supplied, defaulting to 64")
                arch = capstone.CS_MODE_64
            elif arch == 32:
                arch = capstone.CS_MODE_32
            elif arch == 16:
                arch = capstone.CS_MODE_16
            else:
                logger.warn("unknown arch supplied, defaulting to 64")
                arch = capstone.CS_MODE_64
            total_ins = 0
            cs = capstone.Cs(capstone.CS_ARCH_X86, arch)
            # capstone documentation is shit
            cs.detail = True
            logger.info(f"starting at offset: {hex(offset)}")
            file_data = open(filename, 'rb')
            try:
                for line in file_data.readlines():
                    for i in cs.disasm(line, offset):
                        disasm = "0x%x:\t%s\t%s" % (i.address, i.mnemonic, i.op_str)
                        if out_file is None:
                            if total_ins != 0 and total_ins % 10 == 0:
                                input("\nPress enter to continue ...\n\n")
                            print(disasm)
                            total_ins += 1
                        else:
                            out_file.write(f"{disasm}{os.linesep}")

            except KeyboardInterrupt:
                logger.warn("user quit disassembly")
            except Exception as e:
                logger.error(f"unknown error occurred: {str(e)}")
        else:
            logger.info(f"using r2 to disassembly file: {filename}")
            stripper = re.compile('\x1B\[[0-?]*[ -/]*[@-~]')
            command = f'r2 -A -f -c "pi" -qq {filename}'
            logger.info(f"running command: {command}")
            r2_output = subprocess.check_output(command, shell=True)
            logger.info("command ran stripping ANSI and displaying")
            asm = stripper.sub('', r2_output.decode())
            display = asm.split("\n")
            try:
                for i, instructions in enumerate(display):
                    if out_file is None:
                        if i != 0 and i % 10 == 0:
                            input("\nPress enter to continue ...\n\n")
                        print(instructions)
                    else:
                        out_file.write(f"{instructions}{os.linesep}")
            except KeyboardInterrupt:
                logger.warn("use quit disassembly")
            except Exception as e:
                logger.error(f"unknown error while displaying disassembly: {str(e)}")
    if out_file is not None:
        logger.info(f"all disassembly instructions were dumped to file: {out_file.name}")

