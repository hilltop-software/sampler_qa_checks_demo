from typing import List
from decimal import Decimal
import HilltopHost
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .i_check import ICheck


class ThresholdCheck(ICheck):
    """
    An implementation of the ICheck interface that checks test results against specified thresholds.
    """

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.has_check_result(context, "threshold_check"):
            return

        if context.Result is None or context.Result.ResultValue == "":
            return

        metadata = self.repository.get_measurement_by_lab_test_id(context.LabTestID)
        if metadata is None:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Metadata not found for lab test {context.LabTestID}"
            )
            return

        measurement = metadata["MeasurementName"]
        if measurement not in self.config:
            return

        result = Decimal(context.Result.ResultValue)
        return self.evaluate_result_against_thresholds(run_id, context, measurement, result)

    def evaluate_result_against_thresholds(self, run_id, context, measurement, result):
        """
        Args:
            run_id: The identifier of the current run.
            context: The context containing sample and result information.
            measurement: The name of the measurement associated with thresholds.
            result: The numeric result of the analysis.

        Returns:
            A list of threshold QA checks if any threshold is exceeded, otherwise None.
        """
        thresholds = self.config[measurement]

        if "Critical" in thresholds and result > Decimal(thresholds["Critical"]):
            return self.build_qa_check(
                run_id,
                context,
                measurement,
                result,
                QACheckSeverity.Critical,
                thresholds["Critical"],
            )

        if "Warning" in thresholds and result > Decimal(thresholds["Warning"]):
            return self.build_qa_check(
                run_id,
                context,
                measurement,
                result,
                QACheckSeverity.Warning,
                thresholds["Warning"],
            )

        if "Information" in thresholds and result > Decimal(thresholds["Information"]):
            return self.build_qa_check(
                run_id,
                context,
                measurement,
                result,
                QACheckSeverity.Information,
                thresholds["Information"],
            )

    def build_qa_check(
        self, run_id, context, measurement, result, severity, threshold
    ):
        """
        Creates a QA check instance based on the specified threshold and severity.

        Args:
            run_id: Unique identifier for the current run.
            context: Container for sample and lab result details.
            measurement: Name of the measurement being evaluated.
            result: Numeric result value.
            severity: Severity level of the threshold exceedance.
            threshold: Threshold value being tested against.

        Returns:
            A list containing the created QA check instance.
        """
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.LabTestID = context.LabTestID
        qa_check.Label = "threshold_check"
        qa_check.Title = f"Exceedance: {measurement}"
        qa_check.Severity = severity
        qa_check.Details = (
            f"Sample {context.SampleID} {measurement} result {result} "
            f"exceeds the {severity.name} threshold of {threshold}"
        )
        return [qa_check]
