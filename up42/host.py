DOMAIN = "com"


def endpoint(path: str):
    """Gets endpoint url based on its path."""
    return f"https://api.up42.{DOMAIN}{path}"


def token_endpoint():
    return f"https://auth.up42.{DOMAIN}/realms/public/protocol/openid-connect/token"
