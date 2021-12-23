import os
import requests
import sys
import time
supervisor_api = "http://supervisor/%s/%s"


def supervisor(param: str):
    while True:
        try:
            print("connecting to supervisor...")    
            supervisor_auth = {
                "Authorization": "Bearer %s" % os.environ['SUPERVISOR_TOKEN']
            }

            result = requests.get(supervisor_api % (
                "services", param), headers=supervisor_auth)
            result_json = result.json()
            return result_json["data"] if "data" in result_json else None

        except Exception as e:
            print("Could not connect to supervisor. Retry in 5 secs. %s" % e, file=sys.stderr)
            time.sleep(5)
