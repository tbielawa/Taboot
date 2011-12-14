# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2011, Red Hat, Inc.
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

import sys
from errors import TabootTaskNotFoundException


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


def instantiator(type_blob, relative_to, **kwargs):
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
    except TypeError, e:
        import pprint
        print "Unable to instantiate %s with the following arguments:"\
            % instance_type
        pprint.pprint(kwargs)
        print "Full backtrace below\n"
        raise


def log_update(msg):
    sys.stderr.write(str(msg) + "\n")
    sys.stderr.flush()
