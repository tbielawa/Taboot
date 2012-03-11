# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009,2011, Red Hat, Inc.
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


class _FileLikeOutputObject(object):
    """
    A file-like parent class.
    """

    import exceptions
    import time as _time
    defaults = None
    starttime = None

    def __init__(self, *args, **kwargs):
        """
        Creates an instance of a file-like object.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
        import ConfigParser
        import os.path

        if _FileLikeOutputObject.defaults is None:
            if os.path.expanduser("~/.taboot.conf"):
                _FileLikeOutputObject.defaults = ConfigParser.ConfigParser()
                _FileLikeOutputObject.defaults.read(
                    os.path.expanduser("~/.taboot.conf"))

        # Only set the start time once, not for each logger instance
        if _FileLikeOutputObject.starttime is None:
            import datetime
            _FileLikeOutputObject.starttime = datetime.datetime.today()

        self._pos = 0L
        self._closed = False
        self._setup(*args, **kwargs)

    def _setup(self, *args, **kwargs):
        """
        Implementation specific setup.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
        pass

    def flush(self):
        """
        We are not buffering so we always just return None.
        """
        return None

    def read(self, *args, **kwargs):
        """
        We are an output only file-like object. Raise exception.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
        raise self.exceptions.NotImplementedError('Object for output only.')

    def tell(self):
        """
        Returns the position of the file-like object.
        """
        return self._pos

    def truncate(self, size):
        """
        We are an output only file-like object. Raise exception.

        :Parameters:
           - `size`: size to truncate to.
        """
        raise self.exceptions.NotImplementedError(
            'This does not support truncate.')

    def writelines(self, sequence):
        """
        Writes a sequence of lines.

        :Parameters:
           - `sequence`: iterable sequence of data to write.
        """
        for item in sequence:
            self.write(item)

    def write(self, item):
        """
        Writer wrapper (not rapper, beav). Simply calls _write which is
        implementation specific and updates the position.

        :Parameters:
           - `item`: the item to write.
        """
        self._write(item)
        self._pos += 1

    def _write(self, item):
        """
        Implementation of writing data.

        :Parameters:
           - `item`: the item to write.
        """
        raise self.exceptions.NotImplementedError(
            '_write must be overriden.')

    def close(self):
        """
        Close wrapper (again, not rapper, beav). Simply calls _close  which
        is implementation specific and updates the closed property.
        """
        self._close()
        self._closed = True

    def _close(self):
        """
        Implementation of closing the file-like object.
        By default nothing occurs.
        """
        pass

    # Read aliases
    readline = read
    readlines = read
    xreadlines = read
    seek = read

    # Read-only Properties
    closed = property(lambda self: self._closed)
    timestamp = property(lambda self: self._time.strftime(
            "%Y-%m-%d %H:%M:%S", self._time.localtime()))
