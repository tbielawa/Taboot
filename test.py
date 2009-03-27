#!/usr/bin/env python

import poseidon.runner

r = poseidon.runner.Runner(hostglobs='*',
                           tasks=['task1',
                                  'task2'],
                           concurrency=2)

r.run(dry_run=True)
