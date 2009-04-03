class BaseOutput(object):
    pass

class CLIOutput(BaseOutput):
    def __call__(self, success, host, output):
        import Colors

        c = Colors.Colors()
        if success:
            output_color = 'green'
        else:
            output_color = 'red'

        print "%s:\n%s" % (c.format_string(host,'blue'), c.format_string(output, output_color))
