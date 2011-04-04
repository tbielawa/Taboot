Command
^^^^^^^

* API: :class:`taboot.tasks.command`
* Classes

  * Run


The ``command`` module is used to execute arbitrary commands on a
remote host. The ``command`` module has one callable class, that is
the ``Run`` class.


Run
***

* API: :class:`taboot.tasks.command.Run`
* Keys

  * ``command``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: The command to run

Syntax::

    ---
      tasks:
        # Normal form
        - command.Run:
	    command: command-to-run

	# Abbreviated form
        - command.Run: {command: command-to-run}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - command.Run: {command: yum -y install httpd}

