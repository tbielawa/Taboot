#!/usr/bin/env python
# Copyright (c) 2011 Tim Bielawa <tbielawa@redhat.com>
#
# dotgen is just a controller that creates the necessary input to run
# the GraphMachine, and then runs it.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import graphmachine
# Mapping tracks module->class relationships
mapping = {}
# taboot_classes tracks all classes native to taboot
taboot_classes = []
graphmachine = graphmachine.GraphMachine(taboot_classes, mapping)


def rels():
    return [f.strip().split(' ') for f in file("input").readlines()]

for edge in rels():
    base = edge.pop(0)
    name = edge.pop(0)
    fullname = base + "." + name
    if not base in mapping:
        mapping[base] = [name]
    else:
        mapping[base].append(name)
    taboot_classes.append(name)

for edge in rels():
    base = edge.pop(0)
    name = base + "." + edge.pop(0)
    for parent in edge:
        graphmachine.make_edge(parent, name)

graphmachine.write_graph()
