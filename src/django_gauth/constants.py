import os

from bcta.settings import PUBLIC_SITE_URL, SITE_HOSTNAME

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

if PUBLIC_SITE_URL:
    BASE_URI = PUBLIC_SITE_URL.rstrip("/")
else:
    base_host = SITE_HOSTNAME.strip()
    if base_host.startswith("http://") or base_host.startswith("https://"):
        BASE_URI = base_host.rstrip("/")
    else:
        BASE_URI = f"http://{base_host}"

GOOGLE_REDIRECT_URI = f"{BASE_URI}/oauth/google/callback"

GOOGLE_SCOPES = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"

# Probably should add state to this to help prevent CSRF attacks
GOOGLE_LOGIN_REDIRECT_URI = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"response_type={'code'}"
    f"&scope={GOOGLE_SCOPES}"
    f"&access_type={'offline'}"
    f"&include_grant_scopes={'true'}"
    #  f"&state={ <SESSION STATE> }"
    f"&client_id={GOOGLE_CLIENT_ID}"
    f"&redirect_uri={GOOGLE_REDIRECT_URI}"
)
