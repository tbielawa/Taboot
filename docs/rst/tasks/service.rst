Service
^^^^^^^

* API: :class:`taboot.tasks.service`
* Classes

  * Start
  * Stop
  * Restart

The ``service`` module provides interface classes to the system
`service` command.


Start
*****

* API: :class:`taboot.tasks.service.Start`
* Keys

  * ``service``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: The service to start

Syntax::

    ---
      tasks:
        # Normal form
        - service.Start:
	    service: service-to-start

	# Abbreviated form
        - service.Start: {service: service-to-start}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - service.Start: {service: httpd}

Stop
****

* API: :class:`taboot.tasks.service.Stop`
* Keys

  * ``service``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: The service to stop

Syntax::

    ---
      tasks:
        # Normal form
        - service.Stop:
	    service: service-to-stop

	# Abbreviated form
        - service.Stop: {service: service-to-stop}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - service.Stop: {command: httpd}

Restart
*******

* API: :class:`taboot.tasks.service.Restart`
* Keys

  * ``service``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: The service to restart

Syntax::

    ---
      tasks:
        # Normal form
        - service.Restart:
	    service: service-to-restart

	# Abbreviated form
        - service.Restart: {service: service-to-restart}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - service.Restart: {command: httpd}

