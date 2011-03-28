Examples
========

Building a Job with YAML
------------------------

Most Taboot use cases can be accomplished by crafting a YAML file
and running it with the `taboot` executable.

Here is a simple example YAML which will update an RPM and restart
httpd::

    - hosts:
        - 'java0*.web.qa.*'
        - 'someotherhost'
      concurrency: 2
      tasks:
        - type: yum.Update
          args: some-rpm-package-name
        - type: service.Restart
          args: httpd

Save this to a file `myjob.yaml` and run as such::

  $ taboot myjob.yaml

or alternatively if you omit the filename, read from stdin::

  $ cat myjob.yaml | taboot

.. seealso::
   
   :doc:`YAMLScripts`
       Complete documentation of the YAML syntax `taboot` understands.

   :ref:`tasks`
       Documentation for each of the built-in tasks `taboot` provides.

YAML format
^^^^^^^^^^^

The root of the YAML document should be a list.  For each item in this
list, the taboot executable will do a little bit of work to convert
your types into actual Python objects and then pass the datastructure
as the keyword arguments to instantiate a
:class:`taboot.runner.Runner` instance and finally run the instance.
`args` when used for a task will be expanded for positional argument
expansion when creating task options.  Similarly, `kwargs` is used as
the keword arguments.

See :ref:`taboot.tasks` for details on the available tasks and
what options are available to control their behavior.

Task Examples
-------------

These are some examples of how to use specific tasks.

:class:`taboot.tasks.poller.PollTask`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    - hosts:
        - foo.example.com
      tasks:
        - type: poller.PollTask
          kwargs:
            task:
              type: command.Run
              args: /bin/false
            fail_task:
              type: command.Run
              args: /bin/true
            sleep_interval: 5
            max_attempts: 5

The `task` argument to PollTask gets instantiated and run.  After it
completes, it will continue to run until one of two things happen:

  - `task` succeeds
  - `max_attempts` number of runs have occured

If `task` succeeds, then the PollTask is considered to have succceeded.

If `max_attempts` is reached, then `fail_task` is executed one time.

So in the above instance, we are going to run '/bin/false' five times,
waiting five seconds in between each invocation.  Then we will run
/bin/true, which succeeds, and causes the entire poll task to succeed.

Note that if you're particularly insane you could nest PollTasks like
this::

    - hosts:
        - foo.example.com
      tasks:
        - type: poller.PollTask
          kwargs:
            task:
              type: poller.PollTask
              kwargs:
                task:
                  type: command.Run
                  args: /bin/false
                fail_task:
                  type: command.Run
                  args: echo "also fail!" && /bin/false
                max_attempts: 1
            fail_task:
              type: command.Run
              args: /bin/true
            sleep_interval: 5
            max_attempts: 5


API Examples
------------

Simple
^^^^^^

A script that simply queries the hostname and uptime of all hosts
available to the func overlord.  ::

    #!/usr/bin/env python

    import taboot.runner
    from taboot.tasks.command import Run

    r = taboot.runner.Runner(hosts=['*'],
                               tasks=[{'type': Run, 'args': 'hostname'},
                                      {'type': Run, 'args': 'uptime'}])
    r.run()


Advanced
^^^^^^^^

A more involved example that does a rolling upgrade of a JBoss
cluster.
::


    #!/usr/bin/env python

    import taboot.runner
    import taboot.tasks.yum as yum
    import taboot.tasks.service as service
    import taboot.tasks.puppet as puppet
    import taboot.tasks.poller as poller
    import taboot.tasks.command as command
    import taboot.output as output

    r = taboot.runner.Runner(hosts=['java0*.web.qa.*'],

                               tasks=[{'type': puppet.Disable},

                                      {'type': service.Stop,
                                       'args': 'jbossas'},

                                      {'type': command.Run,
                                       'args': 'rm -f /var/log/jbossas/production/server.log'},

                                      {'type': yum.Update,
                                       'args': 'jbossas'},

                                      {'type': puppet.Enable},

                                      {'type': puppet.Run},

                                      {'type': service.Start,
                                       'args': 'jbossas'}],

                                output=[{'type': output.CLIOutput},

                                        {'type': output.LogOutput,
                                         'args': 'myfile.log'}],

                                concurrency=2
                                )

    r.run()

There's a few interesting things to note here.

  * We set concurrency=2 so that two hosts will operate in parallel.

  * We explicitly set the runner's output option so that we get output
    to both the CLI and to the logfile myfile.log.
