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
with a ``-`` character::

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

A dictionary is represented in a simple ``key:`` and ``value`` form::

    # An employee record
    name: John Eckersberg
    job: Developer
    skill: Elite

Like lists, dictionaries can be represented in an abbreviated form::

    # An employee record
    {name: John Eckersberg, job: Developer, skill: Elite}

That's all you really need to know about YAML to get started writing
`poseidon` scripts.

.. seealso::

   `YAMLLint <http://yamllint.com/>`_
       YAML Lint gets the lint out of your YAML


Elements of a Poseidon script
-----------------------------

A script can specify the following keys:

* hosts
* concurrency
* output
* tasks

Each of these keys and their respective arguments is described in the
following sections.

.. include:: elements/hosts.rst
.. include:: elements/concurrency.rst
.. include:: elements/output.rst
.. include:: elements/tasks.rst


Putting it all together
-----------------------

Before we continue, lets put together everything we've seen up to
now. That will include ``hosts``, ``concurrency``, ``output``, and an
example ``task``::

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
	    
      tasks:
        - type: service.Restart
	  args: httpd


.. _tasks:

Tasks
-----

All the built-in tasks are documented here. 

.. include:: tasks/command.rst
