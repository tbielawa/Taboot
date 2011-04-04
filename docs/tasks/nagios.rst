Nagios
^^^^^^

* API: :class:`taboot.tasks.nagios`
* Classes

  * EnableNotifications
  * DisableNotifications
  * ScheduleDowntime

The ``nagios`` module lets you handle notification and set downtime
from your Taboot scripts.

.. note::

   The ``nagios_url`` for your site is going to be something like
   `https://foo.example.com/nagios/cgi-bin/cmd.cgi`.

.. note::

   The nagios module is currently limited to Kerberos authentication
   only. Additionally, operations will silently fail if the client
   doesn't have a valid Kerberos ticket in their ticket cache.


EnableAlerts
************

* API: :class:`taboot.tasks.nagios.EnableAlerts`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Full URL to a Nagios command cgi

Syntax::

    ---
      tasks:
        # Normal form
        - nagios.EnableAlerts:
	    nagios_url: url-to-cmd.cgi

	# Abbreviated form
        - nagios.EnableAlerts: {nagios_url: url-to-cmd.cgi}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.EnableAlerts: {nagios_url: https://foo.example.com/nagios/cgi-bin/cmd.cgi}


DisableAlerts
*************

* API: :class:`taboot.tasks.nagios.DisableAlerts`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Full URL to a Nagios command cgi

Syntax::

    ---
      tasks:
        # Normal form
        - nagios.DisableAlerts:
	    nagios_url: url-to-cmd.cgi

	# Abbreviated form
        - nagios.DisableAlerts: {nagios_url: url-to-cmd.cgi}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.DisableAlerts: {nagios_url: https://foo.example.com/nagios/cgi-bin/cmd.cgi}


ScheduleDowntime
****************

* API: :class:`taboot.tasks.nagios.ScheduleDowntime`
* Keys

  * ``nagios_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Full URL to a Nagios command cgi

  * ``service``

    * Type: String
    * Default: HOST
    * Required: No (has default)
    * Description: The name of the service to be scheduled for downtime

  * ``minutes``

    * Type: Integer
    * Default: 15
    * Required: No (has default)
    * Description: The number of minutes to schedule downtime for


Syntax::

    ---
      tasks:
        # Normal form
        - nagios.ScheduleDowntime:
	    nagios_url: url-to-cmd.cgi
	    service: service-to-schedule
	    minutes: length-of-downtime

	# Abbreviated form
        - nagios.ScheduleDowntime: {nagios_url: url-to-cmd.cgi, service: service-to-schedule, minutes: length-of-downtime}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - nagios.ScheduleDowntime:
	    nagios_url: https://foo.example.com/nagios/cgi-bin/cmd.cgi
	    service: httpd
	    minutes: 60
