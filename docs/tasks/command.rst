Command
^^^^^^^

* Default: None
* Argument Type: String
* Null Argument Allowed: No
* API: :class:`taboot.tasks.command.Run`

The ``command`` task is used to execute arbitrary commands on a remote
host. The syntax of the argument is just a string that is the command
to execute.

Example::


    - hosts
        - www*
    - tasks
        - type: command.Run
	  args: rm -fR /

Example 2::

    - tasks
        - type: command.Run
	  args: yum -y install python-taboot

        - type: command.Run
	  args: service funcd restart

