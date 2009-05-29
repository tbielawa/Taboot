Examples
=========

Simple
------

A script that simply queries the hostname and uptime of all hosts available to the func overlord.
::

    #!/usr/bin/env python

    import poseidon.runner
    from poseidon.tasks.command import Run

    r = poseidon.runner.Runner(hostglobs=['*'],
                               tasks=[(Run, 'hostname'),
                                      (Run, 'uptime')])
    r.run()


Advanced
--------

A more involved example that does a rolling upgrade of a JBoss
cluster.
::


    #!/usr/bin/env python

    import poseidon.runner
    import poseidon.tasks.mod_jk as mod_jk
    import poseidon.tasks.yum as yum
    import poseidon.tasks.service as service
    import poseidon.tasks.puppet as puppet
    import poseidon.tasks.poller as poller
    import poseidon.tasks.command as command
    import poseidon.output as output

    r = poseidon.runner.Runner(hostglobs=['java0*.web.qa.*'],

                               tasks=[(mod_jk.OutOfRotation, (['proxyjava01.web.qa.ext.intdev.redhat.com'])),

                                      (puppet.Disable),

                                      (service.Stop, ('jbossas')),

                                      (command.Run, ('rm -f /var/log/jbossas/production/server.log')),

                                      (yum.Update, ('jbossas')),

                                      (puppet.Enable),

                                      (puppet.Run),

                                      (service.Start, ('jbossas')),

                                      (mod_jk.InRotation, (['proxyjava01.web.qa.ext.intdev.redhat.com']))],

                                output=[(output.CLIOutput),
                                        (output.LogOutput, ('myfile.log'))],

                                concurrency=2
                                )

    r.run()

There's a few interesting things to note here.

  * We set concurrency=2 so that two hosts will operate in parallel.

  * We explicitly set the runner's output option so that we get output
    to both the CLI and to the logfile myfile.log.
