Sleep
^^^^^

* API: :class:`taboot.tasks.sleep`
* Classes

  * Seconds
  * Minutes
  * WaitOnInput


The ``sleep`` module is used to halt further task processing for a
specified period of time, or until the user presses enter (as in the case of WaitOnInput)

You might use this if you've rolled the services on a node and need to
let it build up or sync a cache before you put it back into rotation.

WaitOnInput can be used when user verification needs to be performed before proceeding on to another node.


Seconds
*******

* API: :class:`taboot.tasks.sleep.Seconds`
* Keys

  * ``seconds``

    * Type: Integer
    * Default: 60
    * Required: No (has default)
    * Description: The number of seconds to halt

Syntax::

    ---
      tasks:
        # Normal form
        - sleep.Seconds:
	    seconds: number-of-seconds

	# Abbreviated form
        - sleep.Seconds: {seconds: number-of-seconds}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - service.Restart: {service: jbossas}
        - sleep.Seconds: {seconds: 300}


Minutes
*******

* API: :class:`taboot.tasks.sleep.Minutes`
* Keys

  * ``minutes``

    * Type: Integer
    * Default: 1
    * Required: No (has default)
    * Description: The number of minutes to halt

Syntax::

    ---
      tasks:
        # Normal form
        - sleep.Minutes:
	    minutes: number-of-minutes

	# Abbreviated form
        - sleep.Minutes: {minutes: number-of-minutes}


Example::

    ---
    - hosts:
        - java*
      tasks:
        - service.Restart: {service: jbossas}
        - sleep.Minutes: {minutes: 5}


WaitOnInput
*******

* API: :class:`taboot.tasks.sleep.WaitOnInput`
* Keys

  * ``message``

    * Type: String
    * Default: "Press enter to continue\n"
    * Required: No (has default)
    * Description: The message to prompt the user with

Syntax::

    ---
      tasks:
        # Normal form
        - sleep.WaitOnInput:
	    message: message-to-prompt-user

	# Abbreviated form
        - sleep.WaitOnInput: {message: message-to-prompt-user}


Example::

    ---
    - hosts:
        - java*
      tasks:
        - service.Restart: {service: jbossas}
        - sleep.WaitOnInput

