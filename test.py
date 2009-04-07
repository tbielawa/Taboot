#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks.command
import poseidon.tasks.mod_jk
import poseidon.output

r = poseidon.runner.Runner(hostglobs=['*'],
                           tasks=[poseidon.tasks.command.Run('yum update -y')],
                           output=[poseidon.output.CLIOutput(),
                                   poseidon.output.LogOutput(),
                                   poseidon.output.EmailOutput('jeckersb@redhat.com')],
                           concurrency=2)

r.run()
