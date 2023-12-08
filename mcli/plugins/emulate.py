import tabulate

import mcli.lib.settings as settings
import mcli.lib.logger as logger
import mcli.api.mapi as mapi


__help__ = """
Performs dynamic emulation on a provided binary file

Available Args:
    filename    -> the filename to perform emulation on     *default=None    **REQUIRED
    table_type  -> the type of table that will be displayed *default=simple  **REQUIRED
    outfile     -> the file to write the results to         *default=None
    show_help   -> show the help and exit                   *default=False
"""


def plugin(*args, **kwargs):
    filename = kwargs.get("filename", None)
    show_help = kwargs.get("show_help", False)
    table_type = kwargs.get("table_type", "simple")
    outfile = kwargs.get("outfile", None)

    if show_help:
        print(__help__)
    else:
        acceptable_table_formats = (
            "latex", "html", "textile", "youtrack", "moinmoin", "mediawiki", "rst", "jira", "orgtbl",
            "asciidoc", "pipe", "psql", "pretty", "presto", "outline", "grid", "github", "plain",
            "simple"
        )
        if table_type not in list(acceptable_table_formats):
            logger.error(
                f"the provided table format is not available please use one of the following: "
                f"{','.join(list(acceptable_table_formats))}"
            )
            return
        if filename is None:
            logger.error("you did not pass a file to emulate?")
        else:
            logger.info("starting dynamic emulation process")
            conf = settings.get_conf()
            api = mapi.ExtendedMalcoreApi(conf['api_key'])
            try:
                dynamic_results = api.dynamic_analysis(filename)
                logger.debug("dynamic emulation done, parsing data")
                parsed_output = []
                results = dynamic_results['data'][0]['dynamic_analysis'][0]
                ep_args = results['entry_points'][0]['ep_args']
                instruction_count = results['entry_points'][0]['instr_count']
                api_calls = results['entry_points'][0]['apis']
                # TODO:/
                # memory_access = results['entry_points'][0]['mem_access']
                errors = results['entry_points'][0]['error']
                in_memory_strings = results['strings']['in_memory']
                run_time = results['emulation_total_runtime']
                ran_os = results['os_run']
                start_address = results['entry_points'][0]['start_addr']
                emulation_breakdown = (
                    f"Entrypoint Arguments: {','.join(ep_args)}\n"
                    f"Instructions Count: {instruction_count}\n"
                    f"Total API calls: {len(api_calls)}\n"
                    f"Emulation OS: {ran_os}\n"
                    f"File Start Address: {start_address}\n"
                    f"Total Runtime: {run_time}\n\n"
                )
                for api in api_calls:
                    args = []
                    for arg in api['args']:
                        if len(arg) >= 14:
                            args.append(f"{list(arg)[0:7]} ...cont")
                        else:
                            args.append(arg)
                    parsed_output.append([api['pc'], f"{api['api_name']}", ','.join(args), api['ret_val']])
                ascii_strings = in_memory_strings['ansi']
                unicode_strings = in_memory_strings['unicode']
                mem_strings = []
                if len(ascii_strings) != 0 or len(unicode_strings) != 0:
                    mem_strings += unicode_strings
                    mem_strings += ascii_strings
                    logger.info(f"discovered a total of {len(mem_strings)} in memory string(s)")
                    settings.display_by_size(mem_strings)
                else:
                    logger.warn("no in memory strings discovered")
                if len(parsed_output) != 0:
                    headers = ("Offset", "API call", "Arguments", "Return Value")
                    table = tabulate.tabulate(parsed_output, headers=headers, tablefmt=table_type)
                    if outfile is None:
                        logger.info("no outfile requested dumping to display")

                        settings.display_by_size(table)
                        print(f"\n\n{emulation_breakdown}")
                    else:
                        with open(outfile, "a+") as fh:
                            fh.write(table)
                            fh.write(f"\n\n{emulation_breakdown}")
                        logger.info(f"all data dumped to file: {outfile}")
                else:
                    logger.warn("nothing was able to be parsed from the output, dumping errors")
                    if len(errors) == 0:
                        logger.error("there weren't any errors, can this file be emulated?")
                    else:
                        register = ""
                        for key in sorted(errors['regs'].keys()):
                            if len(key) == 2:
                                output_key = f"{key} "
                            else:
                                output_key = key
                            register += f"{output_key}: {errors['regs'][key]}\n"
                        print(f"\nRegisters at time of error:\n{register}")
                        del errors['regs']
                        error_instruction = errors['instr']
                        error_type, error_stack = errors['type'], errors['stack']
                        error_address, error_pc = errors['address'], errors['pc']
                        error_stack = '\n'.join(error_stack)
                        print(f"\nError information:\n"
                              f"------------------\n"
                              f"Instructions causing error: {error_instruction}\n"
                              f"Instruction location: {error_address}\n"
                              f"PC offset: {error_pc}\n"
                              f"Error type: {error_type}\n"
                              f"Error stack:\n---START STACK---\n{error_stack}\n---END STACK---")
            except Exception as e:
                logger.error(f"unable to perform emulation got error: {str(e)}")





