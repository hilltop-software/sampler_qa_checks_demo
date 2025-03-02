import json
import pyodbc
import HilltopHost
from .config_loader import ConfigLoader
from .check_factory import CheckFactory
from . import utils

class SamplerQAChecksPluginDemo:
    """
    A plugin that demonstrates how to perform QA checks on runs, samples, and tests.
    """

    def sampler_qa_checks(self, payload):
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - checks started")
        try:

            self.config = ConfigLoader.load()

            self.save = self.config.get("save_qachecks_to_database", False)
            if self.save:
                HilltopHost.LogInfo(
                    f"sampler_qa_checks_demo - 'save_qachecks_to_database' set to true, saving checks to database"
                )
            else:
                HilltopHost.LogInfo(
                    f"sampler_qa_checks_demo - not saving checks to database"
                )

            self.connection = self.open_db_connection()

            factory = CheckFactory(self.config, self.connection)
            run_checks = factory.create_run_checks()
            sample_checks = factory.create_sample_checks()
            test_checks = factory.create_test_checks()

            for run in payload.Runs:
                for run_check in run_checks:
                    qa_checks = run_check.perform_checks(run.RunID, run)
                    self.save_qa_checks(qa_checks)
                for sample in run.Samples:
                    for sample_check in sample_checks:
                        qa_checks = sample_check.perform_checks(run.RunID, sample)
                        self.save_qa_checks(qa_checks)
                    for test in sample.Tests:
                        if test.IsTestSet == False:
                            for test_check in test_checks:
                                qa_checks = test_check.perform_checks(run.RunID, test)
                                self.save_qa_checks(qa_checks)
                        else:
                            for subtest in test.Tests:
                                for test_check in test_checks:
                                    qa_checks = test_check.perform_checks(
                                        run.RunID, subtest
                                    )
                                    self.save_qa_checks(qa_checks)
            HilltopHost.LogInfo(f"sampler_qa_checks_demo - checks finished")
        except Exception as e:
            HilltopHost.LogError(f"sampler_qa_checks_demo - error occurred: {str(e)}")

    def save_qa_checks(self, qa_checks):
        if qa_checks is None:
            return
        for qa_check in qa_checks:
            if self.save:
                HilltopHost.Sampler.SaveQACheck(qa_check)
            else:
                HilltopHost.LogInfo(utils.dump(qa_check))

    def open_db_connection(self):
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - connecting to database '{self.config.get('db_name', '')}'"
        )
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.get('db_server', 'localhost')};DATABASE={self.config.get('db_name', '')};Trusted_Connection=yes;"
        db = pyodbc.connect(connection_string)
        cursor = db.cursor()
        cursor.execute("SELECT @@version;")
        result = cursor.fetchone()
        cursor.close()
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - connected to database: {result}")
        return db
