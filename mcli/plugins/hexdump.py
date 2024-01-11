import json
import shutil
import tempfile

import requests

import mcli.__version__ as version
import mcli.lib.settings as settings
import mcli.lib.logger as logger


__help__ = """
Processes the hexdump of a file using the Malcore API and downloads the data locally

Available Arguments:
    filename    -> filename to perform hexdump on           *default=None **REQUIRED
    out_file    -> filename to store data to if you want    *default=None
    show_help   -> show this help and exit                  *default=False
"""


def plugin(*args, **kwargs):
    filename = kwargs.get("filename", None)
    out_file = kwargs.get("out_file", None)
    show_help = kwargs.get("show_help", False)

    if show_help:
        print(__help__)
    else:
        if filename is None:
            logger.warn("you did not provide a filename to perform analysis on")
        else:
            logger.info("starting hexdump process")
            conf = settings.get_conf()
            api_key = conf['api_key']
            url = 'https://api.malcore.io/api/hexdump'
            headers = {
                "apiKey": api_key,
                'X-No-Poll': 'True',
                'User-Agent': settings.build_agent(),
                'Source': f'mCLI v{version.VERSION}'
            }
            output_filename = tempfile.NamedTemporaryFile(prefix='hexdump_', suffix='.json', delete=False)
            file_data = {'filename1': open(filename, "rb")}
            logger.info("making request to Malcore API")
            try:
                with requests.post(url, headers=headers, files=file_data, stream=True) as stream:
                    with open(output_filename.name, 'wb') as fh:
                        shutil.copyfileobj(stream.raw, fh)
                logger.info("data downloaded successfully")
                json_data = json.load(output_filename)
                if json_data != '' or json_data != b'':
                    output_filename.truncate(0)
                    output_filename.close()
                    if out_file is None:
                        settings.display_by_size(json_data['data']['results'])
                        logger.info("end of data processing")
                    else:
                        logger.info(f"saving all data to outfile: {out_file}")
                        with open(output_filename, "a+") as fh:
                            fh.write(json_data['data']['results'])
                        logger.info("all data successfully saved to outfile")
            except Exception as e:
                logger.error(f"unable to process hexdump due to an error: {str(e)}")