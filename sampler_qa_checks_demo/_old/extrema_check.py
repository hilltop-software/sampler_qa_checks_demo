# sampler_qa_checks_demo/checks/extrema_check.py
import HilltopHost
import Hilltop
from decimal import *
from datetime import datetime, timedelta
from .base_check import BaseCheck
from ..utils import get_parameter_value_from_test_info, truncate

class ExtremaCheck(BaseCheck):
    def __init__(self, measurement, metadata, sample_id, lab_test_id, value, check_config):
        super().__init__(measurement, metadata, sample_id, lab_test_id, value, check_config)
        self.dfile1 = Hilltop.Connect("C:\\Hilltop\\Data\\Processing.hts")

    def __del__(self):
        Hilltop.Disconnect(self.dfile1)

    def do_check(self):
        measurement_name = self.measurement.MeasurementName
        value = Decimal(self.value)  # convert to Decimal for this check
        critical_range = self.check_config.get('critical', '').split(',')
        warning_range = self.check_config.get('warning', '').split(',')
        info_range = self.check_config.get('info', '').split(',')

        check = HilltopHost.Sampler.QACheck()
        check.SampleID = self.sample_id
        check.LabTestID = self.lab_test_id
        check.Severity = HilltopHost.Sampler.QACheckSeverity.OK
        title = f"{value:.5f} is OK"

        start_date = (datetime.today() - timedelta(days=self.check_config.get('period_years', 15) * 365)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')

        s1 = Hilltop.GetData(self.dfile1, self.metadata.SiteName, measurement_name, start_date, end_date)
        if s1.size == 0 or s1.size < self.check_config.get('min_data_points', 0):
            return None

        extrema = self.get_extrema(self.metadata.SiteName, measurement_name, start_date, end_date)
        if extrema is not None:
            check.Severity = self.check_extrema(value, extrema, critical_range, HilltopHost.Sampler.QACheckSeverity.Critical)
            if check.Severity == HilltopHost.Sampler.QACheckSeverity.Critical:
                title = f"{value:.5f} outside critical extrema"
            elif check.Severity == HilltopHost.Sampler.QACheckSeverity.OK:
                check.Severity = self.check_extrema(value, extrema, warning_range, HilltopHost.Sampler.QACheckSeverity.Warning)
                if check.Severity == HilltopHost.Sampler.QACheckSeverity.Warning:
                    title = f"{value:.5f} outside warning extrema"
                elif check.Severity == HilltopHost.Sampler.QACheckSeverity.OK:
                    check.Severity = self.check_extrema(value, extrema, info_range, HilltopHost.Sampler.QACheckSeverity.Information)
                    if check.Severity == HilltopHost.Sampler.QACheckSeverity.Information:
                        title = f"{value:.5f} outside info extrema"
        else:
            HilltopHost.LogWarning(f"Could not retrieve extrema for {measurement_name} at {self.metadata.SiteName}")
            return None

        check.Title = truncate(title, 50)
        check.Details = self.details_header(title, check)
        return check

    def get_extrema(self, site_name, measurement_name, start_date, end_date):
        # PDist returns a tuple of (percentiles: numpy, extrema: dict)
        percentiles, extrema = Hilltop.PDist(self.dfile1, site_name, measurement_name, start_date, end_date)
        return extrema  # return extrema dict

    def check_extrema(self, value, extrema, range, severity):
        lower = extrema['Min'] - extrema['StdDev'] 
        upper = extrema['Max'] + extrema['StdDev']
        if value < lower or value > upper:
            return severity
        return HilltopHost.Sampler.QACheckSeverity.OK