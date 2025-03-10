import yaml
import os
import HilltopHost


class ConfigLoader:
    """
    A class that loads the YAML configuration file for the sampler_qa_checks_demo plugin.
    """

    @staticmethod
    def load() -> dict:
        config_section = HilltopHost.System.GetConfigSection("sampler_qa_checks_demo")
        if not config_section:
            raise ValueError("sampler_qa_checks_demo configuration section not found")
        config_file_path = config_section.get("ConfigFile")
        if config_file_path is None:
            raise ValueError("ConfigFile configuration item not found")
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"configuration file not found: {config_file_path}")

        with open(config_file_path, "r") as file:
            config = yaml.safe_load(file)
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - using configuration file from {config_file_path}")
        return config
