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

import re
import taboot
import sys
import tempfile
from argparse import ArgumentParser, ArgumentTypeError
from errors import TabootTaskNotFoundException
from os.path import isfile
from taboot.log import *


def resolve_types(ds, relative_to='taboot.tasks'):
    """
    Recursively translate string representation of a type within a
    datastructure into an actual type instance.

    :Parameters:
      - `ds`: An arbitrary datastructure.  Within `ds`, if a dict key named
        `type` is encountered, the string contained there is replaced with the
        actual type named.
      - `relative_to`: The prefix which types are relative to; used during
        import.  As an example, if `relative_to`='taboot.tasks' and `ds`
        contains a `type` key `command.Run`, then the type is imported as
        `taboot.tasks.command.Run`.
    """
    __import__(relative_to)

    if isinstance(ds, list):
        result = []
        for item in ds:
            result.append(resolve_types(item, relative_to))
        return result
    elif isinstance(ds, dict):
        result = {}
        for k, v in ds.iteritems():
            if k == 'type':
                tokens = v.split('.')
                if len(tokens) == 1:
                    result[k] = getattr(sys.modules[relative_to], tokens[0])
                else:
                    pkg = "%s.%s" % (relative_to, tokens[0])
                    the_task = ".".join([pkg, tokens[1]])
                    try:
                        __import__(pkg)
                        result[k] = getattr(sys.modules[pkg], tokens[1])
                    except (AttributeError, ImportError):
                        raise TabootTaskNotFoundException(the_task)
            else:
                result[k] = resolve_types(v, relative_to)
        return result
    else:
        return ds


def instantiator(type_blob, relative_to="taboot.tasks", **kwargs):
    """
    Instantiate a type, which is defined by a type blob in the
    following format:

      - If no paremeters are required for the type, then the blob
        should be a single string describing the desired type

      - If parameters are required, then the type blob must be a
        dictionary with only one key that is a string describing
        the desired type.  The value associated with this key
        should be dictionary which maps the parameter:value pairs
        required when instantiating the type.

    Returns the instantiated object.
    """

    __import__(relative_to)

    def str2type(s):
        import sys
        tokens = s.split('.')
        if len(tokens) == 1:
            return getattr(sys.modules[relative_to], tokens[0])
        else:
            pkg = "%s.%s" % (relative_to, tokens[0])
            try:
                __import__(pkg)
                task = getattr(sys.modules[pkg], tokens[1])
            except (AttributeError, ImportError):
                missing_task = ".".join([pkg, tokens[1]])
                raise TabootTaskNotFoundException(missing_task)
            return task

    if isinstance(type_blob, basestring):
        instance_type = str2type(type_blob)
    else:
        if len(type_blob.keys()) != 1:
            raise Exception("Number of keys isn't 1")
        instance_type = str2type(type_blob.keys()[0])
        kwargs.update(type_blob[type_blob.keys()[0]])

    try:
        return instance_type(**kwargs)
    except TypeError:
        import pprint
        log_error("Unable to instantiate %s with the following arguments:",
                  instance_type)
        pprint.pprint(kwargs)
        log_error("Full backtrace below\n")
        raise


def make_blob_copy(blob):
    """
    Concat the header with the given blob to edit into a temporary
    file.

    Returns a tuple of the new file name and the location to position
    the cursor at when opening.
    """
    if isfile(taboot.edit_header):
        header = open(taboot.edit_header).read()
        offset = len(header.split("\n"))
        log_debug("Header file is %s lines long", offset)
    else:
        log_warn("Header file not found when launching Taboot edit mode!")
        log_warn("Expected to find: %s", taboot.edit_header)
        header = ""
        offset = 0

    tmpfile = tempfile.NamedTemporaryFile(suffix=".yaml",
                                          prefix="taboot-")
    header = header.replace("$TMPFILE$", tmpfile.name)
    tmpfile.write(header)
    tmpfile.write(blob)
    tmpfile.flush()
    return (tmpfile, offset)


def sync_blob_copy(tmpfile):
    """
    For backwards compatibility we copy the blob back manually to
    tmpfile. NamedTemporaryFile didn't support the 'delete' parameter
    until py2.6.
    """
    blob = open(tmpfile.name).read()
    tmpname = tmpfile.name
    tmpfile.close()  # The file is erased when close()'d
    open(tmpname, 'w').write(blob)
    return blob


def flatten(x):
    """
    Flatten an arbitrary depth nested list.
    """
    # Lifted from: http://stackoverflow.com/a/406822/263969
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def print_stderr(msg):
    sys.stderr.write(msg)
    sys.stderr.flush()


def parse_int_or_all(arg):
    """
    Custom ArgumentParser type which accept integers and 'all' as
    arguments to the `concurrency` parameter.
    """
    value = re.match(r'^((\d+)|(all))$', arg, re.IGNORECASE)
    if not value:
        raise ArgumentTypeError("'" + arg + "' is not a valid value. \
Expecting an integer or 'all'.")
    else:
        return value.group(1)
