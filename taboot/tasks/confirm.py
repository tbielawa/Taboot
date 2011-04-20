# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009,2010, Red Hat, Inc.
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

from taboot.tasks import BaseTask
from taboot.dispatch import CLIDispatcher


class Ask_CLI(BaseTask):
    """
    Block on CLI Input
    """

    def __init__(self, question, dispatcher=CLIDispatcher):
        self._question = question
        BaseTask.__init__(self, dispatcher)

    def __call__(self, **kwargs):
        print "Running %s:" % self
        result = self._dispatcher.prompt(self._question)
        if result:
            print 'OK'
        else:
            print 'Not OK!'
        return result
