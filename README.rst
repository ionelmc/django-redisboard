=============================
    django-redisboard
=============================

| |docs| |travis| |appveyor| |coveralls| |landscape| |scrutinizer|
| |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/django-redisboard/badge/?style=flat
    :target: https://readthedocs.org/projects/django-redisboard
    :alt: Documentation Status

.. |travis| image:: http://img.shields.io/travis/ionelmc/django-redisboard/master.png?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/django-redisboard

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ionelmc/django-redisboard?branch=master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/django-redisboard

.. |coveralls| image:: http://img.shields.io/coveralls/ionelmc/django-redisboard/master.png?style=flat
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/django-redisboard

.. |landscape| image:: https://landscape.io/github/ionelmc/django-redisboard/master/landscape.svg?style=flat
    :target: https://landscape.io/github/ionelmc/django-redisboard/master
    :alt: Code Quality Status

.. |version| image:: http://img.shields.io/pypi/v/django-redisboard.png?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/django-redisboard

.. |downloads| image:: http://img.shields.io/pypi/dm/django-redisboard.png?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/django-redisboard

.. |wheel| image:: https://pypip.in/wheel/django-redisboard/badge.png?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/django-redisboard

.. |supported-versions| image:: https://pypip.in/py_versions/django-redisboard/badge.png?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/django-redisboard

.. |supported-implementations| image:: https://pypip.in/implementation/django-redisboard/badge.png?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/django-redisboard

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/ionelmc/django-redisboard/master.png?style=flat
    :alt: Scrtinizer Status
    :target: https://scrutinizer-ci.com/g/ionelmc/django-redisboard/

Redis monitoring and inspection drop-in application using django admin.

* Free software: BSD license

Features
========

* Sever statistics in the admin changelist
* Key summary in the inspect view
* Value introspection with pagination for lists and sorted sets

Requirements
============

:OS: Any
:Runtime: Python 2.7, 3.4, 3.4 or PyPy
:Services: Redis 2.2 or later.
:Packages: Django>=1.3, py-redis>=2.10.0

Don't have a django project ?
=============================

Use the quick start script ! It will create and run a django project on 0.0.0.0:8000 with just the redisboard installed.

With curl::

    curl -L https://raw.github.com/ionelmc/django-redisboard/master/run_redisboard.py | tee run_redisboard.py | sh -e

With wget::

    wget --no-check-certificate https://raw.github.com/ionelmc/django-redisboard/master/run_redisboard.py -O - | tee run_redisboard.py | sh -e

Don't want to run on 0.0.0.0:8000 ? Run::

    ./run_redisboard.py ip:port

Installation guide
==================

Install from pypi, with pip::

    pip install django-redisboard

Or with setuptools::

    easy_install django-redisboard

Add ``redisboard`` to ``INSTALLED_APPS``:

::

    INSTALLED_APPS += ("redisboard", )

After that you need to run::

    manage.py syncdb

Or if you use south you can migrate this app::

    manage.py migrate redisboard

Then you can add redis servers in the admin. You will see the stats in the changelist.

Redisboard has few css tweaks for the pages (they are optional). If you use staticfiles just run::

    manage.py collectstatic

If you do not use django.contrib.staticfiles you must manually symlink the
site-packages/redisboard/static/redisboard dir to <your media root>/redisboard.

Optional django settings
========================

REDISBOARD_DETAIL_FILTERS
-------------------------

REDISBOARD_DETAIL_FILTERS - a list of regular expressions to match against the keys in the server
details colum. Eg, to only show uptime and list of active databases::

    REDISBOARD_DETAIL_FILTERS = ['uptime.*', 'db.*']

To show all the details just use::

    REDISBOARD_DETAIL_FILTERS = ['.*']

REDISBOARD_ITEMS_PER_PAGE
-------------------------

REDISBOARD_ITEMS_PER_PAGE - default 100. Used for paginating the items from a list or a sorted set.

REDISBOARD_SOCKET_TIMEOUT
-------------------------

REDISBOARD_SOCKET_TIMEOUT - default None. Socket operations time out after this many seconds.

REDISBOARD_SOCKET_CONNECT_TIMEOUT
---------------------------------

REDISBOARD_SOCKET_CONNECT_TIMEOUT - default None. Socket connect operation times out after this many seconds.

REDISBOARD_SOCKET_KEEPALIVE
---------------------------

REDISBOARD_SOCKET_KEEPALIVE - default None. Enables or Disables socket keepalive.

REDISBOARD_SOCKET_KEEPALIVE_OPTIONS
-----------------------------------

REDISBOARD_SOCKET_KEEPALIVE_OPTIONS - default None. Additional options for socket keepalive.


Screenshots
===========

Changelist:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/changelist.png

Inspect:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect.png

Inspect key details:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-key.png


Documentation
=============

https://django-redisboard.readthedocs.org/

Development
===========

To run the all tests run::

    tox
