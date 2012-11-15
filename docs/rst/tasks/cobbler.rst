.. _cobbler:

Cobbler
^^^^^^^

* API: :class:`taboot.tasks.cobbler`
* Classes

  * EnableNetboot
  * DisableNetboot
  * Sync

The ``cobbler`` module provides a uniform way interact with the cobbler
service.

EnableNetboot
*************

* API: :class:`taboot.tasks.cobbler.EnableNetboot`
* Keys

  * ``cobbler_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the cobbler server.

  * ``sync``

    * Type: Boolean
    * Default: ``False``
    * Required: No
    * Description: Run "cobbler sync" right after edit or not.


Syntax::

    ---
      tasks:
        # Normal form
        - cobbler.EnableNetboot:
            cobbler_url: cobbler-hostname

        # Abbreviated form
        - cobbler.EnableNetboot: {cobbler_url: cobbler-hostname}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - cobbler.EnableNetboot: {cobbler_url: cobbler.example.com}


DisableNetboot
**************

* API: :class:`taboot.tasks.cobbler.DisableNetboot`
* Keys

  * ``cobbler_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the cobbler server.

  * ``sync``

    * Type: Boolean
    * Default: ``False``
    * Required: No
    * Description: Run "cobbler sync" right after edit or not.


Syntax::

    ---
      tasks:
        # Normal form
        - cobbler.DisableNetboot:
            cobbler_url: cobbler-hostname

        # Abbreviated form
        - cobbler.DisableNetboot: {cobbler_url: cobbler-hostname}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - cobbler.DisableNetboot: {cobbler_url: cobbler.example.com}


Sync
****

* API: :class:`taboot.tasks.cobbler.Sync`
* Keys

  * ``cobbler_url``

    * Type: String
    * Default: None
    * Required: Yes
    * Description: Hostname of the cobbler server.

This class runs ``cobbler sync`` command.


Syntax::

    ---
      tasks:
        # Normal form
        - cobbler.Sync:
            cobbler_url: cobbler-hostname

        # Abbreviated form
        - cobbler.Sync: {cobbler_url: cobbler-hostname}


Example::

    ---
    - hosts:
        - www*
    tasks:
        - cobbler.DisableNetboot:
            cobbler_url: cobbler.example.com
    ---
    - hosts:
        - overlord.example.com
    tasks:
        - cobbler.Sync:
            cobbler_url: cobbler.example.com
