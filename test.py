#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks.command

r = poseidon.runner.Runner(hostglobs=['*'],
                           tasks=[poseidon.tasks.command.Run('date'),
                                  poseidon.tasks.command.Run('uptime'),
                                  poseidon.tasks.command.Run('hostname'),
                                  poseidon.tasks.command.Run('yum update -y')],
                           concurrency=1)

r.run()
