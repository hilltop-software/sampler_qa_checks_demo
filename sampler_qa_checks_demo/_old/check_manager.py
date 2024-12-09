import HilltopHost
from .repository import Repository
from .utils import dump_object
from .checks.range_check import RangeCheck
from .checks.percentile_check import PercentileCheck
from .checks.extrema_check import ExtremaCheck

class CheckManager:
    def __init__(self, config, check=None):
        self.config = load_config(config_path)
        self.check = check

    def perform_checks(self, sample_id, lab_test_id, value):
        # find the measurement to see if we're interested in it
        db = Repository(server='localhost', database='MDC', username='hilltop', password='hilltop')
        measurement = db.get_measurement_by_lab_test_id(lab_test_id)
        if measurement is None:
            HilltopHost.LogWarning(f"Measurement not found for lab test {lab_test_id}")
            return
        if measurement.MeasurementName not in self.config.get('measurements', {}):
            return # ignore this measurement

        # ensure we have metadata for context
        metadata = db.get_sample_metadata_by_sample_and_lab_test_id(sample_id, lab_test_id)
        if metadata is None:
            HilltopHost.LogWarning(f"Metadata not found for sample {sample_id}, lab test {lab_test_id}")
            return

        # perform checks        
        checks = self.config.get('measurements', {})[measurement.MeasurementName]
        for check_type, check_config in checks.items():
            try:
                qa_check = None
                if check_type == 'extrema' and check_type == self.check:
                    extrema_check = ExtremaCheck(measurement, metadata, sample_id, lab_test_id, value, check_config)
                    qa_check = extrema_check.do_check()
                elif check_type == 'range' and check_type == self.check:
                    range_check = RangeCheck(measurement, metadata, sample_id, lab_test_id, value, check_config)
                    qa_check = range_check.do_check()
                elif check_type == 'percentiles' and check_type == self.check:
                    percentile_check = PercentileCheck(measurement, metadata, sample_id, lab_test_id, value, check_config)
                    qa_check = percentile_check.do_check()
                if qa_check:
                    HilltopHost.Sampler.SaveQACheck(qa_check)
            except Exception as e:
                HilltopHost.LogWarning(f"Check execution failed: {str(e)}")
