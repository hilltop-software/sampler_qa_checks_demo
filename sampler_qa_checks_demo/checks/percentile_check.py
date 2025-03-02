from typing import List
from decimal import Decimal
from datetime import datetime, timedelta
import json

import HilltopHost
import Hilltop

from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .. import utils


class PercentileCheck(ICheck):
    """
    An implementation of the ICheck interface that checks test results against historical percentiles.
    """

    _measurement_cache = {}

    def __init__(self, config, repository):
        super().__init__(config, repository)
        self.period_years = self.config.get(
            "period_years", 15
        )  # default to 15 years ago
        self.min_data_points = self.config.get(
            "min_data_points", 20
        )  # default to minimum 20 data points
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - PercentileCheck is using a history limit of {self.period_years} years and {self.min_data_points} data points"
        )
        if self.disabled:
            return
        # if we're not disabled then connect to the Hilltop data file
        data_file = self.config.get("data_file")
        if data_file is None:
            HilltopHost.LogWarning(
                "sampler_qa_checks_demo - data_file is required in PercentileCheck configuration"
            )
        self.dfile1 = Hilltop.Connect(data_file)
        if self.dfile1 is None:
            HilltopHost.LogError(
                f"sampler_qa_checks_demo - Hilltop data file '{data_file}' not connected"
            )
        self.data_file = data_file
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - PercentileCheck connected to Hilltop data file '{data_file}'"
        )

    def __del__(self):
        Hilltop.Disconnect(self.dfile1)

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.disabled:
            return
        if self.has_check_result(context, "percentile_check"):
            return
        if context.Result is None or context.Result.ResultValue is "":
            return
        if self.dfile1 is None:
            return

        sample_id = context.SampleID
        lab_test_id = context.LabTestID

        metadata = self.repository.get_sample_metadata(sample_id, lab_test_id)
        if metadata is None:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Metadata not found for sample {sample_id}, lab test {lab_test_id}"
            )
            return

        measurement = metadata["MeasurementName"]
        if (
            measurement not in self.config
        ):  # No percentile range configured for {measurement}"
            return

        result = Decimal(context.Result.ResultValue)
        return self.check_result(metadata, result)

    def check_result(self, metadata, result):

        # get the last x years of data based on the configuration
        # this ignores leap years
        start_date = (
            datetime.today() - timedelta(days=self.period_years * 365)
        ).strftime("%Y-%m-%d")
        end_date = datetime.today().strftime("%Y-%m-%d")

        measurement = metadata["MeasurementName"]
        site = metadata["SiteName"]

        # HilltopHost.LogInfo(f"sampler_qa_checks_demo - Searching {measurement} history of {site} from {start_date} to {end_date}")
        s1 = Hilltop.GetData(self.dfile1, site, measurement, start_date, end_date)

        if s1.size < self.min_data_points:
            # HilltopHost.LogInfo(f"sampler_qa_checks_demo - Insufficient ({s1.size}) {measurement} data points for {site}")
            return

        critical_range = self.get_range(measurement, "critical")
        if critical_range is None:
            return

        warning_range = self.get_range(measurement, "warning")
        if warning_range is None:
            return

        # Use Hilltop.PDist to get percentiles
        percentiles = self.get_percentiles(site, measurement, start_date, end_date)
        if percentiles is None:
            return

        qa_check = self.check_percentiles(
            metadata,
            result,
            percentiles,
            critical_range,
            "critical",
            site,
            measurement,
            s1.size,
            start_date,
            end_date,
            QACheckSeverity.Critical,
        )
        if qa_check is not None:
            return [qa_check]

        qa_check = self.check_percentiles(
            metadata,
            result,
            percentiles,
            warning_range,
            "warning",
            site,
            measurement,
            s1.size,
            start_date,
            end_date,
            QACheckSeverity.Warning,
        )
        if qa_check is not None:
            return [qa_check]

        return None

    def check_percentiles(
        self,
        metadata,
        result,
        percentiles,
        range,
        key,
        site,
        measurement,
        size,
        start_date,
        end_date,
        severity,
    ):
        # set up a qa_check object, just in case
        qa_check = QACheck()
        qa_check.RunID = metadata["RunID"]
        qa_check.SampleID = metadata["SampleID"]
        qa_check.LabTestID = metadata["LabTestID"]
        qa_check.Label = "percentile_check"

        lower, upper = range
        lower_ordinal = utils.ordinal(lower)
        upper_ordinal = utils.ordinal(upper)
        percentile_lower = percentiles[lower - 1]
        percentile_upper = percentiles[upper - 1]
        if result < percentile_lower or result > percentile_upper:
            qa_check.Title = f"{measurement} is outside of {key} percentiles"
            qa_check.Severity = severity
            qa_check.Details = f"""{measurement} is outside of the critical percentiles
{self.data_file} has {size} data points for {measurement} at {site} from {start_date} to {end_date}
{key} percentile limits: {lower_ordinal} and {upper_ordinal}
{lower_ordinal} percentile: {percentile_lower}
{upper_ordinal} percentile: {percentile_upper}
Result: {result}
            """
            if result < percentile_lower:
                qa_check.Details += f"\nResult is below the {lower_ordinal} percentile"
            if result > percentile_upper:
                qa_check.Details += f"\nResult is above the {upper_ordinal} percentile"
            return qa_check
        return None

    def get_percentiles(self, site, measurement, start_date, end_date):
        pdist = Hilltop.PDist(self.dfile1, site, measurement, start_date, end_date)
        if not pdist:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - No percentiles returned for {measurement} at {site}"
            )
            return None
        # pdist is a tuple of (percentiles: numpy, extrema: dict)
        percentiles, extrema = pdist
        return percentiles

    def get_range(self, measurement, key):
        config = self.config[measurement].get(key, "")
        range = tuple(map(int, config.split(",")))
        if not self.validate_range(range):
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Invalid {key} range configured for {measurement}"
            )
            return None
        return range

    def validate_range(self, range):
        if range is None:
            return False
        if len(range) != 2:
            return False
        lower, upper = range
        if lower < 1 or upper > 100:
            return False
        if lower > upper:
            return False
        return True
