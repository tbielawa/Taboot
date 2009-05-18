from poseidon.tasks import command, TaskResult


class PreManifest(command.Run):
    """
    Gather list of installed RPMs
    """

    def __init__(self, *args):
        super(PreManifest, self).__init__('rpm -qa | sort')

    def run(self, runner):
        """
        Override the default :class:`command.Run` to strip the output
        from the result because we're really not interested in the
        contents of the pre-manifest; we just want to collect it to
        compare later on with PostManifest.
        """

        result = super(PreManifest, self).run(runner)
        self.manifest = result.output
        result.output = ''
        return result


class PostManifest(command.Run):
    """
    Gather list of installed RPMs and compare against a previously
    taken :class:`PreManifest`
    """

    from difflib import Differ as _Differ

    def __init__(self, *args):
        super(PostManifest, self).__init__('rpm -qa | sort')

    def run(self, runner):
        """
        This bears some pretty involved explanation...

        The runner that gets passed in contains the list of all of the
        tasks that are being run against the current host.

        Somewhere in that list, we should find an instance of
        PreManifest that has a result stored in it.  So we'll go grab
        that output and then re-take the manifest and do a diff.
        """
        pre_manifest = None
        for task in runner._tasks:
            if isinstance(task, PreManifest):
                pre_manifest = task
                break
        if not pre_manifest:
            return TaskResult(self, success=False,
                   output="You must use PreManifest before PostManifest")

        # ok, so now we have something to compare against so we get
        # new state...
        result = super(command.Run, self).run(runner)

        old_list = pre_manifest.manifest.splitlines(1)
        new_list = result.output.splitlines(1)

        differ = self._Differ()
        diff_output = list(differ.compare(old_list, new_list))
        diff_output = [line for line in diff_output if line[0] in ('+', '-')]

        result.output = ''.join(diff_output)

        return result
