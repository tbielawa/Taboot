# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009, Red Hat, Inc.
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

from taboot.log import log_warn

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
            log_warn("Color %s doesn't exist, using default.", color)
            color = 'normal'
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


class HTMLColors(Colors):
    """
    Simple HTML string coloring object
    """

    def __init__(self):
        """
        Define the HTML color pallet
        """
        self.colors = {}
        self.colors['normal'] = '#000000'
        self.colors['red'] = '#FF0000'
        self.colors['green'] = '#008000'
        self.colors['yellow'] = '#FFFF00'
        self.colors['blue'] = '#0000FF'
        self.colors['white'] = '#FFFFFF'

    def format_string(self, text, color, normalize=True):
        """
        Returns a color formatted string.
        """
        if not self.does_color_exist(color):
            log_warn("Color %s doesn't exist, using default.", color)
            color = 'normal'
        end_str = ""
        if normalize:
            end_str = "</tt></font>"
        return "<font color='%s'><tt>%s%s" % \
            (self.colors[color], text, end_str)

    def does_color_exist(self, color):
        """
        Answer the question "do you recognize this color?"
        """
        return color.lower() in self.colors
