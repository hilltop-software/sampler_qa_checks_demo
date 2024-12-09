import yaml
import os
import HilltopHost


class ConfigLoader:

    @staticmethod
    def load():
        config_section = HilltopHost.System.GetConfigSection("sampler_qa_checks_demo")
        if not config_section:
            raise ValueError("sampler_qa_checks_demo configuration section not found")
        config_file_path = config_section.get("ConfigFilePath")
        if config_file_path is None:
            raise ValueError("ConfigFilePath configuration item not found")
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"configuration file not found: {config_file_path}")

        with open(config_file_path, "r") as file:
            config = yaml.safe_load(file)
        return config
