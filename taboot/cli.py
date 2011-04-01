#!/usr/bin/env python
# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import sys
import yaml
import taboot.runner

class MalformedYAML(Exception):
    pass

def resolve_types(ds, relative_to):
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
                    __import__(pkg)
                    result[k] = getattr(sys.modules[pkg], tokens[1])
            else:
                result[k] = resolve_types(v, relative_to)
        return result
    else:
        return ds

def build_runner(ds):
    """
    Build a :class:`taboot.runner.Runner` instance from the given
    datastructure.

    :Parameters:
      - `ds`: Datastructure roughly representing keyword arguments to be used
        when instantiating runner.  All types are processed through
        :function:`resolve_types` before handing off for instantiation.
    """
    ds['tasks'] = resolve_types(ds['tasks'], 'taboot.tasks')
    if 'output' in ds:
        ds['output'] = resolve_types(ds['output'], 'taboot.output')
    return taboot.runner.Runner(**ds)

def main():
    """
    Main function.
    """
    if len(sys.argv) == 2:
        blob = open(sys.argv[1]).read()
    else:
        blob = sys.stdin.read()
    try:
        ds = yaml.load(blob)
    except:
        raise MalformedYAML("Please check the validity of your YAML")

    for runner_source in ds:
        runner = build_runner(runner_source)
        if not runner.run():
            break

if __name__ == '__main__':
    main()