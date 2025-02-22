# third party libraries
import apache_beam as beam
import requests
import yaml
from bs4 import BeautifulSoup


def parse_beam_transforms():
    """Parse Beam YAML documentation page and return dictionary of transforms and their usage.

    Returns:
        dict: Dictionary where keys are transform names and values are usage strings
    """
    url = f"https://beam.apache.org/releases/yamldoc/{beam.__version__}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    transforms = {}
    transforms["UNKNOWN"] = "Usage not found."

    # Find all transform headings (h2 with id)
    for h2 in soup.find_all("h2", id=True):
        transform_name = h2.text.strip()

        # Find the next usage example
        usage_block = None
        next_sibling = h2.find_next_sibling()
        while next_sibling and not usage_block:
            if next_sibling.name == "div" and "codehilite" in next_sibling.get("class", []):
                usage_block = next_sibling.find("pre")
            next_sibling = next_sibling.find_next_sibling()

        if usage_block:
            transforms[transform_name] = usage_block.text.strip()

    return transforms


def extract_config_from_yaml(yaml_str):
    """Extract only the configuration part from a YAML string.

    Args:
        yaml_str (str): YAML string to parse

    Returns:
        str: Configuration string or empty string if parsing fails
    """
    try:
        data = yaml.safe_load(yaml_str)
        if isinstance(data, dict) and "config" in data:
            return yaml.dump(data["config"], default_flow_style=False, indent=2, sort_keys=False)
        return ""
    except yaml.YAMLError:
        return ""


BEAM_YAML_TRANSFORMS = parse_beam_transforms()

# Create a dictionary of transform configurations
BEAM_YAML_TRANSFORMS_CONFIG = {
    name: extract_config_from_yaml(transform) if name != "UNKNOWN" else "Usage not found."
    for name, transform in BEAM_YAML_TRANSFORMS.items()
}
