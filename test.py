#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks.command
import poseidon.tasks.mod_jk

r = poseidon.runner.Runner(hostglobs=['*'],
                           tasks=[poseidon.tasks.command.Run('service httpd restart')],
                           concurrency=2)

r.run()
