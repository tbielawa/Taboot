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


Concepts Covered
````````````````

Lets get started and write a Taboot script. This example will build up
to a script that performs a rolling update of a web server cluster in
our fictitious domain: ``foobar.com``. When complete it will
demonstrate:

* Using `globbing` to select hosts
* Operating on multiple hosts at once
* Advanced logging techniques
* Use of the preflight element
* Scheduling downtime in Nagios
* Updating packages via Yum
* Showing a summary of all changed RPMs


Hosts in foobar.com
```````````````````

Our webservers will consist of the following:

* ``www01.ext.foobar.com``
* ``www02.ext.foobar.com``
* ``www11.ext.foobar.com``
* ``www12.ext.foobar.com``

There is also a Nagios server:

* ``nagios.int.foobar.com``

On the Nagios server each webserver is monitored with an ``http``
check.


Script Elements
```````````````

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


Updating Just One Host
``````````````````````

Lets start simple and do a yum update on one webserver,
``www01.ext.foobar.com``. In the ``hosts`` element we specify a list
with just one item (our web server) and in our tasks element we use
the ``yum.Update`` task::


    # www01-yum-update.yaml
    ---
    - hosts: [www01.ext.foobar.com]
      tasks:
        - yum.Update


That is the entire script. Run it like this::

    $ taboot www01-yum-update.yaml

When it runs you might notice a long delay before anything
happens. That will happen when a command takes along time to run, as
the output only updates once a task finishes.

Output
++++++

You should see a screen similar to this when it finishes::


    [root@griddle ~]# taboot www01-yum-update.yaml
    www01.ext.foobar.com:
    2011-12-13 17:32:38 Starting Task[taboot.tasks.yum.Update('yum update -y ',)]
    www01.ext.foobar.com:
    2011-12-13 17:36:11 Finished Task[taboot.tasks.yum.Update('yum update -y ',)]:
    Loaded plugins: langpacks, presto, refresh-packagekit
    Adding en_US to language list
    Setting up Update Process
    Resolving Dependencies
    --> Running transaction check
    ---> Package lftp.x86_64 0:4.3.3-1.fc14 set to be updated
    ---> Package mock.noarch 0:1.1.18-1.fc14 set to be updated
    ---> Package parted.x86_64 0:2.3-5.fc14 set to be updated
    ---> Package tito.noarch 0:0.4.0-1.fc14 set to be updated
    ---> Package ypbind.x86_64 3:1.32-3.fc14 set to be updated
    --> Finished Dependency Resolution
    
    Dependencies Resolved
    
    ================================================================================
     Package         Arch            Version                 Repository        Size
    ================================================================================
    Updating:
     lftp            x86_64          4.3.3-1.fc14            updates          729 k
     mock            noarch          1.1.18-1.fc14           updates          181 k
     parted          x86_64          2.3-5.fc14              updates          632 k
     tito            noarch          0.4.0-1.fc14            updates          100 k
     ypbind          x86_64          3:1.32-3.fc14           updates           56 k
    
    Transaction Summary
    ================================================================================
    Upgrade       5 Package(s)
    
    Total download size: 1.7 M
    Downloading Packages:
    Setting up and reading Presto delta metadata
    Processing delta metadata
    Download delta size: 682 k
    Presto reduced the update size by 56% (from 1.5 M to 682 k).
    Package(s) data still to download: 181 k
    Running rpm_check_debug
    Running Transaction Test
    Transaction Test Succeeded
    Running Transaction
    
      Updating       : 3:ypbind-1.32-3.fc14.x86_64                             1/10
      Updating       : parted-2.3-5.fc14.x86_64                                2/10
      Updating       : lftp-4.3.3-1.fc14.x86_64                                3/10
      Updating       : tito-0.4.0-1.fc14.noarch                                4/10
      Updating       : mock-1.1.18-1.fc14.noarch                               5/10
      Cleanup        : 3:ypbind-1.32-1.fc14.x86_64                             6/10
      Cleanup        : parted-2.3-4.fc14.x86_64                                7/10
      Cleanup        : lftp-4.0.9-3.fc14.x86_64                                8/10
      Cleanup        : tito-0.3.2-1.fc14.noarch                                9/10
      Cleanup        : mock-1.1.17-1.fc14.noarch                              10/10
    
    Updated:
      lftp.x86_64 0:4.3.3-1.fc14             mock.noarch 0:1.1.18-1.fc14
      parted.x86_64 0:2.3-5.fc14             tito.noarch 0:0.4.0-1.fc14
      ypbind.x86_64 3:1.32-3.fc14
    
    Complete!


RPM Pre/Post Manifest
`````````````````````


Updating Multiple Hosts
```````````````````````

Taboot lets you target multiple hosts in a script. We can specify
additional hosts in a few ways. We could enumerate each host::

    # www-yum-update.yaml
    ---
    - hosts: [www01.ext.foobar.com,www02.ext.foobar.com,www11.ext.foobar.com,www12.ext.foobar.com]
      tasks:
        - yum.Update

Or we could use `globbing`, a technique where you give part of a name
and the rest is filled in automatically::

    # www-yum-update.yaml
    ---
    - hosts: [www*.ext.foobar.com]
      tasks:
        - yum.Update

.. note::

    We could simplify our glob even further by using ``www*`` for our
    glob.


.. seealso::

    `Func Glob Documentation <https://fedorahosted.org/func/wiki/CommandLineGlobbing>`_


Concurrency: Multiple Updates At Once
`````````````````````````````````````

Taboot lets you run scripts with different levels of
`concurrency`. Concurrency means doing multiple things at once. This
can save you time because it would mean we could run the
``yum.Update`` task on all of our web servers at the same time.

By default Taboot runs with ``concurrency`` set to ``1``. You have two
options available for setting the ``concurrency``.


Define It In Your Script
++++++++++++++++++++++++

Concurrency can be permanently set in your Taboot scripts via the
``concurrency`` element::

    # www-yum-update-concurrent.yaml
    ---
    - hosts: [www*.ext.foobar.com]
      concurrency: 2
      tasks:
        - yum.Update



Via Command Line
++++++++++++++++

Concurrency can also be specified or overridden via command line::

    $ taboot -C 2 www-yum-update.yaml


Advanced Logging Techniques
```````````````````````````


The Preflight Element
`````````````````````


Scheduling Downtime In Nagios
`````````````````````````````

