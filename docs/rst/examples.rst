Examples
========

Building a Job with YAML
------------------------

Most Taboot use cases can be accomplished by crafting a YAML file and
running it with the `taboot` executable.

Here is a simple example YAML which will update an RPM and restart
httpd::

    - hosts:
        - 'java0*.web.qa.*'
        - 'someotherhost'
      concurrency: 2
      tasks:
        - yum.Update: {packages: [sun-java, httpd]}
        - service.Restart: {service: httpd}

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
list, the taboot CLI will instantiate a :class:`taboot.runner.Runner`
instance and finally run the instance.

See :ref:`taboot.tasks` for details on the available tasks and what
options are available to control their behavior.

Task Examples
-------------

These are some examples of how to use specific tasks.

:class:`taboot.tasks.poller.PollTask`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    - hosts:
        - foo.example.com
      tasks:
        - poller.PollTask:
            task:
              command.Run:
                command: /bin/false
            fail_task:
              command.Run:
                command: /bin/true
            sleep_interval: 5
            max_attempts: 5

The ``task`` argument to PollTask gets instantiated and run as a
subtask.  After it completes, it will continue to run until one of two
things happen:

  - ``task`` succeeds
  - ``max_attempts`` number of runs have occurred

If ``task`` succeeds, then the PollTask is considered to have succeeded.

If ``max_attempts`` is reached, then ``fail_task`` is executed one time.

So in the above instance, we are going to run ``/bin/false`` five times,
waiting five seconds in between each invocation.  Then we will run
``/bin/true``, which succeeds, and causes the entire poll task to succeed.

Note that if you're particularly insane you could nest PollTasks like
this::

    - hosts:
        - foo.example.com
      tasks:
        - poller.PollTask:
            task:
              poller.PollTask:
                task:
                  command.Run:
                    command: /bin/false
                fail_task:
                  command.Run:
                    command: echo "also fail!" && /bin/false
                max_attempts: 1
            fail_task:
              command.Run:
                command: /bin/true
            sleep_interval: 5
            max_attempts: 5

