=============================
    django-redisboard
=============================

.. image:: https://badge.fury.io/py/django-redisboard.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/django-redisboard

Redis monitoring and inspection drop-in application using django admin.

Features
========

* Sever statistics in the admin changelist
* Key summary in the inspect view
* Value introspection with pagination for lists and sorted sets

Requirements
============

:OS: Any
:Runtime: Python 2.6, 2.7 or PyPy
:Services: Redis 2.2 or later.
:Packages: Django>=1.3, py-redis

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

.. code-block:: python

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
details colum. Eg, to only show uptime and list of active databases:

.. code-block:: python

    REDISBOARD_DETAIL_FILTERS = ['uptime.*', 'db.*']

To show all the details just use:

.. code-block:: python

    REDISBOARD_DETAIL_FILTERS = ['.*']

REDISBOARD_ITEMS_PER_PAGE
-------------------------

REDISBOARD_ITEMS_PER_PAGE - default 100. Used for paginating the items from a list or a sorted set.

Screenshots
===========

Changelist:

.. image:: https://github.com/downloads/ionelmc/django-redisboard/screenshot.png

Inspect page:

.. image:: https://github.com/downloads/ionelmc/django-redisboard/redisboard-inspect.png
