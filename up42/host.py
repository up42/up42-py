DOMAIN = "com"


def endpoint(path: str):
    """Gets endpoint url based on its path."""
    return f"https://api.up42.{DOMAIN}{path}"
