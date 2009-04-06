#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks.command

r = poseidon.runner.Runner(hostglobs=['minion', 'overlord'],
                           tasks=[poseidon.tasks.command.Run('date'),
                                  poseidon.tasks.command.Run('uptime'),
                                  poseidon.tasks.command.Run('hostname')],
                           concurrency=2)

r.run()
