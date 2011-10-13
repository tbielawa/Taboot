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
    * Default: taboot-%s.html
    * Required: No, has default
    * Description: Name of file to log to.
    * Special: The string ``%s`` is replaced with a datestamp

  * ``destdir``

    * Type: String
    * Default: Present working directory
    * Required: No, has default
    * Description: Name of directory to save log file in.
    * Special: This directory path (including parents) will be created
      if it does not exist


Special to the ``HTMLOutput`` option is the ability to save the
defaults for ``logfile`` and ``destdir`` to a configuration file,
``~/.taboot.conf``. ``HTMLOutput`` will substitute the string ``%s``
for a datestamp (format ``YYYY-MM-DD-HHMMSS``) if used in the
``logfile`` keyword. This works in release scripts and in the
configuration file.


Keywords defined in the yaml file override all other places they are
set. Next, keywords set in ``~/.taboot.conf`` override the method
defaults. Finally, if not set in the yaml file or the config file then
the default is used (if available).


Config File Syntax::

  [HTMLOutput]
  destdir=/var/www/html
  logfile=taboot.html


Config File Using Date Substitution::

  [HTMLOutput]
  destdir=/var/www/html
  # Here '%s' expands to YYYY-MM-DD-HHMMSS
  logfile=hack-check-%s.html


HTMLOutput Syntax::

  ---
    output:
      - HTMLOutput:
          logfile: taboot.log

Abbreviated form::

  ---
    output: [HTMLOutput: {logfile: taboot.html, destdir: /var/www/html}]

.. versionadded:: 0.3.2



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
