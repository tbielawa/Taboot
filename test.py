#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks
import poseidon.tasks.command
import poseidon.tasks.confirm

r = poseidon.runner.Runner(hostglobs=['minion',
                                      'overlord'],
                           tasks=[poseidon.tasks.BaseTask(),
                                  poseidon.tasks.command.Run('date'),
                                  poseidon.tasks.command.Run('uptime'),
                                  poseidon.tasks.confirm.Ask_CLI('Continue???'),
                                  poseidon.tasks.command.Run('echo frazzle snazzle')],
                           concurrency=2)

r.run(dry_run=True)
