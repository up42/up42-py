DOMAIN = "com"
REGION = "eu"

def endpoint(path: str):
    """Gets endpoint url based on its path."""
    return f"https://api.up42.{DOMAIN}{path}"


def token_endpoint():
    if REGION == "eu":
        return f"https://auth.up42.{DOMAIN}/realms/public/protocol/openid-connect/token"
    elif REGION == "sa":
        return f"https://auth.sa.up42.{DOMAIN}/realms/public/protocol/openid-connect/token"
    raise UnsupportedRegion(f"Region {REGION} is not supported")


def user_info_endpoint():
    if REGION == "eu":
        return f"https://auth.up42.{DOMAIN}/realms/public/protocol/openid-connect/userinfo"
    elif REGION == "sa":
        return f"https://auth.sa.up42.{DOMAIN}/realms/public/protocol/openid-connect/userinfo"
    raise UnsupportedRegion(f"Region {REGION} is not supported")

class UnsupportedRegion(ValueError):
    pass
