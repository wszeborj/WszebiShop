from django.core.management.utils import get_random_secret_key


import environ

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, get_random_secret_key())
)