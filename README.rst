=============================
    django-redisboard
=============================


Brief redis monitoring in django admin

Installation guide
==================

Add ``redisboard`` to ``INSTALLED_APPS``::

    INSTALLED_APPS += ("redisboard", )

After that you need to run::

    manage.py syncdb

Or if you use south you can migrate this app::

    manage.py migrate redisboard


Then you can add redis servers in the admin. You will see the stats in the changelist.

Screenshots
===========

Changelist:

.. image:: https://github.com/downloads/ionelmc/django-redisboard/screenshot.png

Inspect page:

.. image:: https://github.com/downloads/ionelmc/django-redisboard/redisboard-inspect.png
