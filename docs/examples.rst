Examples
=========

Example 1
---------

A script that simply queries the hostname and uptime of all hosts available to the func overlord.
::

    #!/usr/bin/env python

    import poseidon.runner
    import poseidon.tasks.command as command
    import poseidon.output
    
    r = poseidon.runner.Runner(hostglobs=['*'],
                               tasks=[command.Run('hostname'),
                                      command.Run('uptime')],
                               concurrency=2)

    r.run()
