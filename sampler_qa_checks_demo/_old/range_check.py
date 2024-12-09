import HilltopHost
from decimal import *
from .base_check import BaseCheck
from ..utils import get_parameter_value_from_test_info, truncate

class RangeCheck(BaseCheck):

    def do_check(self):
        measurement_name = self.measurement.MeasurementName
        value = Decimal(self.value) # convert to Decimal for this check
        critical_range = self.check_config.get('critical', '').split(',')
        warning_range = self.check_config.get('warning', '').split(',')

        check = HilltopHost.Sampler.QACheck()
        check.SampleID = self.sample_id
        check.LabTestID = self.lab_test_id
        check.Severity = HilltopHost.Sampler.QACheckSeverity.OK
        title = f"{value:.5f} is OK"

        if len(warning_range) == 2:
            warning_min, warning_max = map(Decimal, warning_range)
            if (value < warning_min):
                check.Severity = HilltopHost.Sampler.QACheckSeverity.Warning
                title = f"{value:.5f} is < warning min {warning_min}"
            if (value > warning_max):
                check.Severity = HilltopHost.Sampler.QACheckSeverity.Warning
                title = f"{value:.5f} is > warning max {warning_max}"

        if len(critical_range) == 2:
            critical_min, critical_max = map(Decimal, critical_range)
            if (value < critical_min):
                check.Severity = HilltopHost.Sampler.QACheckSeverity.Critical
                title = f"{value:.5f} is < critical min {critical_min}"
            if (value > critical_max):
                check.Severity = HilltopHost.Sampler.QACheckSeverity.Critical
                title = f"{value:.5f} is > critical max {critical_max}"

        check.Title = truncate(title, 50)

        check.Details = self.details_header(title, check)

        # we can append additional details to the check        
        check.Details += f"""
Lower confidence limit: {get_parameter_value_from_test_info(self.metadata.TestInfo, 'Lower Confidence Limit')}
"""

        return check
