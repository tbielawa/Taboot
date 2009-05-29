from poseidon.tasks import command, TaskResult


class PreManifest(command.Run):
    """
    Gather list of installed RPMs.  A later invocation of :class:`PostManifest`
    is then used to output the RPMs changed during intermediate tasks.
    """

    def __init__(self, *args, **kwargs):
        super(PreManifest, self).__init__('rpm -qa | sort', **kwargs)

    def run(self, runner):
        """
        Override the default :class:`command.Run` to strip the output
        from the result because we're really not interested in the
        contents of the pre-manifest; we just want to collect it to
        compare later on with PostManifest.
        """

        result = super(PreManifest, self).run(runner)
        runner['rpm.PreManifest'] = result.output
        result.output = ''
        return result


class PostManifest(command.Run):
    """
    Gather list of installed RPMs and compare against a previously
    taken :class:`PreManifest`
    """

    from difflib import Differ as _Differ

    def __init__(self, *args, **kwargs):
        super(PostManifest, self).__init__('rpm -qa | sort', **kwargs)

    def run(self, runner):
        """
        The runner that gets passed in contains state that can be
        access via dict-like access.  PreManifest uses this to write
        to the rpm.Premanifest field.  So we'll check to make sure the
        pre-manifest is there by looking for that state.
        """
        try:
            pre_manifest = runner['rpm.PreManifest']
        except:
            return TaskResult(self, success=False,
                   output="You must use PreManifest before PostManifest")

        # ok, so now we have something to compare against so we get
        # new state...
        result = super(command.Run, self).run(runner)

        old_list = pre_manifest.splitlines(1)
        new_list = result.output.splitlines(1)

        differ = self._Differ()
        diff_output = list(differ.compare(old_list, new_list))
        diff_output = [line for line in diff_output if line[0] in ('+', '-')]

        result.output = ''.join(diff_output)

        return result
