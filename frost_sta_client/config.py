import os


class Config(object):
    ## configure request retries
    # Total number of retries to allow. Takes precedence over other counts.
    total_retries = os.environ.get("HTTP_RETRY_TOTAL", 20) 
    # How many connection-related errors to retry on.
    connect = os.environ.get("HTTP_RETRY_CONNECT", 15) 
    # A backoff factor to apply between attempts after the second try
    backoff_factor = os.environ.get("HTTP_RETRY_BACKOFF_FACTOR", 0.3) 
    # A set of integer HTTP status codes that we should force a retry on
    status_forcelist = os.environ.get("HTTP_RETRY_STATUS_FORCELIST", [500, 502, 503, 504]) 
    ## Enable HTTP_AUTH
    HTTP_AUTH = os.environ.get("HTTP_AUTH") or False
    if HTTP_AUTH:
        HTTP_AUTH_USER = os.environ.get("HTTP_AUTH_USER") 
        HTTP_AUTH_PASSWORD = os.environ.get("HTTP_AUTH_PASSWORD")
   