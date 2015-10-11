
Changelog
============

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
