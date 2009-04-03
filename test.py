#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks.command

r = poseidon.runner.Runner(hostglobs=['*'],
                           tasks=[poseidon.tasks.command.Run('date'),
                                  poseidon.tasks.command.Run('uptime'),
                                  poseidon.tasks.command.Run('echo foo; echo bar;'),
                                  poseidon.tasks.command.Run('hostname')],
                           concurrency=1)

r.run()
