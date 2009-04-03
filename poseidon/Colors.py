# Copyright 2009, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Colorizing functions and objects.
"""


class Colors(object):
    """
    Simple terminal colors object.
    """

    def __init__(self):
        """
        Creates the Colors object.

        @param self: Internal Colors object.
        @type self: Colors
        """
        self.colors = {}
        self.colors['normal'] = '\033[0;00m'
        self.colors['red'] = '\033[1;31m'
        self.colors['green'] = '\033[01;32m'
        self.colors['yellow'] = '\033[01;33m'
        self.colors['blue'] = '\033[01;34m'
        self.colors['white'] = '\033[01;37m'

    def format_string(self, text, color, normalize=True):
        """
        Returns a color formatted string.

        @param self: Internal Colors object.
        @type self: Colors

        @param text: The text to print.
        @type text: str

        @param color: String representation of color.
        @type color: str

        @param normalize: If the string should end in normal color.
        @type normalize: bool

        @return: Color formatted string.
        @rtype: str
        """
        if not self.does_color_exist(color):
            raise(Exception("Color %s doesn't exist." % color))
        end_str = ""
        if normalize:
            end_str = self.colors['normal']
        return "%s%s%s" % (self.colors[color], text, end_str)

    def does_color_exist(self, color):
        """
        Returns a color formatted string.

        @param self: Internal Colors object.
        @type self: Colors

        @param color: String representation of color.
        @type color: str

        @return: True if the color exists, False otherwise.
        @rtype: bool
        """
        if color.lower() in self.colors:
            return True
        return False
