class BaseCheck:
    def __init__(self, measurement, metadata, sample_id, lab_test_id, value, check_config):        
        self.measurement = measurement
        self.metadata = metadata
        self.sample_id = sample_id
        self.lab_test_id = lab_test_id
        self.value = value
        self.check_config = check_config
        
    def do_check(self):
        raise NotImplementedError

    def details_header(self, title, check):
        header = f"""{title}
Severity: {check.Severity.name}

Measurement: {self.measurement.MeasurementName}
Value: {self.value}
Check config: {self.check_config}

Run: {self.metadata.RunName}
Run date: {self.metadata.RunDate}
Project: {self.metadata.ProjectName}
Site: {self.metadata.SiteName}
Sample type code: {self.metadata.SampleTypeCode}
Sample ID: {self.sample_id}
Lab test ID: {self.lab_test_id}

Lab: {self.metadata.LabName}
Lab test name: {self.metadata.LabTestName}
Lab method: {self.metadata.LabMethod}

"""

        return header