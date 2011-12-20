#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2011, Red Hat, Inc.
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


import util

LOG_DEBUG = 3
LOG_WARN = 2
LOG_INFO = 1
LOG_ERROR = 0
LOG_LEVEL_CURRENT = 1


"""
Log levels adapted from the `Apache Commons` Logging User Guide:

http://commons.apache.org/logging/guide.html#Message%20Priorities/Levels

Each level includes all of the levels below it.

* ``Debug`` - Detailed information on the flow through the system.

* ``Warn`` - Use of deprecated APIs, poor use of API, 'almost' errors,
  other runtime situations that are undesirable or unexpected, but not
  necessarily "wrong".

* ``Info`` - Interesting runtime events (startup/shutdown). Expect
  these to be immediately visible on a console, so be conservative and
  keep to a minimum.

* ``Error`` - Severe errors that cause premature termination. This
  would rarely be seen.


Examples:

some_thing = "something"
something = "something"
thing = "thing"

log_debug("Something is broken!!!")

log_debug("%s is broken!!!!", some_thing)

log_debug("In %s there is a broken %s", something, thing)

log_debug("In %s there is a broken %s", (something, thing))

log_debug("In %s there is a broken %s", [something, thing])

"""


def log_wrap(origfunc):
    """
    DRY: Use magic instead of code to get a string for the correct log
    level when calling ``print_log_msg``.
    """
    def orig_func_wraper(msg, *args):
        log_level = origfunc.__name__.split("_")[1]

        import log
        if getattr(log, "LOG_%s" % log_level.upper()) <= log.LOG_LEVEL_CURRENT:
            # flatten the positional params so we don't tuple() a
            # tuple or an array and end up with weirdness.
            a = util.flatten(args)
            
            print_log_msg(log_level, msg % tuple(a))
    return orig_func_wraper


def print_log_msg(log_level, msg):
    for l in msg.split("\n"):
        print "%s: %s" % (log_level.upper(), l)


@log_wrap
def log_error(mgs, LOG_ERROR, *args):
    pass


@log_wrap
def log_warn(msg, LOG_WARN, *args):
    pass


@log_wrap
def log_info(msg, LOG_INFO, *args):
    pass


@log_wrap
def log_debug(msg, *args):
    pass


def _log_test():
    some_thing = "something"
    something = "something"
    thing = "thing"

    log_debug("Something is broken!!!")
    log_debug("%s is broken!!!!", some_thing)
    log_debug("In %s there is a broken %s", something, thing)
    log_debug("In %s there is a broken %s", (something, thing))
    log_debug("In %s there is a broken %s", [something, thing])


if __name__ == "__main__":
    #log_debug("test wrapped message: %s/%s", "one param", "two param")
    _log_test()
