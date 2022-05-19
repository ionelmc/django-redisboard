========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/django-redisboard/badge/?style=flat
    :target: https://django-redisboard.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/ionelmc/django-redisboard/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/ionelmc/django-redisboard/actions

.. |requires| image:: https://requires.io/github/ionelmc/django-redisboard/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ionelmc/django-redisboard/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/ionelmc/django-redisboard/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/django-redisboard

.. |codecov| image:: https://codecov.io/gh/ionelmc/django-redisboard/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/ionelmc/django-redisboard

.. |version| image:: https://img.shields.io/pypi/v/django-redisboard.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/django-redisboard

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-redisboard.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/django-redisboard

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/django-redisboard.svg
    :alt: Supported versions
    :target: https://pypi.org/project/django-redisboard

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/django-redisboard.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/django-redisboard

.. |commits-since| image:: https://img.shields.io/github/commits-since/ionelmc/django-redisboard/v8.2.2.svg
    :alt: Commits since latest release
    :target: https://github.com/ionelmc/django-redisboard/compare/v8.2.2...master



.. end-badges

Redis monitoring and inspection drop-in application using django admin.

* Free software: BSD 2-Clause License

Features
========

* Sever statistics in the admin changelist
* Key summary in the inspect view
* Value introspection with pagination for lists and sorted sets

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

Optional Django settings
========================

======================================= ====
Setting name                            Description
======================================= ====
``REDISBOARD_CONNECTION_POOL_OPTIONS``  Extra connection options. Default: ``{}``. Example:

                                        .. sourcecode:: python

                                            REDISBOARD_CONNECTION_POOL_OPTIONS = {'socket_timeout': 60, 'socket_connect_timeout': 10}


``REDISBOARD_DECODER_CLASS``            Default: ``'redisboard.data.UTF8BackslashReplaceDecoder'``.
``REDISBOARD_DISPLAY_CLASS``            Default: ``'redisboard.data.TabularDisplay'``.
``REDISBOARD_VALUE_QUERY_CLASS``        Default: ``'redisboard.data.ValueQuery'``.
``REDISBOARD_LENGTH_QUERY_CLASS``       Default: ``'redisboard.data.LengthQuery'``.
``REDISBOARD_DETAIL_FILTERS``           A list of regular expressions to match against the keys in the server
                                        details colum. Eg, to only show uptime and list of active databases:

                                        .. sourcecode:: python

                                            REDISBOARD_DETAIL_FILTERS = ['uptime.*', 'db.*']

                                        To show all the details just use:

                                        .. sourcecode:: python

                                            REDISBOARD_DETAIL_FILTERS = ['.*']
``REDISBOARD_DETAIL_CONVERTERS``        Mapping of regexes to functions to convert those values. Checkout the sourcecode for what's
                                        available.
``REDISBOARD_SLOWLOG_NUM``              Number of slowlog entries to show. Default: ``10``.
``REDISBOARD_SCAN_COUNT``               Count used for the various scan commands. Affects pagination for key list and key details.
                                        Default: ``1000``.
``REDISBOARD_STRING_PAGINATION``        Count used just for paginating string values. Default: ``10000``
======================================= ====

Screenshots
===========

Screenshot of the changelist:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/changelist.png
    :alt: Screenshot of the changelist

Screenshot of inspecting:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect.png
    :alt: Screenshot of inspecting

Screenshot of inspecting a sorted set:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-sorted-set.jpg
    :alt: Screenshot of inspecting a sorted set

Screenshot of inspecting a db:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-db.jpg
    :alt: Screenshot of inspecting a db

Screenshot of inspecting a big string:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-big-string.jpg
    :alt: Screenshot of inspecting a big string

Screenshot of inspecting a hash:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-hash.jpg
    :alt: Screenshot of inspecting a hash

Screenshot of inspecting a hash with binary values:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-binary-hash.jpg
    :alt: Screenshot of inspecting a hash with binary values

Screenshot of inspecting a binary string:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-binary-string.jpg
    :alt: Screenshot of inspecting a binary string

Screenshot of inspecting a binary key:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-binary-key.jpg
    :alt: Screenshot of inspecting a binary key

Screenshot of inspecting a set:

.. image:: https://raw.githubusercontent.com/ionelmc/django-redisboard/master/docs/inspect-set.jpg
    :alt: Screenshot of inspecting a set

Documentation
=============

https://django-redisboard.readthedocs.org/en/latest/

Development
===========

To run the all tests run::

    tox
