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
        self.colors['orange'] = '#F87217'

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
