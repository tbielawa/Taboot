# Copyright (c) 2011 Tim Bielawa <tbielawa@redhat.com>
#
# GraphMachine is a simple class for generating graphviz code from
# strings using naming conventions like parent.Child and
# parent.OtherChild. Basically, module-prefixed python class names.
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


class GraphMachine:
    """
    This generates edges and tracks connections made
    """
    def __init__(self, taboot_classes, mapping):
        # Connections should be {parent: [child1, child2, child3]}
        self.connections = {}
        self.taboot_classes = taboot_classes
        self.mapping = mapping

    def _connected(self, parent, child):
        """
        Check if a parent has already been connected to the given child
        """
        if parent in self.connections:
            return child in self.connections[parent]
        else:
            return False

    def get_base(self, inclass):
        """
        What base group of things (module) does inclass belong to?
        """
        if "." in inclass:
            # Full-named classes give their base away, ex: command.Run is
            # a member of the command base
            return inclass.split('.')[0]

        if not inclass in self.taboot_classes:
            # This is a member of none of our bases
            return None

        for b, members in self.mapping.iteritems():
            # Look up which base it is a member of
            if inclass in members:
                return b
        return None

    def make_edge(self, parent, child):
        """
        Do the logic to determine the correct nomenclature when
        defining the relationship from parent to child. Including:
        parents-parent and parent naming verification.

        When make_edge is called the childs name will be given in
        full. This includes the base prefix, e.g., command.Run.

        TODO: Simplify this logic. There's symmetry here that could
        use used to our advantage.
        """
        parent_child = []
        if parent == 'object':
            # The simplest case.
            parent_child.append((parent, child))
        elif not "." in parent:
            # the parents name does not include a base so we will look it up
            pbase = self.get_base(parent)
            if pbase is None:
                # The parent is not native to Taboot (not found in any
                # base), so we define an edge from object to it
                # explicitly to prevent creating a forest with
                # detached digraphs.
                parent_child.append(('object', parent))
                parent_child.append((parent, child))
            else:
                # Class is a Taboot class
                p = pbase + "." + parent
                parent_child.append((p, child))
        elif not self.get_base(parent) in self.mapping:
            # Parent has a base, but the base is not in Taboot
            parent_child.append(('object', parent))
            parent_child.append((parent, child))
        else:
            # Name includes base
            if self.get_base(parent) is None:
                # Includes base, but base isn't in Taboot
                parent_child.append(('object', parent))
                parent_child.append((parent, child))
            else:
                # Name includes base and the parent is a member of
                # that base.
                parent_child.append((parent, child))

        self._add_connections(parent_child)

    def _add_connections(self, connections):
        """
        Save discovered edges to this instance of GraphMachine
        """
        for p, c in connections:
            # Iterate over all the given parent, child tuples
            if not self._connected(p, c):
                # Check that no edge has been made between these nodes
                # yet so we don't have multiple edges going to the
                # same place.
                if not p in self.connections:
                    # Give the parent a list to hold its children if
                    # this is the parents first appearance
                    self.connections[p] = [c]
                else:
                    # Append the child to the list of sibblings if
                    # we've seen its parent before
                    self.connections[p].append(c)

    def __str__(self):
        """
        String representation of this graph in dot language
        """
        from datetime import datetime
        from random import randrange

        dt = datetime.today()
        last_generated = "// Last updated on: %s" % \
            dt.strftime("%Y-%m-%d %H:%M:%S")
        header = """digraph objectgraph {
\tfontsize=30;
\tlabel=\"Class Inheritance Graph of the entire Taboot source code.\\n\
http://fedorahosted.org/Taboot/\";"""
        defaultnode = "node [fontname=Helvetica];"
        footer = "}\n"
        edges = [last_generated, header, defaultnode]

        for parent, children in self.connections.iteritems():
            # http://www.graphviz.org/doc/info/colors.html#brewer
            color = randrange(1, 10)
            nodecolor = "\tnode [color=\"/paired10/%s\"];" % color
            edges.append(nodecolor)
            for child in children:
                edge = "\t\"%s\"->\"%s\";" % (parent, child)
                edges.append(edge)

        edges.append(footer)
        return "\n".join(edges)

    def write_graph(self, outfile="objectgraph.dot"):
        """
        Write the graph out to a file
        """
        f = open(outfile, 'w')
        f.write(str(self))
        f.flush()
        f.close()
