def set_auth_cookies(response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Changed for local dev testing
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Changed for local dev testing
        samesite="lax"
    )

def clear_auth_cookies(response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
