Poller
^^^^^^

* API: :class:`taboot.tasks.poller.PollTask`
* Classes

  * PollTask


PollTask
********

This task allows you to run other tasks until they succeed, or fail a
given number of times.

* API: :class:`taboot.tasks.poller.PollTask`
* Keys

  * ``sleep_interval``

    * Type: Integer
    * Default: 5
    * Required: No (has default)
    * Description: Time to wait between each run of ``task``

  * ``max_attempts``

    * Type: Integer
    * Default: 6
    * Required: No (has default)
    * Description: Maximum number of attempts to run ``task`` before quitting or running the ``fail_task``

  * ``task``

    * Type: YAML datastructure representing any valid task
    * Default: None
    * Required: Yes
    * Description: The task to run

  * ``fail_task``

    * Type: YAML datastructure representing any valid task
    * Default: None
    * Required: No
    * Description: The task to run if ``task`` fails ``max_attempts`` times


The ``task`` argument to PollTask gets instantiated and run.  After it
completes, it will continue to run until one of two things happen:

  - ``task`` succeeds
  - ``max_attempts`` number of runs have occured

If ``task`` succeeds, then the PollTask is considered to have succceeded.

If ``max_attempts`` is reached, then ``fail_task`` is executed one time.

So in the following example, we are going to run ``/bin/false`` five
times, waiting five seconds in between each invocation.  Then we will
run ``/bin/true``, which succeeds, and causes the entire poll task to
succeed.


Example::

    ---
    - hosts: [www*]
      tasks:
        - poller.PollTask:
            sleep_interval: 5
            max_attempts: 3
            task:
                command.Run: {command: /bin/false}
	    fail_task:
	        command.Run: {command: /bin/true}
	        
