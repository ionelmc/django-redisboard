# -*- encoding: utf8 -*-
from setuptools import setup, find_packages

import os

setup(
    name = "django-redisboard",
    version = "0.2",
    url = '',
    download_url = '',
    license = 'BSD',
    description = "",
    author = 'Ionel Cristian Mărieș',
    author_email = 'contact@ionelmc.ro',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
