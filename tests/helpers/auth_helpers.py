def build_auth_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}"
    }