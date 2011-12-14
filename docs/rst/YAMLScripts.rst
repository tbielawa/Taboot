YAML Scripts
============

This page provides a basic overview of correct YAML
syntax. Additionally it covers non-task specific modules that are
valid in `Taboot` scripts.

.. seealso::

   :ref:`tasks`
       The complete documentation of all included task modules

YAML Basics
-----------

For `taboot`, every YAML script must be a list at it's root-most
element. Each item in the list is a dictionary. These dictionaries
represent all the options you can use to write a `taboot` script. In
addition, all YAML files (regardless of their association with
`taboot` or not) should start with ``---``.

In YAML a list can be represented in two ways. In one way all members
of a list are lines beginning at the same indentation level starting
with a ``-`` character::

    ---
    # A list of tasty fruits
    - Apple
    - Orange
    - Strawberry
    - Mango

In the second way a list is represented as comma separated elements
surrounded by square brackets. Newlines are permitted between
elements::

    ---
    # A list of tasty fruits
    [apple, orange, banana, mango]

A dictionary is represented in a simple ``key:`` and ``value`` form::

    ---
    # An employee record
    name: John Eckersberg
    job: Developer
    skill: Elite

Like lists, dictionaries can be represented in an abbreviated form::

    ---
    # An employee record
    {name: John Eckersberg, job: Developer, skill: Elite}

Finally, you can combine these data structures::

    ---
    # An employee record
    name: John Eckersberg
    job: Developer
    skill: Elite
    foods:
        - Apple
        - Orange
        - Strawberry
        - Mango
    languages:
        ruby: Elite
	python: Elite
	dotnet: Lame

That's all you really need to know about YAML to get started writing
`Taboot` scripts.

.. seealso::

   `YAMLLint <http://yamllint.com/>`_
       YAML Lint gets the lint out of your YAML


.. _elements:

Elements of a Taboot script
---------------------------

A Taboot release script can specify the following keys:

* ``hosts``
* ``concurrency``
* ``output``
* ``preflight``
* ``tasks``

Each of these keys and their respective arguments is described in the
following sections.

.. include:: elements/hosts.rst
.. include:: elements/concurrency.rst
.. include:: elements/output.rst
.. include:: elements/preflight.rst
.. include:: elements/tasks.rst


Putting it all together
-----------------------

Before we finish, lets put together everything we've seen up to
now. That will include ``hosts``, ``concurrency``, ``output``,
``preflight``, and an example ``task``::

    ---
    - hosts:
        - ruby*.web.qa.example.com
	- www01.web.qa.example.com
	- www02.web.qa.example.com

      concurrency: 3
      
      output:
        - CLIOutput
	- LogOutput:
	    logfile: web-restarts.log
	- EmailOutput:
	    to_addr: my_boss@example.com
	    from_addr: my_email@example.com
	    
      preflight:
        - puppet.Disable

      tasks:
        - service.Restart: {service: httpd}


On three hosts at a time this `Taboot` script would restart the
`httpd` process, printing progress to the command line, logging it to
'web-restarts.log', and finish by emailing the result of the whole
task to my_boss@example.com.
