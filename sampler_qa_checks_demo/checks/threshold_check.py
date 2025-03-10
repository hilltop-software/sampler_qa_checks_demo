from typing import List
from decimal import Decimal
import HilltopHost
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .i_check import ICheck
from .. import utils

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
            HilltopHost.LogWarning(f"sampler_qa_checks_demo - Metadata not found for lab test {context.LabTestID}")
            return

        measurement = metadata['MeasurementName']
        if measurement not in self.config:
            return

        result = Decimal(context.Result.ResultValue)        
        return self.check_result(run_id, context, measurement, result)

    def check_result(self, run_id, context, measurement, result):
        thresholds = self.config[measurement]

        if 'Critical' in thresholds and result > Decimal(thresholds['Critical']):
            return self.create_qa_check(run_id, context, measurement, result, QACheckSeverity.Critical, thresholds['Critical'])

        if 'Warning' in thresholds and result > Decimal(thresholds['Warning']):
            return self.create_qa_check(run_id, context, measurement, result, QACheckSeverity.Warning, thresholds['Warning'])

        if 'Information' in thresholds and result > Decimal(thresholds['Information']):
            return self.create_qa_check(run_id, context, measurement, result, QACheckSeverity.Information, thresholds['Information'])

    def create_qa_check(self, run_id, context, measurement, result, severity, threshold):
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.LabTestID = context.LabTestID
        qa_check.Label = "threshold_check"
        qa_check.Title = f"{measurement[:39]} exceedance"
        qa_check.Severity = severity
        qa_check.Details = f"Sample {context.SampleID} {measurement} result {result} exceeds the {severity.name} threshold of {threshold}"
        return [qa_check]