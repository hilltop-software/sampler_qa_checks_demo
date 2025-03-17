import xml.etree.ElementTree as ET
import json


def dump(obj) -> str:
    if isinstance(obj, dict):
        return json.dumps(obj)
    properties = []
    for attr in dir(obj):
        if not attr.startswith('_') and hasattr(obj, attr):
            properties.append(f"{attr}={getattr(obj, attr)}")
    return json.dumps(properties)


def get_parameter_value_from_test_info(xml: str, parameter : str) -> str:
    root = ET.fromstring(xml)
    for param in root.findall(".//Parameter"):
        if param.get("Name") == parameter:
            return param.get("Value")


def truncate(x : str, length=50) -> str:
    return x[:length-3] + '...' if len(x) > length else x


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
