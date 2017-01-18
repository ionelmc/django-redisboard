
Changelog
============

3.0.2 (2017-01-19)
------------------

* Fixed UnicodeDecodeError in "redisboard/admin.py" (Issue `#15 <https://github.com/ionelmc/django-redisboard/issues/15>`_). 
  Contributed by Erik Telepovský in `#29 <https://github.com/ionelmc/django-redisboard/pull/29>`_.
* Fixed TypeError in "redisboard/admin.py". Contributed by gabn88 in `#28 <https://github.com/ionelmc/django-redisboard/pull/28>`_.

3.0.1 (2016-09-12)
------------------

* Add supportfor Django 1.10. Contributed by Vincenzo Demasi in `#26 <https://github.com/ionelmc/django-redisboard/pull/26>`_.

3.0.0 (2015-12-17)
------------------

* Drop support for Django < 1.8
* Add support for Django 1.9. Contributed by gabn88 in `#25 <https://github.com/ionelmc/django-redisboard/pull/25>`_.

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
