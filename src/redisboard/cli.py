'''
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mredisboard` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``redisboard.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``redisboard.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration


'''
from __future__ import print_function

import argparse
import os
import random
import string

parser = argparse.ArgumentParser(description='Runs redisboard in an ad-hoc django project.')
parser.add_argument('--password', '-p',
                    help='The admin password. A random one will be generated if not provided.')
parser.add_argument('--storage', '-s', default=os.path.expanduser('~/.redisboard'),
                    help='Where to save the SECRET_KEY and sqlite database. (default: %(default)s)')
parser.add_argument('addrport', nargs='?', default='0:8000',
                    help='Optional port number, or ipaddr:port (default: %(default)s)')

DJANGO_SETTINGS = dict(
    REDISBOARD_SOCKET_CONNECT_TIMEOUT=5,
    REDISBOARD_SOCKET_TIMEOUT=5,
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    INSTALLED_APPS=(
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'redisboard',
    ),
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }],
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    ROOT_URLCONF=__name__,
    STATIC_URL='/static/',
    ALLOWED_HOSTS=['*'],
    LOGGING={
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s | %(name)s - %(message)s',
                'datefmt': '%d/%b/%Y %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            '': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            },
        }
    },
)


def get_random(length=50, chars='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'):
    return ''.join(
        random.SystemRandom().choice(chars)
        for _ in range(length)
    )


def main(args=None):
    args = parser.parse_args(args=args)
    if not os.path.exists(args.storage):
        os.mkdir(args.storage)
    secret_key_path = os.path.join(args.storage, 'SECRET_KEY')
    if os.path.exists(secret_key_path):
        with open(secret_key_path) as fh:
            secret_key = fh.read()
    else:
        secret_key = get_random()
        with open(secret_key_path, 'w') as fh:
            fh.write(secret_key)
    database_path = os.path.join(args.storage, 'db.sqlite')

    import django
    from django.conf import settings
    from django.conf.urls import url
    from django.contrib import admin
    from django.core.management import execute_from_command_line

    settings.configure(
        SECRET_KEY=secret_key,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': database_path
            }
        },
        **DJANGO_SETTINGS
    )

    django.setup()

    global urlpatterns
    urlpatterns = [
        url(r'', admin.site.urls),
    ]

    from django.contrib.auth.models import User
    from redisboard.models import RedisServer

    if not os.path.exists(database_path):
        execute_from_command_line(['django-admin', 'migrate', '--noinput'])

        user = User.objects.create(username='redisboard', is_superuser=True, is_staff=True, is_active=True)
        pwd = get_random(8, string.digits + string.ascii_letters) if args.password is None else args.password
        user.set_password(pwd)
        user.save()
        print()
        print('=' * 80)
        print('''
    Credentials:

        USERNAME: redisboard
        PASSWORD: %s

    ''' % (pwd if args.password is None else '<PROVIDED VIA --password OPTION>'))
        print('=' * 80)
        print()

        RedisServer.objects.create(label='localhost', hostname='127.0.0.1')

    execute_from_command_line(['django-admin', 'runserver', '--insecure', '--noreload', args.addrport])
