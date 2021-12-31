import os
import requests
import sys
import time
import logging
_LOGGER = logging.getLogger(__name__)

supervisor_api = "http://supervisor/%s/%s"


def supervisor(param: str):
    while True:
        try:
            _LOGGER.debug("Connecting to supervisor...")    
            supervisor_auth = {
                "Authorization": "Bearer %s" % os.environ['SUPERVISOR_TOKEN']
            }

            result = requests.get(supervisor_api % (
                "services", param), headers=supervisor_auth)
            result_json = result.json()
            return result_json["data"] if "data" in result_json else None

        except Exception as e:
            _LOGGER.error("Could not connect to supervisor: %s. Retry in 5 secs." % e)
            time.sleep(5)
