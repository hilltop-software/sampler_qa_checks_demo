from typing import List
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass

import HilltopHost
import Hilltop

from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .. import utils


class PercentileCheck(ICheck):
    """
    An implementation of the ICheck interface that checks test results against historical percentiles.
    """

    @dataclass
    class ThresholdParams:
        metadata: dict
        result: Decimal
        percentiles: list
        percentile_range: tuple
        key: str
        site: str
        measurement: str
        size: int
        start_date: str
        end_date: str
        severity: QACheckSeverity

    def __init__(self, config, repository):
        super().__init__(config, repository)
        self.dfile1 = None
        if self.disabled:
            return
        self.period_years = self.config.get(
            "period_years", 15
        )  # default to 15 years ago
        self.min_data_points = self.config.get(
            "min_data_points", 20
        )  # default to minimum 20 data points
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - PercentileCheck is using a history limit of {self.period_years} years \
                and {self.min_data_points} data points"
        )
        # if we're not disabled then connect to the Hilltop data file
        data_file = self.config.get("data_file")
        if data_file is None:
            HilltopHost.LogWarning(
                "sampler_qa_checks_demo - data_file is required in PercentileCheck configuration"
            )
            return
        self.dfile1 = Hilltop.Connect(data_file)
        if self.dfile1 is None:
            HilltopHost.LogError(
                f"sampler_qa_checks_demo - Hilltop data file '{data_file}' not connected."
            )
            return
        self.data_file = data_file
        HilltopHost.LogInfo(
            f"sampler_qa_checks_demo - PercentileCheck connected to Hilltop data file '{data_file}'"
        )

    def __del__(self):
        if self.dfile1 is not None:
            try:
                Hilltop.Disconnect(self.dfile1)
            except Exception:
                pass  # Suppress errors during cleanup

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.has_check_result(context, "percentile_check"):
            return
        if context.Result is None or context.Result.ResultValue == "":
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
        return self.check_result_against_percentile_ranges(metadata, result)

    def check_result_against_percentile_ranges(self, metadata, result):
        """
        Checks the given result against configured percentile ranges for the specified measurement.

        Args:
            metadata (dict): Sample metadata containing measurement information.
            result (Decimal): The numeric result of the test to evaluate.

        Returns:
            List[QACheck] or None: A single QACheck if the result is outside the percentile thresholds, otherwise None.
        """
        # get the last x years of data based on the configuration
        # this ignores leap years
        start_date = (
            datetime.today() - timedelta(days=self.period_years * 365)
        ).strftime("%Y-%m-%d")
        end_date = datetime.today().strftime("%Y-%m-%d")

        measurement = metadata["MeasurementName"]
        site = metadata["SiteName"]

        s1 = Hilltop.GetData(self.dfile1, site, measurement, start_date, end_date)

        if s1.size < self.min_data_points:
            return

        critical_range = self.get_configured_percentile_range(measurement, "critical")
        if critical_range is None:
            return

        warning_range = self.get_configured_percentile_range(measurement, "warning")
        if warning_range is None:
            return

        # Use Hilltop.PDist to get percentiles
        percentiles = self.retrieve_percentile_values(
            site, measurement, start_date, end_date
        )
        if percentiles is None:
            return

        params = self.ThresholdParams(
            metadata=metadata,
            result=result,
            percentiles=percentiles,
            percentile_range=critical_range,
            key="critical",
            site=site,
            measurement=measurement,
            size=s1.size,
            start_date=start_date,
            end_date=end_date,
            severity=QACheckSeverity.Critical,
        )

        qa_check = self.evaluate_percentile_thresholds(params)
        if qa_check is not None:
            return [qa_check]

        params.percentile_range = warning_range
        params.key = "warning"
        params.severity = QACheckSeverity.Warning

        qa_check = self.evaluate_percentile_thresholds(params)
        if qa_check is not None:
            return [qa_check]

    def evaluate_percentile_thresholds(self, params: ThresholdParams):
        """
        Evaluates whether a given result breaches specified percentile thresholds.
        Args:
            params (ThresholdParams): An object containing the parameters for the threshold evaluation, including:
            - metadata (dict): Metadata containing "RunID", "SampleID", and "LabTestID".
            - percentile_range (tuple): A tuple containing the lower and upper percentile bounds.
            - percentiles (list): A list of percentile values.
            - result (float): The result to be evaluated.
            - measurement (str): The name of the measurement being evaluated.
            - key (str): A key identifying the percentile range.
            - severity (str): The severity level of the breach.
            - size (int): The number of data points.
            - site (str): The site where the data was collected.
            - start_date (str): The start date of the data collection period.
            - end_date (str): The end date of the data collection period.
        Returns:
            QACheck: An object containing details of the QA check if the result breaches the specified percentiles,
            otherwise None.
        """

        qa_check = QACheck()
        qa_check.RunID = params.metadata["RunID"]
        qa_check.SampleID = params.metadata["SampleID"]
        qa_check.LabTestID = params.metadata["LabTestID"]
        qa_check.Label = "percentile_check"

        lower, upper = params.percentile_range
        lower_ordinal = utils.ordinal(lower)
        upper_ordinal = utils.ordinal(upper)
        percentile_lower = params.percentiles[lower - 1]
        percentile_upper = params.percentiles[upper - 1]
        if params.result < percentile_lower or params.result > percentile_upper:
            qa_check.Title = f"{params.key.title()} percentile breach: {params.measurement}"
            qa_check.Severity = params.severity
            qa_check.Details = f"""{params.measurement} is outside of the configured {params.key} percentiles
{self.data_file} has {params.size} data points for {params.measurement} at {params.site}
from {params.start_date} to {params.end_date}

{params.key} percentile limits: {lower_ordinal} and {upper_ordinal}
{lower_ordinal} percentile: {percentile_lower}
{upper_ordinal} percentile: {percentile_upper}
Result: {params.result}
            """
            if params.result < percentile_lower:
                qa_check.Details += f"\nResult is below the {lower_ordinal} percentile"
            if params.result > percentile_upper:
                qa_check.Details += f"\nResult is above the {upper_ordinal} percentile"
            return qa_check

    def retrieve_percentile_values(self, site, measurement, start_date, end_date):
        """
        Retrieves percentile information from the data source.

        Args:
            site (str): Name of the site to query.
            measurement (str): Measurement to retrieve percentiles for.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            list or None: List of percentile values or None if unavailable.
        """
        pdist = Hilltop.PDist(self.dfile1, site, measurement, start_date, end_date)
        if not pdist:
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - No percentiles returned for {measurement} at {site}"
            )
            return
        # pdist is a tuple of (percentiles: numpy, extrema: dict)
        percentiles, extrema = pdist
        return percentiles

    def get_configured_percentile_range(self, measurement, key):
        """
        Retrieves the configured percentile range for the given measurement and range category.

        Args:
            measurement (str): The measurement name for which the range is retrieved.
            key (str): The category of the percentile range (e.g. 'critical', 'warning').

        Returns:
            tuple[int, int] or None: A two-element tuple of (lower, upper) percentiles if valid, otherwise None.
        """
        config = self.config[measurement].get(key, "")
        range = tuple(map(int, config.split(",")))
        if not self.validate_range(range):
            HilltopHost.LogWarning(
                f"sampler_qa_checks_demo - Invalid {key} range configured for {measurement}"
            )
            return
        return range

    def validate_range(self, range):
        """
        Validates that the specified percentile range is properly formed.

        Args:
            range (tuple[int, int] or None): The percentile range to validate.

        Returns:
            bool: True if the percentile range is valid, otherwise False.
        """
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
