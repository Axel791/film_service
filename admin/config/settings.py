import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sncde)$(mu1j($wy%w4p^1%#0qspl@eah1f3g7-orz&i^b2)&m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG")

ALLOWED_HOSTS = ['*']


# Application definition
include(
    'components/app_settings.py'
)

# Database
include(
    'components/database.py',
)

# Password validation
include(
    'components/auth.py'
)

# Internationalization
include(
    'components/internationalization.py'
)

# Static files (CSS, JavaScript, Images)
include(
    'components/statick.py'
)

# logging

include(
    'components/logging.py'
)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
