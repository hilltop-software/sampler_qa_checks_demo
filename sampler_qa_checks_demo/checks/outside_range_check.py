from typing import List
from decimal import Decimal

import HilltopHost
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .. import utils

class OutsideRangeCheck(ICheck):
    """
    An implementation of the ICheck interface that checks test results against a fixed range for the measurement.
    """

    _measurement_cache = {}

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.has_check_result(context, "outside_range_check"):
            return []

        if context.Result is None or context.Result.ResultValue is "":
            return []
        
        measurement = self.get_measurement_by_lab_test_id(context.LabTestID)
        if measurement is None:
            return []

        result = Decimal(context.Result.ResultValue)        
        return self.check_result(run_id, context, measurement, result)
    
    def check_result(self, run_id, context, measurement, result):
        # set up a qa_check object, just in case
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.LabTestID = context.LabTestID
        qa_check.Label = "outside_range_check"

        min, max = self.get_range(measurement.MeasurementName, 'critical')
        if min and max and (result < min or result > max):
            qa_check.Title = f"{measurement.MeasurementName} is outside of critical range"
            qa_check.Severity = QACheckSeverity.Critical
            qa_check.Details = f"""{measurement.MeasurementName} is outside of the critical range
Critical range: {min} to {max}
Result: {result}
            """
            return [qa_check]
        
        min, max = self.get_range(measurement.MeasurementName, 'warning')
        if min and max and (result < min or result > max):
            qa_check.Title = f"{measurement.MeasurementName} is outside of warning range"
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = f"""{measurement.MeasurementName} is outside of the warning range
Warning range: {min} to {max}
Result: {result}
            """
            return [qa_check]
        
        return []

    def get_range(self, measurement_name: str, severity: str) -> tuple:
        range_config = self.config.get(measurement_name, {}).get(severity)
        if range_config and 'min' in range_config and 'max' in range_config:
            return range_config['min'], range_config['max']
        return None, None
        
    def get_measurement_by_lab_test_id(self, lab_test_id):
        if lab_test_id in self._measurement_cache:
            return self._measurement_cache[lab_test_id]
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT
                lt.LabTestName,
                lt.LabMethod,
                lt.LabTestID,
                l.LabName,
                t.TestName,
                m.MeasurementName
            FROM
                LabTests lt
                JOIN Labs l ON l.LabID = lt.LabID
                JOIN Tests t ON lt.TestID = t.TestID
                JOIN Measurements m ON t.HilltopMeasurementID = m.MeasurementID
            WHERE
                lt.LabTestID = ?
                    """
            cursor.execute(query, lab_test_id)
            result = cursor.fetchone()
            cursor.close()
            if result is None:
                HilltopHost.LogWarning(
                    f"Measurement not found for lab test {lab_test_id}"
                )
            self._measurement_cache[lab_test_id] = result
            return result
        except Exception as e:
            HilltopHost.LogError(f"Error occurred: {str(e)}")
            return None
