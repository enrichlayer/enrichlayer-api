from os import environ

_ = environ.get


BASE_URL = _("BASE_URL", "https://enrichlayer.com/api/v2")
ENRICHLAYER_API_KEY = _("ENRICHLAYER_API_KEY", "")
TIMEOUT = int(_("TIMEOUT", "90"))
MAX_RETRIES = int(_("MAX_RETRIES", "2"))
MAX_BACKOFF_SECONDS = int(_("MAX_BACKOFF_SECONDS", "60"))
MAX_WORKERS = int(_("MAX_WORKERS", "10"))
