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
required. Func is the system over which Taboot executes all of it's
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
our fictitious domain: ``friendfrobber.com``. When complete it will
demonstrate:

* Using `globbing` to select hosts
* Operating on multiple hosts at once
* Advanced logging techniques
* Use of the preflight element
* Scheduling downtime in Nagios
* Updating packages via Yum
* Showing a summary of all changed RPMs


The FriendFrobber.com Infrastructure
````````````````````````````````````

    **MegaFrobber**: `Reach out and Frob some one!` ™

You are a sysadmin for `FriendFrobber.com`, makers of the wildly
popular social networking service `MegaFrobber`. As such, you are
responsible for maintaining the application servers in their
high-availability web cluster. Part of that responsibility includes
releasing updates to the server component of `MegaFrobber`. These are
your hosts:

* ``www01.ext.friendfrobber.com``
* ``www02.ext.friendfrobber.com``
* ``www11.ext.friendfrobber.com``
* ``www12.ext.friendfrobber.com``

For the sake of simplicity we're going to assume that the wizards in
networking have taken care of all the load balancing to the webserver
pool. To further simplify things, unhealthy nodes are removed from
service automatically (thanks networking!).

Also living in the `FriendFrobber.com` domain is a monitoring server
with Nagios installed. This server watches the ``wwwXX`` hosts and
pages the sysadmin team if it notices any webserver isn't responding
to requests.

* ``monitor.util.friendfrobber.com``

``monitor`` has the `Func` Nagios Server plugin installed so that
downtime can be handled remotely.

Finally there is your administration center:

* ``overlord.util.friendfrobber.com``

``overlord`` is the command center on which you store and run your
Taboot scripts.

.. seealso::

   * `Nagios <http://www.nagios.com>`_ - `The Industry Standard in IT Infrastructure Monitoring`


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

The data of the ``hosts`` element is a list. Each item in the list is
a hostname, or a glob that can be expanded into a hostname. When
Taboot executes your script it will iterate over each host represented
in this list.

.. versionchanged:: 0.4.0
   Prior to this version the order that hosts appeared in this list
   was not guaranteed to be representative of the actual order of
   execution.

   From version 0.4.0 onward Taboot implements **strict ordering** and
   (except for expanded globs) guarantees that the order of execution
   will match the order of definition.

The ``concurrency`` element specifies how many hosts Taboot will run a
script against at a single time. You can specify this as an integer or
``all`` to run against all hosts at once.

The ``output`` element allows you to mix and match exactly which
logging mechanisms to process the scripts output with.

The ``preflight`` and ``tasks`` elements define sequences of actions
to perform for each host. The ``preflight`` sequence is ran at maximum
concurrency before the main ``tasks`` body is executed. When
completed, script execution prompts for input before continuing.

These sequences are composed of items called `tasks`. Each task
represents an action or step to be repeated for each host. These
actions are things like restarting a service, deleting files,
installing packages, or disabling a member in a load balancing pool.

Some tasks, like ``service.Restart``, take arguments which are
represented as hashes or "key-value pairs" in YAML. Some tasks, like
``puppet.Run`` require no arguments at all. Other may have arguments
that are entirely optional.


.. seealso::

   * :ref:`Taboot Tasks stdlib <tasks>`
   * `Puppet <http://puppetlabs.com/>`_ - System Configuration Management


Updating Just One Host (Part 1)
```````````````````````````````

Lets start simple and do a yum update on one webserver,
``www01.ext.friendfrobber.com``. In the ``hosts`` element we specify a
list with just one item (our web server) and in our ``tasks`` element
we use ``command.Run`` to call yum::


    # www01-yum-update.yaml
    ---
    - hosts: [www01.ext.friendfrobber.com]
      tasks:
        - command.Run:
	    command: yum -y update


That is the entire script. Run it like this::

    $ taboot www01-yum-update.yaml

When it runs you might notice a long delay before anything
happens. That will happen when a command takes a long time to run, as
the output only updates once a task finishes.

.. seealso::

   * :ref:`hosts` - Complete ``hosts`` documentation
   * :ref:`command` - Complete ``command.Run`` task documentation


Output
++++++

You should see a screen similar to this when it finishes::


    [root@overlord.util.friendfrobber.com ~]# taboot www01-yum-update.yaml
    www01.ext.friendfrobber.com:
    2011-12-13 17:32:38 Starting Task[taboot.tasks.command.Run('yum update -y ',)]
    www01.ext.friendfrobber.com:
    2011-12-13 17:36:11 Finished Task[taboot.tasks.command.Run('yum update -y ',)]:
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


Updating Just One Host (Part 2)
```````````````````````````````

But wait, there's more! Because yum commands are used frequently we
made a couple of tasks to make using yum simpler:

* ``yum.Install``
* ``yum.Update``
* ``yum.Remove``

Here's the last example again, but written using the ``yum.Update``
task::

    # www01-yum-update.yaml
    ---
    - hosts: [www01.ext.friendfrobber.com]
      tasks:
        - yum.Update

.. seealso::

   * :ref:`yum` - Complete ``yum`` task documentation


RPM Pre/Post Manifest
`````````````````````

Two more bundled tasks are the RPM ``PreManifest`` and
``PostManifest`` tasks. The ``PostManifest`` task is used (in
conjunction with the ``PreManifest`` task) to show you a summary of
the changes to your installed packages. This is especially useful for
verification in systems where an update should only upgrade/install
specific packages::

    # package-install.yaml
    ---
    - hosts: [www0*]
      tasks:
        - rpm.PreManifest

        - yum.Remove: {packages: [docbook-style-xsl]}
        - yum.Install: {packages: [puppet, python-netaddr]}

        - rpm.PostManifest

.. seealso::

   * :ref:`rpm` - Complete ``rpm`` task documentation
   * :ref:`examplepostmanifest`


Updating Multiple Hosts
```````````````````````

Taboot lets you target multiple hosts in a script. We can specify
additional hosts in a few ways. We could enumerate each host::

    # www-yum-update.yaml
    ---
    - hosts: [www01.ext.friendfrobber.com,www02.ext.friendfrobber.com,www11.ext.friendfrobber.com,www12.ext.friendfrobber.com]
      tasks:
        - yum.Update

    # Again, but demonstrating the alternative YAML syntax for list items
    ---
    - hosts:
        - www01.ext.friendfrobber.com
	- www02.ext.friendfrobber.com
	- www11.ext.friendfrobber.com
	- www12.ext.friendfrobber.com
      tasks:
        - yum.Update


Or we could use `globbing`, a technique where you give part of a name
and the rest is filled in automatically::

    # www-yum-update.yaml
    ---
    - hosts: [www*.ext.friendfrobber.com]
      tasks:
        - yum.Update

.. note::

    We could simplify our glob even further by using ``www*`` for our
    glob.


.. seealso::

    * `Func Glob Documentation <https://fedorahosted.org/func/wiki/CommandLineGlobbing>`_


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
    - hosts: [www*.ext.friendfrobber.com]
      concurrency: 2
      tasks:
        - yum.Update



Via Command Line
++++++++++++++++

Additionally, concurrency may be specified or overridden via command
line with the ``-C`` parameter::

    $ taboot -C 2 www-yum-update.yaml


Conncurrencies "Gotcha"
+++++++++++++++++++++++

One "gotcha" when running with ``concurrency`` > 1 is that logs are
not guaranteed to maintain any logical ordering. This is because we
have multiple threads of execution happening in parallel. In this
situation there will be tasks entering and exiting at different times
based on when they originally started and how long they took to run.

The result is, for example, the log the messages for a script running
on ``www01`` becoming interleaved with the logs for a script running
on ``www02`` at the same time.


Additional Logging Techniques
`````````````````````````````

By default Taboot just prints progress on your console. This
``output`` type is called ``CLIOutput``. Some other types available
for formatting results are:

* ``LogOutput`` - Logs to a plain text file
* ``HTMLOutput`` - Creates a colored HTML file with anchors

You aren't limited to just one! Taboot can log to multiple logging
systems at the same time.

.. seealso::

   * :ref:`output` - Complete ``output`` documentation


Logging To a Text File
++++++++++++++++++++++

Logging to a text file is another thing that can be controlled from
the command line at run-time. To add text file logging at run-time you
can use the :option:`-L` option. The default file name is formatted with a
timestamp (``taboot-YYYY-MM-DD-HHMMSS.log``).

It's called in one of two ways:

#. By itself (uses default ``LOGFILE`` value) ::

    $ taboot -L www-frobnicate.yaml

#. With the ``LOGFILE`` option ::

    $ taboot -L megafrobber.log www-frobnicate.yaml


Logging to HTML
+++++++++++++++

``HTMLOutput`` is another available logging mechanism. Unlike the
``LogOutput`` type, ``HTMLOutput`` does not support any command line
options. However, it does have a system available for saving its
configuration in a configuration file.


``HTMLOutput`` is formatted using colors. Each task result is
formatted with an HTML anchor, allowing you to directly link to that
result.

Some tasks are ``HTMLOutput`` aware and will produce enhanced output
with extra styling. For example the ``rpm.PostManifest`` task will
color deletions in red and additions in green. ``puppet.Run`` will
colorize messages by severity. For instance, **err** messages are red,
**warning** messages are yellow, and **info** messages are in
green. ::

    # www-yum-update.yaml
    ---
    - hosts: [www*.ext.friendfrobber.com]
      output:
        - CLIOutput
	- HTMLOutput
      tasks:
        - yum.Update

.. important::

   Keep in mind that if you define the ``output`` element in your
   Taboot script then you must specify **every** logging mechanism you
   want to use. That includes defining the ``CLIOutput`` type!


.. seealso::

   * :ref:`html-output` - Complete ``HTMLOutput`` documentation
   * Source code for :py:meth:`taboot.output.HTMLOutput._write`
   * :download:`Example HTMLOutput <exampleoutput/htmloutput.html>`

Complete Example
----------------

.. note::

   This final section will combine everything described above into a
   realistic example suitable for the real world. It will also
   introduce the ``nagios`` task.

The ``preflight`` element allows you to execute a set of tasks against
all of the nodes concurrently. Before execution continues into the
main ``tasks`` body you are prompted to continue. This is especially
useful for giving you time to run or finish any preparation steps that
are required before you start running a script.

We can use the massive concurrency of the ``preflight`` element to
quickly schedule downtime for all our hosts. This will save us a lot
of time that we otherwise would have spent setting this by hand. While
that happens we can upload and verify the new `MegaFrobber` package is
available on our Yum repository.

    `It's Friday again, that means that the engineers at
    friendfrobber.com have their weekly update ready. As sysadmin it's
    your job to deploy that to the cluster without causing any down
    time.`

    `The engineers have told you that this release requires running
    the megafrobber "frob-db" command after the update is installed on
    each machine.`

    `In the past you may have done this step by hand, but time has
    gone by and treated your company well. To meet increasing demands
    your cluster has had to grow from a measley 4 machines to a full
    rack of 40.`

    `The probability of you making it to the Friday IT meetup at
    Foobar's Pub is starting to look pretty grim.`

::

    # www-rolling-update.yaml
    ---
    - hosts: [www*.ext.friendfrobber.com]
      output:
        - HTMLOutput:
	    destdir: /var/www/html/logs/
	    logfile: megafrobber-%s.html
	- CLIOutput

      preflight:
        - nagios.ScheduleDowntime:
            nagios_url: monitor.util.friendfrobber.com
            minutes: 10
            service: http

      tasks:
        - rpm.PreManifest

	- service.Stop: {service: httpd}
	- service.Stop: {service: megafrobber}

	- yum.Update: {packages: [megafrobber]}

	# This megafrobber release requires updating the
	# local database.
	- command.Run: {command: megafrobber --frob-db}

	- service.Start: {service: megafrobber}
	- service.Start: {service: httpd}

	- rpm.PostManifest


Lets highlight what's happening here:

#. We're using a glob in the ``hosts`` element to target all (40) of
   our web servers.

#. Using ``HTMLOutput`` we're going to create a log file we can view
   from the web browser of our phone. The ``%s`` string is replaced
   with a datestamp in the file that is created.

#. Our ``preflight`` sets 10 minutes of `downtime` so we do not get
   paged by Nagios if it detects a server is offline in that time.

#. After the preflight finishes all execution stops and we are
   prompted to continue::

    Pre-Flight complete, press enter to continue:

#. At this point we update our Yum repository with the new package
   from engineering.

#. A manifest of installed RPMs is taken on the target node.

#. The `Apache httpd` and `megafrobber` services are stopped.

#. We use yum to update the `megafrobber` package.

#. We make a system call and run the command ``megafrobber --frob-db``

#. `Apache httpd` and `megafrobber` services are started again.

#. A manifest of the installed RPMs is taken and the diff is displayed
   against the manifest from the ``PreManifest`` so we can verify our
   intended changes landed.

As usual, engineering got the release to you with 30 minutes left in
the day. Looks like we just might make it though.

To speed up the release a bit we'll set the ``concurrency`` element to
4 at run-time. If we do 4 hosts at once we'll be done real fast. With
``HTMLOutput`` we'll be able to monitor the situation from the web
browser on our phone at the pub if we have to take off before the
script finishes running. ::

    $ taboot -C4 www-rolling-update.yaml

.. seealso::

   * :ref:`nagios` - Complete ``nagios`` task documentation
   * :ref:`puppet` - Complete ``puppet`` task documentation


More Command Line Features
--------------------------

The ``taboot`` command offers additional features not described above.

.. option:: -p, --printonly
.. option:: -n, --checkonly

   The :option:`-n` and :option:`-p` options are very similar. The
   former loads a script and does basic syntax validation. The latter
   also validates, as well as prints out the optimized YAML.

   The :option:`-n` and :option:`-p` options occur late in the parsing
   sequence. Therefore they both are able to validate the result of
   any edits made with :option:`-E` or with :option:`-L`.

   Taboots document validation catches and identifies:

   * `YAML parsing errors`
   * `Missing required elements`
   * `Tasks that can not be located`

.. note::

   Despite it's best attempts, the YAML library used in Taboot isn't
   always 100% accurate in **describing** what or where illegal syntax
   appears in YAML parsing errors. These are not false positives, you
   just need to look around the area the error is described.

.. option:: -E, --edit

   :option:`-E` opens an editor and lets you make quick one-off edits
   to a script. Great if you need to make a temporary change without
   having to first make a copy of the source script.


.. option:: -L [LOGFILE], --logfile [LOGFILE]

   Adds ``LogOutput`` to the ``output`` element. The default file name
   is formatted with a timestamp
   (``taboot-YYYY-MM-DD-HHMMSS.log``). You can specify an alternative
   log file name by specifying ``LOGFILE`` after giving the
   :option:`-L` flag.


.. option:: -s, --skippreflight

   The :option:`-s` option allows you to skip all ``preflight``
   elements.


.. option:: -o, --onlypreflight

   The :option:`-o` option allows you only run ``preflight`` elements.


.. option:: -C [CONCURRENCY], --concurrency [CONCURRENCY]

   Allows you to change the concurrency at run-time. Give the
   :option:`-C` option followed by the desired level of concurrency
   (as an integer or ``all``).


.. seealso::

   * :ref:`man` - The :manpage:`taboot(1)` man page. For
     quick-reference there is also a :manpage:`taboot-tasks(5)` man
     page which describes the syntax and provides examples of each
     built-in task as well as the different ``output`` types.
