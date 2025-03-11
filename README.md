# Sampler QA Checks Plugin Demonstration

This repository provides demonstration code for running QA checks in Sampler as a Hilltop plugin. It requires a Hilltop Sampler installation.

For more information, read the Hilltop guide for developing Hilltop plugins.

> [!NOTE]
> You do not have to implement your plugin following this architecture. The only thing your plugin must implement is an entry point for `sampler_qa_checks()`. See `project.toml` for an example entry point configuration.
> 
> To save QA checks back into Sampler, use `HilltopHost.Sampler.SaveQACheck()`. Saving QA checks is optional and saving QA checks for runs, samples and lab tests are optional. Alternative approaches include:
> - Write a report to file or send a notification and don't save any QA checks into Sampler.
> - Save a single `OK` QA check for a run, once all results are in and all checks pass.

## Prerequisites

- The latest database migration scripts for QA checks must be run.
- The `Hilltop` Python module dependency must be installed,

Both of these are available for download from the [beta release page](https://www.hilltop.co.nz/docs/guides/scripting-and-development/Plugins/beta/).


> [!NOTE]
> This demonstration plugin code expects a Hilltop installation with the Sampler tables in the main metadata database (`HasSampler=1`) and database style **3** (Sites, Measurements, and DataSources tables).
>
> If you have a separate database for Sampler tables, or a different database style, you will need to modify for your environment.

## Package installation

Refer to [Python package management with PIP](https://www.hilltop.co.nz/docs/guides/scripting-and-development/Plugins/#python-package-management-with-pip) in the Hilltop documentation for general instructions on package management for Hilltop plugins.

### Development mode

Installing the plugin in development mode allows you to make changes on the fly during development and testing.

Navigate to the root directory of this plugin and run `pip install` in `--editable` mode.

```powershell
<path to hilltop>\Libs\python.exe -m pip install --editable .
```

When installed correctly, the plugin will be called when LabMail is run. Ensure LabMail is not running in your test environment, then run LabMail manually and check the Sampler logs.

```powershell
PS C:\Hilltop> .\LabMail.exe N
```

### Build the package for distribution

Navigate to the root directory and run `build`.

```powershell
<path to hilltop>\Libs\python.exe -m build -n .
```

This will create both `tar.gz` and `whl` Python packages in the `dist` directory for distribution. Add `--wheel` if you just want the `whl` package.

### Install the plugin package

```powershell
<path to hilltop>\Libs\python.exe -m pip install .\dist\sampler_qa_checks_demo-1.0-py3-none-any.whl
```

### Uninstall the plugin package

```powershell
<path to hilltop>\Libs\python.exe -m pip uninstall sampler_qa_checks_demo
```

## Configuration

The plugin uses a YAML configuration following the example at `sampler_qa_checks_demo.example.yaml`. 

Using YAML allows the main `HilltopSystem.dsn` to remain uncluttered and protected from users, and lets users manage the plugin configuration from a seperate file. You do not have to use YAML in your own plugins. Hilltop plugins give you access to configuration items in your `HilltopSystem.dsn` file and through Sampler settings and you can use these to bootstrap your configuration. Refer to the Hilltop plugin development guide for more information.

To configure the plugin, create a copy of `sampler_qa_checks_demo.example.yaml` somewhere and add the file path using a `ConfigFile` entry in your `HilltopSystem.dsn` under a `[sampler_qa_checks_demo]` section:

```ini
[sampler_qa_checks_demo]
ConfigFile=C:\Hilltop\Config\sampler_qa_checks_demo.yaml
```

The plugin will use this path to read the rest of the plugin configuration contained in the YAML file.

### YAML configuration

`sampler_qa_checks_demo.example.yaml` is commented with descriptions of each configuration item. Their are top-level configurations required for the plugin then configuration sections named after each individual check type. The name of the Python class for the check and the name of the YAML section must match.

For example, this is the configuration section for the `RunCheck` implementation:

```yaml
RunCheck:
  name_max_length: 80
```

### Database connections

A connection to the Hilltop metadata database is established using `pyodbc`. The server and database name are set in the YAML config file:

```yaml
db_server: localhost
db_name: Hilltop
```

The connection is established using `Trusted_Connection=yes;` so no username or password is included. You must configure the database to accept such connections or update the code to use a different method for authentication.

## Getting started

The QA checks feature looks for runs and samples that either have the `SOME_RESULTS_BACK` or `ALL_RESULTS_BACK` status. You can either use an existing test database with lab results or add your own lab results using the result delivery plugin entry point and a result delivery plugin.

### Saving demo QA checks to the database

By default, this plugin doesn't add QA checks to the database.

To enable this, you need to add this to your YAML configuration file:

```yaml
save_qachecks_to_database: true
```

> **Warning**
Adding this setting and using this plugin on production data for lab settings, lab tests and production runs may result in demonstration QA checks to be added to your production database. Be careful, and use this demonstration plugin on test installations only.

## Disabling checks

Each check type can be disabled by setting `disabled: true`:

```yaml
MissingResultsCheck:
  disabled: true
  age_limit: 3 # days
```

Checks are also ignored if they are not in the YAML configuration.

## Implemented checks

### Run checks

#### RunNameCheck

This check will raise a QA check with severity `Information` against a run if the run name is longer than the specified limit. The limit is configured in the YAML config file. The default is 100.

```yaml
RunNameCheck:
  name_max_length: 100
```

### Sample checks

#### MissingResultsCheck

This check will raise a QA check with severity `Warning` against a sample if the sample date is older than the specified limit and the sample still has status `SOME_RESULTS_BACK`. The limit is configured in the YAML config file. The default is 3 days.

```yaml
MissingResultsCheck:
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

#### ThresholdCheck

This check will raise a QA check as Information, Warning, or Critical if the result value is over a predefined threshold for that measurement.

```yaml
ThresholdCheck:
  "Nitrate - Nitrogen": # Hilltop measurement name
    Information: 1.0
    Warning: 3.0
    Critical: 10.0
```

#### PercentileCheck

This check requires the `Hilltop` Python package is installed.

This check will raise a QA check with either `Warning` or `Critical` severity against a lab test result if the result falls outside the specified percentiles using the historical record for that site and measurement. You must specify the Hilltop measurement name for the lab test and provide a `warning` range and `critical` range. You must also specify the Hilltop `data_file` where the historical record can be found. You can also specify the `min_data_points` required in the historical record before the check can be performed and the `period_years` for how far back in the historical record you will look.


```yaml
PercentileCheck: # test-level check that checks a result is within a certain percentile
  data_file: "C:\\Hilltop\\Data\\Archive.hts"
  min_data_points: 15
  period_years: 25
  "pH": # Hilltop measurement name
    critical: 15,85
    warning: 20,80
```

## Testing checks

These checks are for plugin testing purposes.

### TestCheck

This will add a QA check record to every run. Once only.

```yaml
TestCheck:
  disabled: false
```

### NoisyCheck

This has a 50/50 chance of adding a QA check to a sample. It doesn't check for previous QA checks so it has a 50/50 chance of adding more QA checks to the same sample if it's run repeatedly.

```yaml
NoisyCheck:
  disabled: false
```

## Adding new checks

To add a new check:

1. Create a new class that implements the `ICheck` interface and put it in the `checks` folder.
2. Add a reference to the check in `CheckRegistry` (`check_registry.py`) by adding the class name to the `run_checks`, `sample_checks`, or `test_checks` arrays.

The class will then be called and passed these parameters:

* A run, sample, or test payload, depending on the registered check level.
* The matching class configuration section from the YAML configuration file.
* The `repository`, for access to the Hilltop database in case it's needed.

## Preventing duplicate checks by checking labels

When you call `HilltopHost.Sampler.SaveQACheck()` to save a QACheck you must attach a mandatory label. This is provided back to you so you can determine if you have already reported a particular check for that context.

Run, sample, or test objects provided in the payload include a `QAChecks` attribute containing previous checks saved against that object. By checking the labels in the `QAChecks` you can see if your check has already been saved, and skip creating it again. The `ICheck` interface provides a `has_check_result()` helper method to make this easier:

```python
if self.has_check_result(context, "outside_range_check"):
    return
```

## Contributing

If you would like access to this repository for reporting issues or creating pull requests please email Hilltop support.