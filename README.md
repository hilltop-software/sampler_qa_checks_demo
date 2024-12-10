# Sampler QA Checks Plugin Demonstration

This repository provides demonstration code for runnign QA checks in Sampler as a Hilltop plugin. It requires a Hilltop Sampler installation.

For more information, read the Hilltop guide for developing Hilltop plugins.

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

The plugin will use this path to read the rest of the plugin configuration.

### YAML configuration

The YAML file is commented with descriptions of each configuration item. The structure has a global configuration section and then configuration sections named after each check that implements the `ICheck` interface. The name of the class and the name of the YAML section must match.

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

The connection is established using `Trusted_Connection=yes;` so no username or password is included.

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

## Adding new checks

To add a new check:

1. Create a new class that implements the `ICheck` interface and put it in the `checks` folder.
2. Add a reference to the check in `CheckRegistry` at `check_registry.py` and add the class name to the `run_checks`, `sample_checks`, or `test_checks` arrays.

The class will then be called and passed:

* The appropriate run, sample, or test payload.
* The matching configuration section from the YAML configuration file.
* An active `pyodbc` database connection to the Hilltop database.