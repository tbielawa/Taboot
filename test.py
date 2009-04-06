#!/usr/bin/env python

import poseidon.runner
import poseidon.tasks.command
import poseidon.tasks.mod_jk
import poseidon.output

r = poseidon.runner.Runner(hostglobs=['*'],
                           tasks=[poseidon.tasks.command.Run("""wc -l /var/log/messages | awk '{print $1}'""")],
                           output=[poseidon.output.CLIOutput(),
                                   poseidon.output.LogOutput(),
                                   poseidon.output.EmailOutput('jeckersb-page@redhat.com')],
                           concurrency=2)

r.run()
