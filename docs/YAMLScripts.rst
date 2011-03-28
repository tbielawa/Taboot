YAML Scripts
============

This page should provide a basic overview of YAML syntax and a
complete overview of the allowed items in a proper `poseidon` YAML
script.

YAML Basics
-----------

For `poseidon`, every YAML script must be a list at it's root-most
element. Each item in the list is a dictionary. These dictionaries
represent all the options you can use to write a `poseidon` script.

In YAML a list can be represented in two ways. In one way all members
of a list are lines beginning at the same indentation level starting
with a '-' character::

    # A list of tasty fruits
    - Apple
    - Orange
    - Strawberry
    - Mango

In the second way a list is represented as comma separated elements
surrounded by square brackets. Newlines are permitted between
elements::

    # A list of tasty fruits
    [apple, orange, bananna, mango]

A dictionary is represented in a simple `key:` and `value` form::

    # An employee record
    name: John Eckersberg
    job: Developer
    skill: Elite

Like lists, dictionaries can be represented in an abbreviated form::

    # An employee record
    {name: John Eckersberg, job: Developer, skill: Elite}

That's all you really need to know about YAML to get started writing
`poseidon` scripts.


Elements of a Poseidon script
-----------------------------

A script can specify the following keys:

* hosts
* concurrency
* output
* tasks

Each of these keys and their respective arguments is described in the
following sections.


Hosts
^^^^^

* Required: Yes
* Argument type: List
* Default: None

The `hosts` key is used to describe the target hosts for the script to
act on. The `hosts` key takes a list of hosts as input. Optionally you
can specify hosts as shell-like globs::

    hosts:
      - www01.web.ext.example.com
      - www02.web.ext.example.com
      - www03.web.ext.example.com

To operate on all the www* named hosts in the web subdomain you could
simplify the above list into this single shell-like glob::

    hosts:
      - www*.web.ext.example.com

Or even shorter::

    hosts: [www*.web.ext.example.com]


Concurrency
^^^^^^^^^^^

* Required: No (has default)
* Argument type: Integer
* Default: 1

`concurrency` lets you specify the number of hosts this script can
operate on at once. This is great if you need to perform rolling
restarts or updates. In those cases you can omit this key, as the
default value is 1::

    concurrency: 5


Output
^^^^^^

* Required: No (has default)
* Argument type: List
* Default: CLIOutput

`poseidon` has multiple output methods available to the user. Default
it only prints to `stdout`. The next sections describe all of the
available output methods in greater detail.

CLIOutput
*********

* API: :class:`poseidon.output.CLIOutput`

This is the default output method. If you only want command line
printing then it can be omitted::

    output:
       - CLIOutput


LogOutput
*********

* API: :class:`poseidon.output.LogOutput`

`poseidon` can log a session to file with the `LogOutput` method if
requested. This has a default configured to log to a file called
`poseidon.log` which is configurable via the `logfile` keyword
argument.

Example using `CLIOutput` and `LogOutput` using a special log file::

    output:
       - CLIOutput
       - LogOutput:
           logfile: example.log


EmailOutput
***********

* API: :class:`poseidon.output.EmailOutput`

Finally, `poseidon` can go out of it's way and email you results when
a script has finished running::

    output:
       - EmailOutput:
           to_addr: releases@example.com
	   from_addr: engineer@example.com


Tasks
^^^^^

* Required: Yes
* Argument type: List
* Default: None

The `tasks` key defines the tasks will be performed on each host in
`hosts`. The syntax of each possible tasks varries. All of the tasks
are documented in the following section.


Tasks
-----

All the tasks need to be documented here. I'd much rather write their
documentation files in a tasks subdirectory and link to them from
here. 
