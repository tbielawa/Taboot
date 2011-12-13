Getting Started
===============

What you need
-------------

Put simply, Taboot lets you write a script of actions (:ref:`tasks`)
and execute it on multiple hosts, concurrently if you wish. The
actions come from a standard library, this ensures consistency. Taboot
ships with multiple forms of logging (:ref:`output`). A little Python
is all you need to know if you want to expand the library with your
own custom tasks.

To start using Taboot you need:

A Func Infrastructure
`````````````````````

A working `Func installation <http://fedorahosted.org/func>`_ is
requried. Func is the system over which Taboot executes all of it's
commands. It's comparable to the cell phone network you would have a
conversation over.

Setting up Func is the hardest part and coincidentally is outside of
the scope of this document. See the Func website for instructions:

.. seealso::

   `Func setup instructions <https://fedorahosted.org/func/wiki/InstallAndSetupGuide>`_


A Repetitive Task
`````````````````

Taboot is ideal for scripting a task that needs to happen over and
over again. An example of this is a software release script, or a
maintenance script for rolling updates to a cluster. 



A Working Knowledge of YAML
```````````````````````````

Taboot scripts are simple text files. They are written in format
called YAML (YAML Ain't Markup Language). YAML is whitespace
sensitive, but otherwise fairly forgiving in what you try to do with
it.

You can get away with just applying the patterns shown here when
writing your own scripts. But understanding the language semantics
goes a long way when debugging the inevitable syntax error.

.. note::

    YAML is designed as a "human-readable data serialization format",
    not a markup language. Which is to say, the language concerns
    itself with data structures (lists, strings, dictionaries, keys),
    not document description. We will describe elements of the Taboot
    syntax in the same way.

.. seealso::

   :doc:`YAMLScripts`
       Complete documentation of the YAML syntax `taboot` understands.

   :ref:`tasks`
       Documentation for each of the built-in tasks `taboot` provides.    


Writing Your First Script
-------------------------

Elements
````````

Taboot scripts are broken up into multiple sections. Each section is
called an `element` (see: :ref:`elements`).

* ``hosts``
* ``concurrency``
* ``output``
* ``preflight``
* ``tasks``

.. note::

    The only required elements are ``hosts`` and ``tasks``. The rest
    are optional or have sane defaults.

Lets get started and write a Taboot script. In this example build up
to a scrip that performs a rolling update of a web server cluster in
our fictitious domain: ``foobar.com``. When complete it will
demonstrate:

* Using `globbing` to select hosts
* Operating on multiple hosts at once
* Advanced logging techniques
* Use of the preflight element
* Scheduling downtime in Nagios
* Updating packages via Yum
* Showing a summary of all changed RPMs


Target Hosts
````````````

