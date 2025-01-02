# third party libraries
import requests
from bs4 import BeautifulSoup


def parse_beam_transforms():
    """Parse Beam YAML documentation page and return dictionary of transforms and their usage.

    Returns:
        dict: Dictionary where keys are transform names and values are usage strings
    """
    url = "https://beam.apache.org/releases/yamldoc/2.61.0/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    transforms = {}

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
