from typing import List
from decimal import Decimal

from .i_check import ICheck
import HilltopHost
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .. import utils

class OutsideRangeCheck(ICheck):
    """
    An implementation of the ICheck interface that checks test results against a fixed range for the measurement.
    """

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.has_check_result(context, "outside_range_check"):
            return

        if context.Result is None or context.Result.ResultValue is "":
            return
        
        metadata = self.repository.get_measurement_by_lab_test_id(context.LabTestID)
        if metadata is None:
            HilltopHost.LogWarning(f"sampler_qa_checks_demo - Metadata not found for lab test {context.LabTestID}")
            return
        
        measurement = metadata['MeasurementName']
        
        if measurement not in self.config:
            # HilltopHost.LogWarning(f"sampler_qa_checks_demo - No range configured for {measurement}")
            return

        result = Decimal(context.Result.ResultValue)  
        return self.check_result(run_id, context, measurement, result)
    
    def check_result(self, run_id, context, measurement, result):
        # set up a qa_check object, just in case
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.LabTestID = context.LabTestID
        qa_check.Label = "outside_range_check"

        min, max = self.get_range(measurement, 'critical')
        if min and max and (result < min or result > max):
            qa_check.Title = f"{measurement} is outside of critical range"
            qa_check.Severity = QACheckSeverity.Critical
            qa_check.Details = f"""{measurement} is outside of the critical range
Critical range: {min} to {max}
Result: {result}
            """
            return [qa_check]
        
        min, max = self.get_range(measurement, 'warning')
        if min and max and (result < min or result > max):
            qa_check.Title = f"{measurement} is outside of warning range"
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = f"""{measurement} is outside of the warning range
Warning range: {min} to {max}
Result: {result}
            """
            return [qa_check]
        
    def get_range(self, measurement: str, severity: str) -> tuple:
        range_config = self.config.get(measurement, {}).get(severity)
        if range_config and 'min' in range_config and 'max' in range_config:
            return range_config['min'], range_config['max']
        return None, None
        
