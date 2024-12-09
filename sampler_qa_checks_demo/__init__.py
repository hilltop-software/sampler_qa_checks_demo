import os
import HilltopHost
from .config_loader import load_config
from .check_factory import CheckFactory
from . import utils

class SamplerQAChecksPluginDemo:

    def load_config(self):
        config_section = HilltopHost.System.GetConfigSection("sampler_qa_checks_demo")
        if not config_section:
            raise ValueError("sampler_qa_checks_demo configuration section not found")
        config_file_path = config_section.get("ConfigFilePath")
        if config_file_path is None:
            raise ValueError("ConfigFilePath configuration item not found")
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"configuration file not found: {config_file_path}")
        config = load_config(config_file_path)
        return config

    def sampler_qa_checks(self, payload):
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - checks started")
        try:
            config = self.load_config()
            HilltopHost.LogInfo(f"sampler_qa_checks_demo - config file loaded")
            factory = CheckFactory(config)
            run_checks = factory.create_run_checks()
            for run in payload.Runs:
                HilltopHost.LogInfo(f"sampler_qa_checks_demo - checking run {run.RunName} ({run.RunID})")
                # HilltopHost.LogInfo(str(utils.dump_object(run)))
                for run_check in run_checks:
                    qa_checks = run_check.perform_checks(run)
                    for qa_check in qa_checks:
                        HilltopHost.Sampler.SaveQACheck(qa_check)
                break
            # check_manager = CheckManager(config, "range")
            # for test in payload.LabTestResults:
            #     result_value = test.ResultValue if test.ResultValue else test.Result
            #     check_manager.perform_checks(sample_id=test.SampleID, lab_test_id=test.LabTestID, value=result_value)
            #     i+=1
            HilltopHost.LogInfo(
                f"sampler_qa_checks_demo - checks finished"
            )
        except Exception as e:
            HilltopHost.LogError(f"sampler_qa_checks_demo - error occurred: {str(e)}")

    # def sampler_qa_checks(self, payload):
    #     with open('Sampler_Qa_Checks_Payload_actual.txt', 'w') as file:
    #         file.write("QA Checks payload:\n")
    #         for run in payload.Runs:
    #             file.write(self.get_run_str(run))
    #             check = HilltopHost.Sampler.QACheck()
    #             check.Severity = HilltopHost.Sampler.QACheckSeverity.OK
    #             check.Title = "QA Check Title from TestExtension"
    #             check.Details = "QA Check Details from TestExtension Run Level"
    #             check.RunID = run.RunID
    #             HilltopHost.Sampler.SaveQACheck(check)
    #             for sample in run.Samples:
    #                 file.write(self.get_sample_str(sample))
    #                 HilltopHost.LogInfo(f"sample.Project.CostCode: {self.dump_object(sample.Project.CostCode)}\n")
    #                 check.SampleID = sample.SampleID
    #                 check.Details = "QA Check Details from TestExtension Sample Level"
    #                 HilltopHost.Sampler.SaveQACheck(check)
    #                 for test in sample.Tests:
    #                     file.write("Test =====================\n")
    #                     file.write(f"{self.dump_object(test, ['Result','Tests'])}\n")
    #                     check.LabTestID = test.LabTestID
    #                     check.Details = "QA Check Details from TestExtension Lab Test Level"
    #                     if type(test.Result) is not type(None):
    #                         file.write("TestResult for the SubTest ====================\n")
    #                         file.write(f"{self.dump_object(test.Result)}\n")
    #                     for subTest in test.Tests:
    #                         check.LabTestID = subTest.LabTestID
    #                         check.Details = "QA Check Details from TestExtension Lab Test from the Test Set"
    #                         file.write("SubTest====================\n")
    #                         file.write(f"{self.dump_object(subTest, ['Result', 'Tests'])}\n")
    #                         HilltopHost.Sampler.SaveQACheck(check)
    #                         if type(subTest.Result) is not type(None):
    #                             file.write("SubTest TestResult ====================\n")
    #                             file.write(f"{self.dump_object(test.Result)}\n")

    #                     if not test.IsTestSet:
    #                         HilltopHost.Sampler.SaveQACheck(check)


# class HilltopLabQAPercentileChecksPlugin:

#     def run_lab_test_qa_checks(self, payload):
#         HilltopHost.LogInfo(f"Checks started")
#         try:
#             package_dir = os.path.dirname(__file__)
#             config_file_path = os.path.join(package_dir, 'config.example.yaml')
#             check_manager = CheckManager(config_file_path, "percentiles")
#             i=0
#             for test in payload.LabTestResults:
#                 result_value = test.ResultValue if test.ResultValue else test.Result
#                 check_manager.perform_checks(sample_id=test.SampleID, lab_test_id=test.LabTestID, value=result_value)
#                 i+=1
#         except Exception as e:
#             HilltopHost.LogError(f"Error occurred: {str(e)}")
#         HilltopHost.LogInfo(f"Checks finished on {i} results")

# class HilltopLabQAExtremaChecksPlugin:

#     def run_lab_test_qa_checks(self, payload):
#         HilltopHost.LogInfo(f"Checks started")
#         try:
#             package_dir = os.path.dirname(__file__)
#             config_file_path = os.path.join(package_dir, 'config.example.yaml')
#             check_manager = CheckManager(config_file_path, "extrema")
#             i=0
#             for test in payload.LabTestResults:
#                 result_value = test.ResultValue if test.ResultValue else test.Result
#                 check_manager.perform_checks(sample_id=test.SampleID, lab_test_id=test.LabTestID, value=result_value)
#                 i+=1
#         except Exception as e:
#             HilltopHost.LogError(f"Error occurred: {str(e)}")
#         HilltopHost.LogInfo(f"Checks finished on {i} results")
