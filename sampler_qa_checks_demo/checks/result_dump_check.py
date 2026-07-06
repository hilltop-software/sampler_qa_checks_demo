from typing import List
from .. import utils

from .i_check import ICheck
import HilltopHost
from HilltopHost.Sampler import QACheck, QACheckSeverity


class ResultDumpCheck(ICheck):
    """
    An implementation of the ICheck interface that dumps a LabTestResult object for debugging purposes.
    """

    def perform_checks(self, run_id: int, context) -> List[QACheck]:
        if self.has_check_result(context, "result_dump_check"):
            return

        metadata = self.repository.get_measurement_by_lab_test_id(context.LabTestID)
        if metadata is None:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Metadata not found for lab test {context.LabTestID}"
            )
            return

        measurement = metadata["MeasurementName"]

        dump = utils.dump(context.Result)

        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - Result dump check for lab test {context.LabTestID} ({measurement}): {dump}"
        )

        return
        # continue below if you want to save to the database
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.LabTestID = context.LabTestID
        qa_check.Label = "result_dump_check"
        qa_check.Title = f"Result dump check: {measurement}"
        qa_check.Severity = QACheckSeverity.Information
        qa_check.Details = f"""{measurement}
Result: {dump}
        """
        return [qa_check]
