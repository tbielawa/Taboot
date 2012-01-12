.. _misc:

Misc
^^^^

* API: :class:`taboot.tasks.misc`
* Classes

  * Noop
  * Echo

The ``misc`` module has two simple tasks in it: ``Noop`` and
``Echo``. They are primarily intended for instruction and as
placeholders while testing scripts or major code changes.


Noop
****

* API: :class:`taboot.tasks.misc.Noop`


Syntax::

    ---
      tasks:
        - misc.Noop


Example::

    ---
    - hosts:
        - www*
      tasks:
        - misc.Noop


This is a generic task that litterally does nothing.


Echo
****

* API: :class:`taboot.tasks.misc.Echo`
* Keys

  * ``input``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: String to echo back


Syntax::

    ---
      tasks:
        # Normal form
        - misc.Echo:
	    input: string

	# Abbreviated form
        - misc.Echo: {input: string}


Example 1::

    ---
    - hosts:
        - www*
      tasks:
        - misc.Echo: {input: "Taboot Rules!"}


Example 2::

    ---
    - hosts:
        - www*
      tasks:
        - misc.Echo:
	    input: "Taboot Rules!"


.. versionadded:: 0.4.0
