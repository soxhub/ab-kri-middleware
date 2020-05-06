# Proof of concept for a Key Risk Indicator (KRI) middleware component that
# reads a given configuration file, makes a fetch request via the configuration
# file, using some provided authentication secret, and then uses the response
# from this request to update a given KRI via the Auditboard API. The client/user
# provides a configuration file (in this case poc.yml) and this script merely uses
# that file to make its request, as well as update the associated KRI.
#
# Usage: python app/poc.py

import json
import logging
import argparse
import os
import time
from typing import Dict, Union

import requests
import yaml


handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class ServiceNotFoundError(RuntimeError):
    pass


class ConfigurationError(RuntimeError):
    pass


class Service:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        scheme: str,
        host: str,
        port: int,
        path: str,
        content_type: str,
        kri_id: int,
    ):
        self.name = name
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path
        self.content_type = content_type
        self.kri_id = kri_id

    @property
    def url(self) -> str:
        return self.scheme + "://" + self.host + ":" + str(self.port) + self.path

    def __str__(self) -> str:
        return json.dumps(self.__dict__)


if __name__ == "__main__":

    # read the user-supplied configuration file from the start command
    parser = argparse.ArgumentParser(
        description="An exploratory middleware service allowing external api interaction via KRIs"
    )
    parser.add_argument(
        "-f", "--file", help="configuration file used to make requests", required=True
    )
    parser.add_argument(
        "-s", "--service", help="name of service in configuration file to be run", required=True
    )
    args = vars(parser.parse_args())

    file: str = args.get("f", args.get("file"))
    service: str = args.get("s", args.get("service"))

    # parse the configuration file or exit if we can't
    config: Dict[str, Dict[str, Union[int, str]]] = {}
    with open(file, "r") as stream:
        try:
            logger.info("parsing configuration file at %s", file)
            config = yaml.safe_load(stream)["services"]
        except yaml.YAMLError as err:
            raise ConfigurationError("error reading configuration file: %s" % str(err))

    # create a service from a specific set of configuration parameters, with a
    # configuration file allowing for multiple services, with each service
    # attributed to a unique KRI, and given a unique set of configuration parameters
    if not service in config:
        raise ServiceNotFoundError("service %s not found in configuration" % service)

    srvc = Service(**config[service])  # type: ignore

    while True:

        # make an initial request to some third party endpoint in order to obtain
        # some value, using client/user supplied authentication
        response = requests.get(
            srvc.url,
            headers={
                "Authorization": os.environ["CLIENT_AUTHENTICATION_KEY"],
                "Content-Type": srvc.content_type,
            },
        )

        if not response.status_code == 200:
            logger.warning(
                "received non-200 status code %i from %s",
                response.status_code,
                srvc.url,
            )
            time.sleep(5)
            continue

        logger.info("successfully fetched value from %s", srvc.url)

        # extract the value used to update the KRI from the response (this ideally
        # also should be able to be configured by the client/user)
        response_json = response.json()
        payload = {"value": response_json["ops_audits_inactive_count"]}

        # now make an update request to the auditboard api using this newly extracted
        # value, with the value having an associated KRI (id) and the user/client
        # having an associated bearer token from the swagger documentation branch
        ab_url = f"http://localhost:9001/api/v1/key_risk_indicators/{srvc.kri_id}"
        response = requests.put(
            ab_url,
            headers={
                "Authorization": f"Bearer {os.environ['AUDITBOARD_BEARER_TOKEN']}",
                "Content-Type": "application/json",
            },
            json={
                "key_risk_indicator": {
                    "id": srvc.kri_id,
                    "current_value": payload["value"],
                }
            },
        )

        if not response.status_code == 200:
            logger.warning(
                "received non-200 status code %i from %s", response.status_code, ab_url
            )
            time.sleep(5)
            continue

        logger.info("successfully updated kri at %s", ab_url)

        # the wait interval can either be inside or outside the application
        # fetch/update logic
        time.sleep(5)
