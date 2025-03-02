# Sampler QA Checks Plugin Demonstration

This repository provides demonstration code for running QA checks in Sampler as a Hilltop plugin. It requires a Hilltop Sampler installation.

For more information, read the Hilltop guide for developing Hilltop plugins.

> [!NOTE]
> You do no have to implement your plugin following this architecture. All your plugin must do is implement an entry point for `sampler_qa_checks()` and use `HilltopHost.Sampler.SaveQACheck()` to save your QA checks to the database.
> 
> Even saving QA checks is optional, you may chose to write a report and save it somewhere instead, or send a notification, it's entirely up to you. For example, you may wish to save just a single `OK` QA check for the whole run, once all results are in and all checks pass.

## Hilltop Python package installation

When installing Hilltop plugins, you must call the embedded `python.exe` from your Hilltop `Libs` directory.

### Development mode

Navigate to the root directory and run `pip install` in `--editable` mode.

```powershell
<path to hilltop>\Libs\python.exe -m pip install --editable .
```

When installed correctly, the plugin will be called when LabMail is run, check the Sampler logs.

### Build for installation

Navigate to the root directory and run `build`.

```powershell
<path to hilltop>\Libs\python.exe -m build -n .
```

This will create both `tar.gz` and `whl` Python packages for installation. add `--wheel` if you just want the `whl` package.

### Install the plugin package

```powershell
<path to hilltop>\Libs\python.exe -m pip install .\dist\sampler_qa_checks_demo-1.0-py3-none-any.whl
```

### Uninstall the plugin package

```powershell
<path to hilltop>\Libs\python.exe -m pip uninstall sampler_qa_checks_demo
```

## Configuration

The plugin uses a YAML configuration following the example at `sampler_qa_checks_demo\config.example.yaml`.

To configure the plugin, create a copy of this file and add the file path as `ConfigFile` in your `HilltopSystem.dsn`:

```ini
[sampler_qa_checks_demo]
ConfigFile=C:\Hilltop\Config\sampler_qa_checks_demo.yaml
```

The plugin will use this path to read the rest of the plugin configuration contained in the YAML file.

### YAML configuration

`sampler_qa_checks_demo.example.yaml` is commented with descriptions of each configuration item. Their are top-level configurations required for the plugin then configuration sections named after each individual check that implements the `ICheck` interface. The name of the class and the name of the YAML section must match.

For example, this is the configuration section for the `RunCheck` implementation:

```yaml
RunCheck:
  name_max_length: 80
```

### Database connections

A connection to the Hilltop metadata database is established using `pyodbc`. The server and database name can be set in the YAML config file:

```yaml
db_server: localhost
db_name: Hilltop
```

The connection is established using `Trusted_Connection=yes;` so no username or password is included. You must configure the database to accept such connections or update the code to use a different method for authentication.

## Getting started

* Install the plugin package, either as a wheel or in development mode as described above.
* Install the `Hilltop` Python package, available as a download from Hilltop releases.
* Configure a demonstration lab with lab tests in Sampler.
* Create a run with samples and lab tests from your demo lab.
* Edit the run status to `Sent to lab` so it's ready to receive results.
* Import results for your lab tests. You can use [hilltop-software/resultsdelivery_plugin_demo](https://github.com/hilltop-software/resultsdelivery_plugin_demo) to create mock lab results.
* Run LabMail.
* Open `Sampler.log` to see log entries from the plugin.

### Saving demo QA checks to the database

By default, this plugin doesn't add QA checks to the database.

To enable this, you need to add this to your YAML configuration file:

```yaml
save_qachecks_to_database: true
```

> **Warning**
Adding this setting and using this plugin on production data for lab settings, lab tests and production runs may result in demonstration QA checks to be added to your production database. Be careful to use this plugin on demonstration or testing installations only.

## Implemented checks

### Run checks

#### RunNameCheck

This check will raise a QA check with severity `Information` against a run if the run name is longer than the specified limit. The limit is configured in the YAML config file. The default is 100.

```yaml
RunNameCheck:
  name_max_length: 100
```

### Sample checks

#### SampleTimeCheck

This check will raise a QA check with severity `Warning` against a sample if the sample date is older than the specified limit and the sample still has status `SOME_RESULTS_BACK`. The limit is configured in the YAML config file. The default is 3 days.

```yaml
SampleTimeCheck:
  age_limit: 3 # days
```

### Lab test checks

#### OutsideRangeCheck

This check will raise a QA check with either `Warning` or `Critical` severity against a lab test result if the result falls outside the specified range. You must specify the Hilltop measurement name for the lab test and provide either a `warning` range, `critical` range or both.

```yaml
OutsideRangeCheck:
  "pH": # Hilltop measurement name
    critical: 
      min: 5
      max: 9
    warning:
      min: 6
      max: 8
```

#### PercentileCheck

This check will raise a QA check with either `Warning` or `Critical` severity against a lab test result if the result falls outside the specified percentiles from the historical record for that site and measurement. You must specify the Hilltop measurement name for the lab test and provide a `warning` range and `critical` range. You must also specify the Hilltop `data_file` where the historical record can be found. You can also specify the `min_data_points` required in the historical record before the check can be performed and the `period_years` for how far back in the historical record you will look.

This check requires the `Hilltop` Python module, which can be downloaded from the Hilltop releases and installed as a Python wheel.

```yaml
PercentileCheck: # test-level check that checks a result is within a certain percentile
  data_file: "C:\\Hilltop\\WQADC_Demo\\Archive.hts"
  min_data_points: 15
  period_years: 25
  "pH": # Hilltop measurement name
    critical: 15,85
    warning: 20,80
```

## Testing checks

### SimpleCheck

This will add a QA check record to every run. Once only.

```yaml
SimpleCheck:
  disabled: false
```

### NoisyCheck

This has a 50/50 chance of adding a critical QA check to a sample. It doesn't check for previous QA checks so it can add multiple QA checks to the same sample if it's run repeatedly.

```yaml
NoisyCheck:
  disabled: false
```

## Adding new checks

To add a new check:

1. Create a new class that implements the `ICheck` interface and put it in the `checks` folder.
2. Add a reference to the check in `CheckRegistry` at `check_registry.py` and add the class name to the `run_checks`, `sample_checks`, or `test_checks` arrays.

The class will then be called and passed:

* A run, sample, or test payload, depending on the registered check level.
* The matching class configuration section from the YAML configuration file.
* An active `pyodbc` database connection to the Hilltop database in case it's needed.

## Preventing duplicate checks by checking labels

When you call `HilltopHost.Sampler.SaveQACheck()` to save a QACheck you must attach a mandatory label. This is provided back to you so you can see if youve already reported a problem.

Run, sample, or test objects provided in the payload include a `QAChecks` attribute containing previous checks saved against that object. By checking the labels in the `QAChecks` you can see if your check has already been saved, and skip creating it again. The `ICheck` interface provides a `has_check_result()` helper method to make this easier:

```python
if self.has_check_result(context, "outside_range_check"):
    return
```