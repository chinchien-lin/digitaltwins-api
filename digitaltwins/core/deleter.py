import configparser
import os
from pathlib import Path

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

from digitaltwins import Querier
from digitaltwins.irods.irods import IRODS

import urllib3
urllib3.disable_warnings()


class Deleter(object):
    def __init__(self, config_file):
        config_file = Path(config_file)
        self._config_file = config_file
        self._configs = configparser.ConfigParser()
        self._configs.read(config_file)


        self._config_dir = self._config_file.parent
        self._gen3_cred_file = Path(self._configs["gen3"].get("cred_file"))
        self._ssl_cert = self._configs["gen3"].get("ssl_cert")
        if self._gen3_cred_file:
            self._gen3_cred_file = self._config_dir.joinpath(self._gen3_cred_file)
        if self._ssl_cert:
            self._ssl_cert = self._config_dir.joinpath(self._ssl_cert)
            os.environ["REQUESTS_CA_BUNDLE"] = str(self._ssl_cert.resolve())

        self._program = self._configs["gen3"].get("program")
        self._project = self._configs["gen3"].get("project")
        self._gen3_endpoint = self._configs["gen3"].get("endpoint")

        self._auth = Gen3Auth(self._gen3_endpoint, refresh_file=str(self._gen3_cred_file))
        self._submission = Gen3Submission(self._gen3_endpoint, self._auth)

    def delete(self, dataset_id):
        self.delete_metadata(dataset_id)
        self.delete_dataset(dataset_id)

    def delete_metadata(self, dataset_id):
        querier = Querier(self._config_file)
        records = querier.get_dataset_records(dataset_id=dataset_id, program=self._program, project=self._project)
        self._submission.delete_records(program=self._program, project=self._project, uuids=records)

    def delete_dataset(self, dataset_id):
        irods = IRODS(self._configs)
        irods.delete(dataset_id)
