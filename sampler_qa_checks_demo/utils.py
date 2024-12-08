import xml.etree.ElementTree as ET

def dump_object(obj):
    properties = {attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__')}
    return properties

def get_parameter_value_from_test_info(xml, parameter):
    root = ET.fromstring(xml)
    for param in root.findall(".//Parameter"):
        if param.get("Name") == parameter:
            return param.get("Value")
    return None

def truncate(x, length=50):
    return x[:length-3] + '...' if len(x) > length else x