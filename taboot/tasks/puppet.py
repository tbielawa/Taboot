# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2012, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from taboot.tasks import command, TaskResult
import puppet
import re


class PuppetBase(command.Run):
    """
    Base class for puppet commands
    """

    def __init__(self, pcmd, **kwargs):
        super(PuppetBase, self).__init__(pcmd, **kwargs)


class Run(PuppetBase):
    """
    Run 'puppetd --test || true'

    :Optional Parameters:
      - `server`: Puppetmaster to run against
      - `noop`: If this should be a noop run (Boolean)
      - `safe`: Abort if puppet errors (Boolean)

    See also: :py:meth:`taboot.tasks.Puppet.SafeRun`
    """

    def __init__(self, server="", noop=False, safe=False, **kwargs):
        pcmd = "puppetd --test --color=false"
        if server != "":
            pcmd += " --server=%s" % server
        if noop == True:
            pcmd += " --noop"
        if safe == False:
            # If safe is False, ignore the return code of the puppet run
            pcmd += " || true"
        super(Run, self).__init__(pcmd, **kwargs)

    def run(self, runner):
        result = super(Run, self).run(runner)
        return PuppetTaskResult(result.taskObj, result.success,
                                     result.output, result.ignore_errors)


class SafeRun(puppet.Run):
    """
    Run 'puppetd --test'.

    How is this different from Run? Simple, it will abort everything
    if puppet returns with a non-zero exit status.
    """

    def __init__(self, server="", **kwargs):
        super(SafeRun, self).__init__(server, safe=True, **kwargs)


class Enable(PuppetBase):
    """
    Run 'puppetd --enable'.
    """

    def __init__(self, **kwargs):
        super(Enable, self).__init__('puppetd --enable', **kwargs)


class Disable(PuppetBase):
    """
    Run 'puppetd --disable'.
    """

    def __init__(self, **kwargs):
        super(Disable, self).__init__('puppetd --disable', **kwargs)


class DeleteLockfile(PuppetBase):
    """
    Remove the puppet lock file.
    """

    def __init__(self, **kwargs):
        PUPPET_LOCKFILE = "/var/lib/puppet/state/puppetdlock"
        super(DeleteLockfile, self).__init__("rm -f %s" % PUPPET_LOCKFILE,
                                             **kwargs)


class PuppetTaskResult(TaskResult):
    """
    Wrapper around TaskResult to be able to differentiate in output class
    """

    def __init__(self, task, success=False, output='', ignore_errors=False):
        super(PuppetTaskResult, self).__init__(task, success, output,
                                               ignore_errors)
        self._formatters["HTMLOutput"] = PuppetHTMLOutputFormatter
        self._formatters["CLIOutput"] = PuppetCLIOutputFormatter


class PuppetHTMLOutputFormatter(object):
    def __init__(self, output, colorizer):
        import cgi
        self._output = cgi.escape(output)
        self._c = colorizer

    def _format_lines(self):
        for line in self._output.splitlines():
            if re.match('info:', line):
                htmloutput = "%s<br />\n" %\
                    self._c.format_string(line.strip(), 'normal')
            elif re.match('notice:', line):
                htmloutput = "%s<br />\n" %\
                    self._c.format_string(line.strip(), 'blue')
            elif re.match('warning:', line):
                htmloutput = "%s<br />\n" %\
                    self._c.format_string(line.strip(), 'orange')
            elif re.match('err:', line):
                htmloutput = "%s<br />\n" %\
                    self._c.format_string(line.strip(), 'red')
            else:
                htmloutput = "%s<br />\n" %\
                    self._c.format_string(line.strip(), 'green')
            yield(htmloutput)
        yield("<br /><br />\n")


class PuppetCLIOutputFormatter(object):
    def __init__(self, output, colorizer):
        self._output = output
        self._c = colorizer
        # The log level is matched by regexp
        self._log_colors = {
            r'^info:': 'green',
            r'^notice:': 'blue',
            r'^warning:': 'yellow',
            r'^err:': 'red'
            }

    def _find_color(self, line):
        for level, color in self._log_colors.iteritems():
            if re.match(level, line):
                return color
        # Log line doesn't match anything in table
        return 'normal'

    def _format_lines(self):
        for line in self._output.splitlines():
            output_color = self._find_color(line)
            clioutput = "%s\n" % self._c.format_string(line.strip(),
                                                       output_color)
            yield(clioutput)
