import datetime
import json

import requests

import mcli.lib.settings
import mcli.__version__
from msdk.api import MalcoreApiSdk
from msdk.lib.settings import post_files
from mcli.lib.logger import warn, error, info, fatal


class ExtendedMalcoreApi(MalcoreApiSdk):

    """
    adds new functions to the API that we can use
    """

    secondary_base_url = "https://api.malcore.io/auth"
    stats_url = "https://api.malcore.io/agent/stat"

    def __init__(self, api_key, **kwargs):
        super().__init__(api_key, **kwargs)
        self.headers["X-No-Poll"] = 'True'
        self.headers['User-Agent'] = mcli.lib.settings.build_agent()
        self.headers['Source'] = f'mCLI v{mcli.__version__.VERSION}'

    def register(self, email, password):
        """
        register the user on Malcore
        """
        url = f"{self.secondary_base_url}/register"
        data = {"email": email, "password": password}
        try:
            req = requests.post(url, json=data, headers=self.headers)
            results = req.json()
        except:
            results = None
        if results is None:
            return False
        if not results['success']:
            return False
        else:
            if 'userId' in results['data'].keys():
                return True
            else:
                return False

    def executable_file_analysis(self, filename1, **kwargs):
        """ patches the exec file analysis endpoint """
        no_poll = kwargs.get("no_poll", False)
        if no_poll:
            self.headers['X-No-Poll'] = "true"
        url = f"{self.base_url}/upload"
        try:
            req = requests.post(url, headers=self.headers, files={"filename1": open(filename1, "rb").read()})
            return req.json()['data']
        except:
            return None

    def status_check(self, uuid):
        """ patches the status check endpoint """
        url = f"{self.base_url}/status"
        data = f"uuid={uuid}"
        try:
            req = requests.post(url, headers=self.headers, data=data)
            return req.json()['data']
        except:
            return None

    def login(self, email, password):
        """
        log the user into Malcore
        """
        url = f"{self.secondary_base_url}/login"
        data = {"email": email, "password": password}
        info(f"attempting to login with username: {email} ...")
        req = requests.post(url, data=data)
        try:
            results = req.json()
            with open('test.json', 'w') as fh:
                import json
                json.dump(results, fh, indent=4)
            if results["isMaintenance"]:
                warn("Maintenance mode is currently activated, please try again later")
                return None, None, None
            else:
                if not results["success"]:
                    error(f"Unable to login successfully")
                    return None, None, None
                else:
                    if results["data"] is not None:
                        info(f"Logged in successfully")
                        api_key = results['data']['user']['apiKey']
                        is_verified_user = results['data']['user']['isVerified']
                        is_active_account = results['data']['user']['isActive']
                        if api_key is None or api_key == '':
                            fatal(
                                f"Your API key has not been generated, please login to the web GUI and generate "
                                f"your API key here: {mcli.lib.settings.INSTRUCTION_LINKS['login_to_gui']}. "
                                f"For instructions on how to do so, please see here: "
                                f"{mcli.lib.settings.INSTRUCTION_LINKS['api_key_generation']}"
                            )
                            return None, None, None
                        else:
                            if not is_verified_user:
                                fatal(
                                    "Your account is not verified, please check your email for a verification link. "
                                    "If you have no received a verification link please submit a support ticket here: "
                                    f"{mcli.lib.settings.INSTRUCTION_LINKS['submit_ticket']}"
                                )
                                return None, None, None
                            if not is_active_account:
                                fatal(
                                    "Your account is currently in an inactive status. This could be due to a few "
                                    "reasons. To figure out the issue please submit a support ticket at: "
                                    f"{mcli.lib.settings.INSTRUCTION_LINKS['submit_ticket']}"
                                )
                                return None, None, None
                            return api_key, results['data']['accessToken'], \
                                results['data']['user']['subscription']['plan']
        except Exception as e:
            error(f"Caught error: {e} unable to login")
            return None

    def get_endpoint_list(self, access_token, plan_id):
        """
        get a list of all current available endpoints for the users plan as well as their monthly scan limit
        """
        results = []
        url = f"https://api.malcore.io/plan/{plan_id}"
        del self.headers['apiKey']
        self.headers['Bearer'] = access_token
        try:
            req = requests.get(url, headers=self.headers)
            data = req.json()
        except:
            data = {"data": {"endpoints": []}}
        for endpoint in data['data']['endpoints']:
            try:
                results.append({
                    "endpoint_name": endpoint['endpoint']['name'],
                    "monthly_limit": 999999999 if endpoint['isUnlimited'] else endpoint['limit']
                })
            except:
                pass
        return results

    def send_statistics(self, is_start=False, is_usage=False, is_shutdown=False, from_function=None):
        """
        send statistics of use to the Malcore servers. This can be turned off
        # TODO:/
        """
        conf = mcli.lib.settings.get_conf()
        current_date = datetime.datetime.today()
        if "stats" in conf.keys():
            do_stats = conf["stats"]
        else:
            do_stats = False
        if do_stats:
            try:
                del self.headers['X-No-Poll']
            except:
                pass
            if is_start:
                payload = {
                    "type": "started", "payload": {"message": f"mCLI started at: {current_date}"}
                }
            elif is_usage:
                if from_function is not None:
                    function_name = from_function
                else:
                    function_name = "unknown"
                payload = {
                    "type": "usage", "payload": {"message": f"usage from function: {function_name} on {current_date}"}
                }
            elif is_shutdown:
                payload = {
                    "type": "shutdown", "payload": {"message": f"mCLI shutdown at: {current_date}"}
                }
            else:
                payload = {
                    "type": "interaction", "payload": {"message": f"unknown interaction with mCLI at {current_date}"}
                }
            self.headers['agentVersion'] = mcli.__version__.VERSION
            try:
                requests.post(self.stats_url, json=payload, headers=self.headers, timeout=3)
            except:
                pass

    def code_reuse(self, filename1, filename2):
        """
        code reuse analysis
        """
        url = f"{self.base_url}/reuse"
        return post_files(url, filename1=filename1, filename2=filename2, headers=self.headers)
