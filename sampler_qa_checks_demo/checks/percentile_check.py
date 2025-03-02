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
        )  # default to 15 years ago
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - PercentileCheck is using a history limit of {self.period_years} years and {self.min_data_points} data points"
        )
        if self.disabled:
            return
        # if we're not diabled then connect to the Hilltop data file
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
            return []
        if self.has_check_result(context, "percentile_check"):
            return []

        if context.Result is None or context.Result.ResultValue is "":
            return []

        if self.dfile1 is None:
            return []

        sample_id = context.SampleID
        lab_test_id = context.LabTestID

        metadata = self.repository.get_sample_metadata_by_sample_and_lab_test_id(
            sample_id, lab_test_id
        )
        if metadata is None:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Metadata not found for sample {sample_id}, lab test {lab_test_id}"
            )
            return []

        measurement = metadata["MeasurementName"]
        if measurement not in self.config:
            # HilltopHost.LogWarning(f"sampler_qa_checks_demo - No percentile range configured for {measurement}")
            return []

        result = Decimal(context.Result.ResultValue)
        return self.check_result(run_id, metadata, result)

    def check_result(self, run_id, metadata, result):
        # set up a qa_check object, just in case
        qa_check = QACheck()
        qa_check.RunID = run_id
        qa_check.SampleID = metadata["SampleID"]
        qa_check.LabTestID = metadata["LabTestID"]
        qa_check.Label = "percentile_check"


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
            return None

        critical_config = self.config[measurement].get("critical", "")
        critical_range = tuple(map(int, critical_config.split(",")))
        if not self.validate_range(critical_range):
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Invalid critical range configured for {measurement}"
            )
            return []

        warning_config = self.config[measurement].get("warning", "")
        warning_range = tuple(map(int, warning_config.split(",")))
        if not self.validate_range(warning_range):
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Invalid warning range configured for {measurement}"
            )

        # Use Hilltop.PDist to get percentiles
        percentiles = self.get_percentiles(site, measurement, start_date, end_date)

        if percentiles is None:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - No percentiles returned for {measurement} at {site}"
            )
            return []

        lower, upper = critical_range
        lower_ordinal = utils.ordinal(lower)
        upper_ordinal = utils.ordinal(upper)
        percentile_lower = percentiles[lower - 1]
        percentile_upper = percentiles[upper - 1]
        if result < percentile_lower or result > percentile_upper:
            qa_check.Title = f"{measurement} is outside of critical percentiles"
            qa_check.Severity = QACheckSeverity.Critical
            qa_check.Details = f"""{measurement} is outside of the critical percentiles
{self.data_file} has {s1.size} data points for {measurement} at {site} from {start_date} to {end_date}
Critical percentile limits: {lower_ordinal} and {upper_ordinal}
{lower_ordinal} percentile: {percentile_lower}
{upper_ordinal} percentile: {percentile_upper}
Result: {result}
            """
            if result < percentile_lower:
                qa_check.Details += f"\nResult is below the {lower_ordinal} percentile"
            if result > percentile_upper:
                qa_check.Details += f"\nResult is above the {upper_ordinal} percentile"
            return [qa_check]

        lower, upper = warning_range
        lower_ordinal = utils.ordinal(lower)
        upper_ordinal = utils.ordinal(upper)
        percentile_lower = percentiles[lower - 1]
        percentile_upper = percentiles[upper - 1]
        if result < percentile_lower or result > percentile_upper:
            qa_check.Title = f"{measurement} is outside of warning percentiles"
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = f"""{measurement} is outside of the warning percentiles
{self.data_file} has {s1.size} data points for {measurement} at {site} from {start_date} to {end_date}
Warning percentile limits: {lower_ordinal} and {upper_ordinal}
{lower_ordinal} percentile: {percentile_lower}
{upper_ordinal} percentile: {percentile_upper}
Result: {result}
            """
            if result < percentile_lower:
                qa_check.Details += f"\nResult is below the {lower_ordinal} percentile"
            if result > percentile_upper:
                qa_check.Details += f"\nResult is above the {upper_ordinal} percentile"
            return [qa_check]


        return []

    def get_percentiles(self, site, measurement, start_date, end_date):
        # percentiles is a tuple of (percentiles: numpy, extrema: dict)
        pdist = Hilltop.PDist(self.dfile1, site, measurement, start_date, end_date)
        if pdist:
            percentiles, extrema = pdist
            # HilltopHost.LogInfo(f"Percentiles ({percentiles[0].size}): {percentiles}")
            return percentiles
        return None

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

