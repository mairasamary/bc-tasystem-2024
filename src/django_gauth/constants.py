GOOGLE_CLIENT_ID = "877517324643-lrrfus5tm014p1bmu4ira6vf9v8u7fr7.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
BASE_URI = 'http://127.0.0.1:8000'

GOOGLE_REDIRECT_URI = f"{BASE_URI}/oauth/google/callback"
GOOGLE_SCOPES = "https://www.googleapis.com/auth/userinfo.email"
GOOGLE_LOGIN_REDIRECT_URI = (f"https://accounts.google.com/o/oauth2/v2/auth?"
                             f"response_type={'code'}"
                             f"&scope={GOOGLE_SCOPES}"
                             f"&access_type={'offline'}"
                             f"&include_grant_scopes={'true'}"
                             #  f"&state={ "state" }"
                             f"&client_id={GOOGLE_CLIENT_ID}"
                             f"&redirect_uri={GOOGLE_REDIRECT_URI}")
