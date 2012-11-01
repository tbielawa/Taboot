.. _nagios:

Nagios
^^^^^^

* API: :class:`taboot.tasks.nagios`
* Classes

  * EnableNotifications
  * DisableNotifications
  * ScheduleDowntime
  * SilenceHost
  * UnsilenceHost


The ``nagios`` task lets you handle notification and set downtime
from your Taboot scripts.

.. versionchanged:: 0.2.14
   The ``nagios`` task has switched from a CURL backend using Kerberos
   authentication to a pure Func backend. Significant changes include:

   * Previously this task specified the ``nagios_url`` key as a URL,
     it should now be given as the hostname of the Nagios server. To
     facilitate transitions we automatically correct URLs into
     hostnames. In the future the name of this key may change.

   * Previously the ``service`` key was defined as a scalar, like "HTTP"
     or "JBOSS". This version accepts that key as a scalar OR as a
     list and "does the right thing" in each case.


The host identified by the ``nagios_url`` key must be a registered
Func minion and it must have the new Func Nagios module installed. You
can download it from the Func git repo (in the func/minion/modules/
directory) if it is missing from your installation.

.. seealso::

   `Func git repo <http://git.fedorahosted.org/git/?p=func.git>`_

.. versionadded:: 0.4.3
   Added the ``service_host`` parameter for managing nagios for an alternative host.

EnableAlerts
************

* API: :class:`taboot.tasks.nagios.EnableAlerts`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the nagios server.

  * ``service_host``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Alternative host to enable alerts for.


This class enables host alerts for the current host.


Syntax::

    ---
      tasks:
        # Normal form
        - nagios.EnableAlerts:
            nagios_url: nagios-hostname

        # Abbreviated form
        - nagios.EnableAlerts: {nagios_url: nagios-hostname}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.EnableAlerts: {nagios_url: nagios.example.com}


DisableAlerts
*************

* API: :class:`taboot.tasks.nagios.DisableAlerts`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the nagios server.

  * ``service_host``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Alternative host to disable alerts for.


This class disables host alerts for the current host.


Syntax::

    ---
      tasks:
        # Normal form
        - nagios.DisableAlerts:
            nagios_url: nagios-hostname

        # Abbreviated form
        - nagios.DisableAlerts: {nagios_url: nagios-hostname}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.DisableAlerts: {nagios_url: nagios.example.com}


ScheduleDowntime
****************

* API: :class:`taboot.tasks.nagios.ScheduleDowntime`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the nagios server.

  * ``service``

    * Type: String or List
    * Default: ``HOST``
    * Required: No (has default)
    * Description: The name of the service(s) to be scheduled for downtime. Use the value ``HOST`` by itself to schedule host downtime.

  * ``minutes``

    * Type: Integer
    * Default: 30
    * Required: No (has default)
    * Description: The number of minutes to schedule downtime for.

  * ``service_host``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Alternative host to schedule downtime for.


.. versionchanged:: 0.2.14
   Default for the ``minutes`` key changed from 15 to 30 minutes.


Syntax::

    ---
      tasks:
        # Normal form
        - nagios.ScheduleDowntime:
            nagios_url: nagios-hostname
            service: service-to-schedule
            minutes: length-of-downtime

        # Abbreviated form
        - nagios.ScheduleDowntime: {nagios_url: nagios-hostname, service: service-to-schedule, minutes: length-of-downtime}


Example #1::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.ScheduleDowntime:
            nagios_url: nagios.example.com
            service: httpd
            minutes: 60

Example #2::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.ScheduleDowntime:
            nagios_url: nagios.example.com
            service: [httpd, git, XMLRPC]
            minutes: 60



SilenceHost
***********

* API: :class:`taboot.tasks.nagios.SilenceHost`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the nagios server.

  * ``service_host``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Alternative host to silence.



This class disables all host and service notifications for the current
host.


Syntax::

    ---
      tasks:
        # Normal form
        - nagios.SilenceHost:
            nagios_url: nagios-hostname

        # Abbreviated form
        - nagios.SilenceHost: {nagios_url: nagios-hostname}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.SilenceHost: {nagios_url: nagios.example.com}


.. versionadded:: 0.3.2


UnsilenceHost
*************

* API: :class:`taboot.tasks.nagios.UnsilenceHost`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the nagios server.

  * ``service_host``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Alternative host unsilence.

This class enables all host and service notifications for the current
host.


Syntax::

    ---
      tasks:
        # Normal form
        - nagios.UnsilenceHost:
            nagios_url: nagios-hostname

        # Abbreviated form
        - nagios.UnsilenceHost: {nagios_url: nagios-hostname}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.UnsilenceHost: {nagios_url: nagios.example.com}


.. versionadded:: 0.3.2
