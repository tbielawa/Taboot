class BaseOutput(object):
    pass

class CLIOutput(BaseOutput):
    def __call__(self, task_result):
        import Colors

        c = Colors.Colors()
        if task_result.success:
            output_color = 'green'
        else:
            output_color = 'red'

        output = "%s:\n" % c.format_string(task_result.host,'blue')
        output += "Task[%s]:\n" %   c.format_string(task_result.task, output_color)
        output += "%s\n" % c.format_string(task_result.output.strip(), output_color)
        print output

