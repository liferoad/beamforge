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

    # Find all transform category headings
    for h2 in soup.find_all("h2"):
        # Skip non-transform sections
        if not h2.text.lower().endswith("transforms"):
            continue

        # Process each transform in this category
        current = h2.find_next_sibling()
        while current and current.name != "h2":
            if current.name == "h3":
                # This is a transform definition
                transform_name = current.text.strip()
                # Get the usage example from the next pre block
                usage_block = current.find_next("pre")
                if usage_block:
                    transforms[transform_name] = usage_block.text.strip()
            current = current.find_next_sibling()

    return transforms
