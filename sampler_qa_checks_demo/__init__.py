import pyodbc
import traceback
import HilltopHost
from .config_loader import ConfigLoader
from .check_factory import CheckFactory
from . import utils


class SamplerQAChecksPluginDemo:
    """
    A plugin that demonstrates how to perform QA checks on runs, samples, and tests.
    """

    def sampler_qa_checks(self, payload):
        HilltopHost.LogInfo("sampler_qa_checks_demo - checks started")
        try:

            self.config = ConfigLoader.load()

            self.save = self.config.get("save_qachecks_to_database", False)
            if self.save:
                HilltopHost.LogInfo(
                    "sampler_qa_checks_demo - 'save_qachecks_to_database' set to true, saving checks to database"
                )
            else:
                HilltopHost.LogInfo(
                    "sampler_qa_checks_demo - not saving checks to database"
                )

            self.connection = self.open_db_connection()

            factory = CheckFactory(self.config, self.connection)
            run_checks = factory.create_run_checks()
            sample_checks = factory.create_sample_checks()
            test_checks = factory.create_test_checks()

            for run in payload.Runs:
                self.check_runs(run_checks, run)
                for sample in run.Samples:
                    self.check_samples(sample_checks, run, sample)
                    for test in sample.Tests:
                        self.check_tests(test_checks, run, test)
            HilltopHost.LogInfo("sampler_qa_checks_demo - checks finished")
        except Exception as e:
            HilltopHost.LogError(
                f"sampler_qa_checks_demo - error occurred: {e}: {traceback.format_exc()}"
            )

    def check_tests(self, test_checks, run, test):
        if test.IsTestSet:
            for subtest in test.Tests:
                for test_check in test_checks:
                    if test_check.disabled:
                        continue
                    qa_checks = test_check.perform_checks(run.RunID, subtest)
                    self.save_qa_checks(qa_checks)
        else:
            for test_check in test_checks:
                if test_check.disabled:
                    continue
                qa_checks = test_check.perform_checks(run.RunID, test)
                self.save_qa_checks(qa_checks)

    def check_samples(self, sample_checks, run, sample):
        for sample_check in sample_checks:
            if sample_check.disabled:
                continue
            qa_checks = sample_check.perform_checks(run.RunID, sample)
            self.save_qa_checks(qa_checks)

    def check_runs(self, run_checks, run):
        for run_check in run_checks:
            if run_check.disabled:
                continue
            qa_checks = run_check.perform_checks(run.RunID, run)
            self.save_qa_checks(qa_checks)

    def save_qa_checks(self, qa_checks):
        if qa_checks is None:
            return
        for qa_check in qa_checks:
            if self.save:
                HilltopHost.Sampler.SaveQACheck(qa_check)
            else:
                HilltopHost.LogInfo(utils.dump(qa_check))

    def open_db_connection(self):
        db_server = self.config.get("db_server", "localhost")
        db_name = self.config.get("db_name", "")
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - connecting to database '{db_name}'"
        )
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};\
            SERVER={db_server};DATABASE={db_name};Trusted_Connection=yes;"
        db = pyodbc.connect(connection_string)
        cursor = db.cursor()
        cursor.execute("SELECT @@version;")
        result = cursor.fetchone()
        cursor.close()
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - connected to database: {result}")
        return db
