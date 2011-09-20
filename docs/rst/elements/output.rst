Output
^^^^^^

* Required: No (has default)
* Argument type: List
* Default: :ref:`cli-output`

`taboot` has multiple output methods available to the user. Default
behavior is to only print to `stdout`. The next sections describe all
of the available output methods in greater detail.

* :ref:`cli-output`
* :ref:`log-output`
* :ref:`html-output`
* :ref:`email-output`


.. _cli-output:

CLIOutput
*********

* API: :class:`taboot.output.CLIOutput`

This is the default output method. If you only want command line
printing then it can be omitted.

Syntax::

  ---
    output:
       - CLIOutput

Abbreviated form::

  ---
    output: [CLIOutput]


.. _log-output:

LogOutput
*********

* API: :class:`taboot.output.LogOutput`

`taboot` can log a session to file with the ``LogOutput`` method if
requested. This has a default configured to log to a file called
`taboot.log` which is configurable via the ``logfile`` keyword
argument.

Syntax::

  ---
    output:
      - LogOutput:
          logfile: taboot.log

Abbreviated form::

  ---
    output: [LogOutput: {logfile: taboot.log}]



.. _html-output:

HTMLOutput
**********

* API: :class:`taboot.output.HTMLOutput`

`taboot` can log a session to an HTML file with the ``HTMLOutput``
method if requested.


* Keys

  * ``logfile``

    * Type: String
    * Default: taboot.html
    * Required: No, has default
    * Description: Name of file to log to.

  * ``destdir``

    * Type: String
    * Default: Present working directory
    * Required: No, has default
    * Description: Name of directory to save log file in.


Special the ``HTMLOutput`` option is the ability to save the defaults
for ``logfile`` and ``destdir`` to a configuration file,
``~/.taboot.conf``.


Config File Syntax::

  [HTMLOutput]
  destdir=/var/www/html
  logfile=taboot.html


HTMLOutput Syntax::

  ---
    output:
      - HTMLOutput:
          logfile: taboot.log

Abbreviated form::

  ---
    output: [HTMLOutput: {logfile: taboot.html, destdir: /var/www/html}]



.. _email-output:

EmailOutput
***********

* API: :class:`taboot.output.EmailOutput`

Finally, `taboot` can go out of it's way and email you results when
a script has finished running::

  ---
    output:
      - EmailOutput:
          to_addr: releases@example.com
	  from_addr: engineer@example.com
