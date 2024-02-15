import os


class Config(object):
    ## Enable HTTP_AUTH
    HTTP_AUTH = os.environ.get("HTTP_AUTH") or False
    if HTTP_AUTH:
        HTTP_AUTH_USER = os.environ.get("HTTP_AUTH_USER") 
        HTTP_AUTH_PASSWORD = os.environ.get("HTTP_AUTH_PASSWORD")
   