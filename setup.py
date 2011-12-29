# -*- encoding: utf8 -*-
from setuptools import setup, find_packages

import os

setup(
    name = "django-redisboard",
    version = "0.2.5",
    url = 'https://github.com/ionelmc/django-redisboard',
    download_url = '',
    license = 'BSD',
    description = "Brief redis monitoring in django admin",
    long_description = file(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author = 'Ionel Cristian Mărieș',
    author_email = 'contact@ionelmc.ro',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    include_package_data = True,
    install_requires = [
        'redis',
        'Django>=1.3',
    ],
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
