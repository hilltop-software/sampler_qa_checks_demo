from typing import List
from decimal import Decimal

from .i_check import ICheck
import HilltopHost
from HilltopHost.Sampler import QACheck, QACheckSeverity


class OutsideRangeCheck(ICheck):
    """
    An implementation of the ICheck interface that checks test results against a fixed range for the measurement.
    """

    def perform_checks(self, run_id: int, context) -> List[QACheck]:
        if self.has_check_result(context, "outside_range_check"):
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
        return self.check_result_against_range(run_id, context, measurement, result)

    def check_result_against_range(
        self, run_id, context, measurement, result
    ) -> List[QACheck] | None:
        """
        Checks the result of a measurement against configured critical and warning ranges.

        Args:
            run_id: The run ID for the check
            context: The context containing result data
            measurement: The name of the measurement being checked
            result: The numeric result for the measurement

        Returns:
            A list of QACheck objects or None if no range violation is found
        """
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.LabTestID = context.LabTestID
        qa_check.Label = "outside_range_check"

        min, max = self.get_range(measurement, "critical")
        if min and max and (result < min or result > max):
            qa_check.Title = f"Outside critical range: {measurement}"
            qa_check.Severity = QACheckSeverity.Critical
            qa_check.Details = f"""{measurement} is outside of the critical range
Critical range: {min} to {max}
Result: {result}
            """
            return [qa_check]

        min, max = self.get_range(measurement, "warning")
        if min and max and (result < min or result > max):
            qa_check.Title = f"Outside warning range: {measurement}"
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = f"""{measurement} is outside of the warning range
Warning range: {min} to {max}
Result: {result}
            """
            return [qa_check]

    def get_range(self, measurement: str, severity: str) -> tuple:
        """
        Retrieves the configured minimum and maximum values for the specified measurement and severity.

        Args:
            measurement (str): The name of the measurement to check.
            severity (str): The severity level (e.g., 'critical' or 'warning').

        Returns:
            tuple: A tuple containing the minimum and maximum values if available, otherwise (None, None).
        """
        range_config = self.config.get(measurement, {}).get(severity)
        if range_config and "min" in range_config and "max" in range_config:
            return range_config["min"], range_config["max"]
        return None, None
