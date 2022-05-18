
Changelog
=========

8.2.2 (2022-05-19)
------------------

* Fix broken missing key check for databases different than the default one (usually 0) and render a full page instead of a text/plain 404.

8.2.1 (2022-05-18)
------------------

* Fixed issue with key stats being empty for databases different than the default one (usually 0). Turns out pipelines open up a new
  connection and need a select call.

8.2.0 (2022-05-17)
------------------

* Added a full details page.
* Added some headings in inspect pages.
* Fixed model name in breadcrumbs.
* Fixed empty media in inspect pages.
* Fixed inspect page giving 500 error for unavailable servers.

8.1.0 (2022-05-16)
------------------

* Added ``--version`` CLI option.
* Changed redisboard CLI admin header to show version and also fixed incorrect context that prevented AdminSite customizations overriding
  said header. Probably view site link also fixed.


8.0.1 (2022-05-15)
------------------

* Fixed incorrect settings loading of ``REDISBOARD_DETAIL_CONVERTERS``.

8.0.0 (2022-05-15)
------------------

* Dropped support for Python 3.6.
* Overhauled internals to support customization of redis queries, deserialization and display using custom classes.
  For that purpose there are new settings: ``REDISBOARD_DECODER_CLASS``, ``REDISBOARD_DISPLAY_CLASS``, ``REDISBOARD_VALUE_QUERY_CLASS`` and
  ``REDISBOARD_LENGTH_QUERY_CLASS``.
* Fixed various issues with pagination by simplifying it and making the use of cursors transparent to the user.
  For this purpose the ``sampling_size`` and ``sampling_threshold`` models fields have been removed, and the ``REDISBOARD_ITEMS_PER_PAGE``
  was removed and replaced with ``REDISBOARD_SCAN_COUNT`` and ``REDISBOARD_STRING_PAGINATION``.
* Added new setting ``REDISBOARD_DETAIL_CONVERTERS`` for customizing display of server details somewhat.
* Added new setting ``REDISBOARD_SLOWLOG_NUM`` option for limiting the slowlow displayed.
* The default value for the ``REDISBOARD_DETAIL_FILTERS`` setting was changed.
* Better connection management was implemented, both via render callbacks and ``__del__`` (as a fallback).
  There shouldn't be any connection leaks anymore. If the DEBUG setting is True then warnings
  will be issued should any connection be closed via ``__del__``.
* Added the ``--debug`` (to enable DEBUG and autoreload) and ``--decoder`` (to load a different data decoder) in the ``redisboard`` CLI.

7.0.1 (2022-05-12)
------------------

* Fixed ``--password`` killing the django session (it won't change the password and invalidate session if it's identical).
* Fixed some alignment regressions in the table cells.

7.0.0 (2022-05-12)
------------------

* Removed some of the more expensive and frankly pointless stats computations.
* Fixed internal error that occurred for empty databases.
* Cleaned up more code (hopefully all the Python 2 is all gone now).
* Changed the inspect page to include all the stats from the changelist.
* Changed the stats display to use tables instead of definition lists.
* Changed the ``--password`` CLI option to update the password regardless if the local sqlite was created or not.


6.0.0 (2022-04-12)
------------------

* Replaced the hostname/port fields with an url field.
  This allow SSL connection and whatever Redis will have in the future.
* Removed more dead code.

5.0.0 (2022-01-27)
------------------

* Drop support for old Python/Django. Minimum requirements are now Python 3.6 and Django 2.2.
* Fixed various issues with newer Django (up to 4.0):

  * Fixed various deprecations and broken imports.
  * Added a ``default_auto_field`` - fixes Django complaining about missing migrations if you have a custom ``DEFAULT_AUTO_FIELD``
    in settings.

4.1.1 (2020-07-28)
------------------

* Improved exception handling for errors coming from redis. Now timeouts show the server as "DOWN" and other errors
  don't result in a 500 page.

4.1.0 (2020-07-23)
------------------

* Fixed a KeyError that could occur on fast changing databases.
  Contributed by Rand01ph in `#39 <https://github.com/ionelmc/django-redisboard/pull/39>`_.
* Added a port filter.
  Contributed by Rick van Hattem in `#41 <https://github.com/ionelmc/django-redisboard/pull/41>`_.
* Added support for Django 3.
  Contributed by Alireza Amouzadeh in `#43 <https://github.com/ionelmc/django-redisboard/pull/43>`_.
* Fixed issues that could occur when running the ``redisboard`` CLI with newer Django
  (migrations will run now).
* Fixed ugettext deprecation.
* Added a ``favicon.ico`` and handler in the ``redisboard`` CLI.

4.0.0 (2018-11-01)
------------------

* Fixed typo in inspect.html template to reflect `out`.
* Added Django 2.0 support. Contributed by Erik Telepovský
  in `#33 <https://github.com/ionelmc/django-redisboard/pull/33>`_.
* Converted the ``run_redisboard.py`` script to a ``redisboard`` bin and fixed Django 2.x issues.
* Dropped support for Django older than 1.11.
* Dropped support for Python older than 3.4 or 2.7.
* Fixed issues with data being displayed as binary strings.
* Fixed unwanted tag escaping. Contributed by Gilles Lavaux
  in `#37 <https://github.com/ionelmc/django-redisboard/pull/37>`_.

3.0.2 (2017-01-19)
------------------

* Fixed UnicodeDecodeError in "redisboard/admin.py" (fixes
  issue `#15 <https://github.com/ionelmc/django-redisboard/issues/15>`_).
  Contributed by Erik Telepovský in `#29 <https://github.com/ionelmc/django-redisboard/pull/29>`_.
* Fixed TypeError in "redisboard/admin.py". Contributed by gabn88
  in `#28 <https://github.com/ionelmc/django-redisboard/pull/28>`_.

3.0.1 (2016-09-12)
------------------

* Add supportfor Django 1.10. Contributed by Vincenzo Demasi
  in `#26 <https://github.com/ionelmc/django-redisboard/pull/26>`_.

3.0.0 (2015-12-17)
------------------

* Drop support for Django < 1.8
* Add support for Django 1.9. Contributed by gabn88
  in `#25 <https://github.com/ionelmc/django-redisboard/pull/25>`_.

2.0.0 (2015-11-08)
------------------

* Fix error handling in couple places. Now pages don't return 500 errors if there's something bad going on with the
  redis connection.
* Remove key stats that came from ``DEBUG OBJECT`` (LRU, Address, Length etc). Now ``OBJECT
  [REFCOUNT|ENCODING|IDLETIME]`` is used instead. **BACKWARDS INCOMPATIBLE**

1.2.2 (2015-10-11)
------------------

* Exception handling for AWS ElastiCache Redis or any Redis that does not have DEBUG OBJECT command.
* Enabled Redis keys to be inspected despite not having details from DEBUG OBJECT command.

1.2.1 (2015-06-30)
------------------

* Fixed a bug on Python 3 (no ``xrange``).
* Fixed some issues the ``run_redisboard.py`` bootstrapper had with virtualenv.

1.2.0 (2015-02-21)
------------------

* Add ``REDISBOARD_SOCKET_TIMEOUT``, ``REDISBOARD_SOCKET_CONNECT_TIMEOUT``, ``REDISBOARD_SOCKET_KEEPALIVE`` and
  ``REDISBOARD_SOCKET_KEEPALIVE_OPTIONS`` options.

1.1.0 (2015-01-21)
------------------

* Fix broken slowlog display.

1.0.0 (2014-12-10)
------------------

* Show slowlog and cpu usage and more memory stats (contributed by Rick van Hattem)
* Use pipelines to send commands for faster response (contributed by Rick van Hattem)
* Added Python 3.3 and 3.4 support.
* Added a test suite and other minor fixes.

0.2.7 (?)
---------

* N/A.
