# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2012, Red Hat, Inc.
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

from taboot.tasks import BaseTask, TaskResult

"""
Let these serve as examples of how to build simple tasks.
"""


class MiscBaseTask(BaseTask):
    """
    This also does nothing. But it helps to collect common tasks
    together under a base task when generating inheritance graphs.
    """
    pass


class Noop(MiscBaseTask):
    """
    A generic task that litterally does nothing.
    """

    def run(self, *args):
        return TaskResult(self, success=True)


class Echo(MiscBaseTask):
    """
    A generic task that just echos whatever its input is.

    Override the __init__ method if you have to accept parameters in
    your task.
    """

    def __init__(self, input, **kwargs):
        """
        Every task is passed a group of keyword arguments that we
        collect into 'kwargs'.
        """
        self.input = input
        # Call our superclass with our special keyword arguments. This
        # will contain at *least* a 'host' keyword.
        super(Echo, self).__init__(**kwargs)

    def run(self, *args):
        return TaskResult(self, success=True, output=self.input)
