# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from poseidon.tasks import BaseTask
from poseidon.dispatch import CLIDispatcher


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
