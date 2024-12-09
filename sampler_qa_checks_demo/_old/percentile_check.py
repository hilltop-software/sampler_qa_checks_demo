import HilltopHost
import Hilltop
from decimal import *
from datetime import datetime, timedelta
from .base_check import BaseCheck
from ..utils import get_parameter_value_from_test_info, truncate

class PercentileCheck(BaseCheck):


    def __init__(self, measurement, metadata, sample_id, lab_test_id, value, check_config):        
        super().__init__(measurement, metadata, sample_id, lab_test_id, value, check_config)
        self.dfile1 = Hilltop.Connect("C:\Hilltop\Data\Processing.hts")

    def __del__(self):
        Hilltop.Disconnect(self.dfile1)

    def do_check(self):
        measurement_name = self.measurement.MeasurementName
        value = Decimal(self.value) # convert to Decimal for this check
        critical_range = self.check_config.get('critical', '').split(',')
        warning_range = self.check_config.get('warning', '').split(',')
        info_range = self.check_config.get('info', '').split(',')

        check = HilltopHost.Sampler.QACheck()
        check.SampleID = self.sample_id
        check.LabTestID = self.lab_test_id
        check.Severity = HilltopHost.Sampler.QACheckSeverity.OK
        title = f"{value:.5f} is OK"

        # get the last x years of data based on the configuration
        # this ignores leap years
        start_date = (datetime.today() - timedelta(days=self.check_config.get('period_years', 15) * 365 )).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
        s1 = Hilltop.GetData(self.dfile1, self.metadata.SiteName, measurement_name, start_date, end_date)

        # no history
        if s1.size == 0:
            return None
        
        # not enough data points        
        if s1.size < self.check_config.get('min_data_points', 0):
            return None
        
        # Use Hilltop.PDist to get percentiles
        percentiles = self.get_percentiles(self.metadata.SiteName, measurement_name, start_date, end_date)
        
        if percentiles is not None:
            check.Severity = self.check_percentiles(value, percentiles, critical_range, HilltopHost.Sampler.QACheckSeverity.Critical)
            if check.Severity == HilltopHost.Sampler.QACheckSeverity.Critical:
                title = f"{value:.5f} outside {critical_range[0]}/{critical_range[1]} percentiles"
            elif check.Severity == HilltopHost.Sampler.QACheckSeverity.OK: # not critical, try again
                check.Severity = self.check_percentiles(value, percentiles, warning_range, HilltopHost.Sampler.QACheckSeverity.Warning)
                if check.Severity == HilltopHost.Sampler.QACheckSeverity.Warning:
                    title = f"{value:.5f} outside {warning_range[0]}/{warning_range[1]} percentiles"
                elif check.Severity == HilltopHost.Sampler.QACheckSeverity.OK: # not warning, try again
                    check.Severity = self.check_percentiles(value, percentiles, info_range, HilltopHost.Sampler.QACheckSeverity.Information)
                    if check.Severity == HilltopHost.Sampler.QACheckSeverity.Information:
                        title = f"{value:.5f} outside {info_range[0]}/{info_range[1]} percentiles"
        else:
            HilltopHost.LogWarning(f"Could not retrieve percentiles for {measurement_name} at {self.metadata.SiteName}")
            return None
        
        check.Title = truncate(title, 50)
        check.Details = self.details_header(title, check)

        return check

    def get_percentiles(self, site_name, measurement_name, start_date, end_date):
        # PDist returns a tuple of (percentiles: numpy, extrema: dict)
        percentiles, extrema = Hilltop.PDist(self.dfile1, site_name, measurement_name, start_date, end_date)
        return percentiles
    
    def check_percentiles(self, value, percentiles, range, severity):
        # range is a tuple of (lower, upper)
        lower = int(range[0])
        upper = int(range[1])
        # percentiles is a 0-based numpy array, so we drop by 1
        if value < percentiles[lower-1] or value > percentiles[upper-1]:
            return severity
        return HilltopHost.Sampler.QACheckSeverity.OK
