import HilltopHost

class Repository:
    
    _measurement_cache = {}

    def __init__(self, connection):
        self.connection = connection

    def get_sample_metadata(self, sample_id, lab_test_id):
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT
                l.LabName,
                t.TestName,
                m.MeasurementName,
                m.Units,
                m.Divisor,
                x.testElement.value('Value[1]', 'varchar(30)') AS TestValue, -- Extract the <Value> element
                smp.SampleID,
                smp.SiteID,
                st.SiteName COLLATE SQL_Latin1_General_CP1_CI_AS AS SiteName,
                r.RunID,
                r.RunName,
                r.RunDate,
                COALESCE(sp.SampleTypeCode, p.SampleTypeCode) AS SampleTypeCode, -- Select from Sample first, fallback to Run
                COALESCE(sp.ProjectID, p.ProjectID) AS ProjectID, -- Select from Sample first, fallback to Run
                COALESCE(sp.ProjectName, p.ProjectName) AS ProjectName, -- Select from Sample first, fallback to Run
                smp.SampleInfo,
                x.testElement.query('.') AS TestInfo, -- Include the full XML of the test element
                x.testElement.value('@ID', 'INT') as TestID,
                lt.LabTestName,
                lt.LabMethod,
                lt.LabTestID
            FROM
                Samples smp
                OUTER APPLY SampleInfo.nodes('(SampleInfo/Test, SampleInfo/TestSet/Test)') AS x(testElement)
                JOIN LabTests lt ON lt.LabTestID = x.testElement.value('@ID', 'INT') -- Joining on the extracted Test ID--
                JOIN Labs l ON l.LabID = lt.LabID
                JOIN Tests t ON lt.TestID = t.TestID
                JOIN Measurements m ON t.HilltopMeasurementID = m.MeasurementID
                JOIN Sites st ON smp.SiteID = st.SiteID
                JOIN Runs r ON smp.RunID = r.RunID
                LEFT JOIN Projects p ON r.ProjectID = p.ProjectID -- Left join in case ProjectID is present only in Sample
                LEFT JOIN Projects sp ON smp.ProjectID = sp.ProjectID -- Join to handle Project from Sample
            WHERE
                smp.SampleID = ?
                AND lt.LabTestID = ?
            """
            cursor.execute(query, sample_id, lab_test_id)
            row  = cursor.fetchone()
            if row is None:
                cursor.close()
                return

            column_names = [column[0] for column in cursor.description]  # Extract column names
            cursor.close()
            result_dict = dict(zip(column_names, row))  # Map column names to values
            return result_dict
        except Exception as e:
            HilltopHost.LogError(f"sampler_qa_checks_demo - Error occurred: {str(e)}")

    def get_measurement_by_lab_test_id(self, lab_test_id):
        if lab_test_id in self._measurement_cache:
            return self._measurement_cache[lab_test_id]
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT
                lt.LabTestName,
                lt.LabMethod,
                lt.LabTestID,
                l.LabName,
                t.TestName,
                m.MeasurementName
            FROM
                LabTests lt
                JOIN Labs l ON l.LabID = lt.LabID
                JOIN Tests t ON lt.TestID = t.TestID
                JOIN Measurements m ON t.HilltopMeasurementID = m.MeasurementID
            WHERE
                lt.LabTestID = ?
                    """
            cursor.execute(query, lab_test_id)
            row  = cursor.fetchone()
            if row is None:
                cursor.close()
                return
            column_names = [column[0] for column in cursor.description]  # Extract column names
            cursor.close()
            result_dict = dict(zip(column_names, row))  # Map column names to values
            self._measurement_cache[lab_test_id] = result_dict
            return result_dict
        except Exception as e:
            HilltopHost.LogError(f"sampler_qa_checks_demo - Error occurred: {str(e)}")
