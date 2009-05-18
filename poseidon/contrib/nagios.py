import urllib2
import urllib

#there's a python egg for this, but it was easier for me to just throw
#it in the src dir
from urllib2_kerberos import HTTPKerberosAuthHandler


class Nagios:
    """
    A simple class to enable and disable machines in Nagios.
    """

    #some constants that map to things Nagios expects to get in the POST.
    #A full list is in the Nagios source, in include/common.h
    NAGIOS_DISABLE = '29'
    NAGIOS_ENABLE = '28'
    NAGIOS_ADD_COMMENT = '1'
    NAGIOS_DELETE_ALL_COMMENTS = '20'

    def __init__(self, nagios_instance='http://monitor.mgmt.stage.redhat.com' +
                                       '/nagios/cgi-bin/cmd.cgi'):
        """
        You need a Kerberos ticket before running this. I'm not going
        to pass passwords over HTTP.
        """

        self.nagios_instance = nagios_instance
        opener = urllib2.build_opener(HTTPKerberosAuthHandler())
        urllib2.install_opener(opener)

    def disable_alerts(self, host):
        self._call_nagios_alerts(host, Nagios.NAGIOS_DISABLE)

    def enable_alerts(self, host):
        self._call_nagios_alerts(host, Nagios.NAGIOS_ENABLE)

    def add_comment(self, host, comment):
        self._call_nagios_comment(host, comment, Nagios.NAGIOS_ADD_COMMENT)

    def delete_all_comments(self, host):
        self._call_nagios_comment(host, '', Nagios.NAGIOS_DELETE_ALL_COMMENTS)

    def _call_nagios_alerts(self, host, command):
        """
        build up the POST call for an enable or disable. Example of
        what nagios expects to get:

        cmd_typ=29&cmd_mod=2&host=xmlserver1.app.stage.redhat.com&
        btnSubmit=Commit

        XXX: need to combine with other call methods
        """

        opts = {}
        opts['host'] = host
        opts['cmd_typ'] = command
        opts['cmd_mod'] = '2'
        opts['btnSubmit']='Commit'
        try:
            response = urllib2.urlopen(self.nagios_instance,
                                       urllib.urlencode(opts))
        except:
            print "Failed call to Nagios for " + host
            raise

    def _call_nagios_comment(self, host, comment, command):
        """
        build up the POST call for a host comment. Example of what
        nagios expects to get:

        cmd_typ=1&cmd_mod=2&host=app02.web.stage.ext.phx2.redhat.com&
        persistent=on&com_data=test+post&btnSubmit=Commit

        XXX: need to combine with other call methods
        """

        opts = {}
        opts['host'] = host
        opts['cmd_typ'] = command
        opts['cmd_mod'] = '2'
        opts['btnSubmit']='Commit'
        opts['persistent']='on'
        opts['com_data'] = comment
        try:
            response = urllib2.urlopen(self.nagios_instance,
                                       urllib.urlencode(opts))
        except:
            print "Failed call to Nagios for " + host
            raise

    def _call_nagios_delete_all_comments(self, host, command):
        """
        build up the POST call for a host comment. Example of what
        nagios expects to get:

        cmd_typ=20&cmd_mod=2&host=app02.web.stage.ext.phx2.redhat.com&
        btnSubmit=Commit

        XXX: need to combine with other call methods
        """
        opts = {}
        opts['host'] = host
        opts['cmd_typ'] = command
        opts['cmd_mod'] = '2'
        opts['btnSubmit']='Commit'
        opts['persistent']='on'
        try:
            response = urllib2.urlopen(self.nagios_instance,
                                       urllib.urlencode(opts))
        except:
            print "Failed call to Nagios for " + host
            raise
