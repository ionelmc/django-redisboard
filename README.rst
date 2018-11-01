========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/django-redisboard/badge/?style=flat
    :target: https://readthedocs.org/projects/django-redisboard
    :alt: Documentation Status


.. |travis| image:: https://travis-ci.org/ionelmc/django-redisboard.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/django-redisboard

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ionelmc/django-redisboard?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/django-redisboard

.. |requires| image:: https://requires.io/github/ionelmc/django-redisboard/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ionelmc/django-redisboard/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/ionelmc/django-redisboard/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/django-redisboard

.. |codecov| image:: https://codecov.io/github/ionelmc/django-redisboard/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/ionelmc/django-redisboard

.. |version| image:: https://img.shields.io/pypi/v/django-redisboard.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/django-redisboard

.. |commits-since| image:: https://img.shields.io/github/commits-since/ionelmc/django-redisboard/v4.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ionelmc/django-redisboard/compare/v4.0.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-redisboard.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/django-redisboard

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/django-redisboard.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/django-redisboard

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/django-redisboard.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/django-redisboard


.. end-badges

Redis monitoring and inspection drop-in application using django admin.

* Free software: BSD 2-Clause License

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
:Packages: Django>=1.8, py-redis>=2.10.0

Don't have a django project?
============================

If you just want to run redisboard quickly do this::

    pip install django-redisboard
    redisboard

Don't want to run on 0.0.0.0:8000? Run::

    redisboard ip:port

Want a password that ain't random (you might need to ``rm -rf ~/.redisboard`` first tho)? Run::

    redisboard --password=foobar

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

    manage.py migrate

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

https://django-redisboard.readthedocs.org/en/latest/

Development
===========

To run the all tests run::

    tox
