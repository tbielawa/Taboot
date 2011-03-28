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
* :ref:`email-output`


.. _cli-output:

CLIOutput
*********

* API: :class:`taboot.output.CLIOutput`

This is the default output method. If you only want command line
printing then it can be omitted::

    output:
       - CLIOutput


.. _log-output:

LogOutput
*********

* API: :class:`taboot.output.LogOutput`

`taboot` can log a session to file with the ``LogOutput`` method if
requested. This has a default configured to log to a file called
`taboot.log` which is configurable via the ``logfile`` keyword
argument.

Example using ``CLIOutput`` and ``LogOutput`` using a special log file::

    output:
       - CLIOutput
       - LogOutput:
           logfile: example.log


.. _email-output:

EmailOutput
***********

* API: :class:`taboot.output.EmailOutput`

Finally, `taboot` can go out of it's way and email you results when
a script has finished running::

    output:
       - EmailOutput:
           to_addr: releases@example.com
	   from_addr: engineer@example.com
