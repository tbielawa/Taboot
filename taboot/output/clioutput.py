class CLIOutput(_FileLikeOutputObject):
    """
    Output a :class:`taboot.tasks.TaskResult` to the command line
    with pretty formatting and colors.
    """

    def _setup(self, host, task):
        """
        Implementation specific setup for outputting to the CLI.

        :Parameters:
           - `host`: name of the host
           - `task`: name of the task
        """
        import Colors
        import sys
        self._c = Colors.Colors()
        self._sys = sys
        self._sys.stdout.write('%s:\n' % (
            self._c.format_string(host, 'blue')))
        self._sys.stdout.write('%s Starting Task[%s]\n' % (
            self.timestamp, self._c.format_string(task, 'white')))

    def _write_result_header(self, result):
        """
        Implementation of writing to the CLI.

        :Parameters:
           - `result`: result object to inspect and write
        """
        import types

        # Set output color
        output_color = 'red'
        if result.success:
            output_color = 'green'

        self._sys.stdout.write("%s:\n" % (
            self._c.format_string(result.host, 'blue')))
        self._sys.stdout.write("%s Finished Task[%s]:\n" % (
            self.timestamp, self._c.format_string(
                result.task, output_color)))

    def _write(self, result):
        self._write_result_header(result)

        for line in result.format_lines(self.__class__.__name__, self._c):
            self._sys.stdout.write(line)

        self._sys.stdout.flush()
