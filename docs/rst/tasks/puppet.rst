Puppet
^^^^^^

* API: :class:`taboot.tasks.service`
* Classes

  * Start
  * Stop
  * Restart

The ``puppet`` module provides a uniform way interact with the puppet
service. This includes like enabling/disabling the daemon and manually
forcing a catalog run.


Run
***

* API: :class:`taboot.tasks.puppet.Run`
* Keys

  * `None`

The ``Run`` class triggers a manual catalog run. This is equivalent to
``puppetd --test``.


Syntax::

    ---
      tasks:
        - puppet.Run


Example::

    ---
    - hosts:
        - www*
      tasks:
        - puppet.Run


Enable
******

* API: :class:`taboot.tasks.puppet.Enable`
* Keys

  * `None`


The ``Enable`` class reverses the effect of the ``disable``
class. This removes the lockfile that prevented any automatic or
manual catalog runs from happening before. This is equivalent to
``puppetd --enable``.


Syntax::

    ---
      tasks:
        - puppet.Enable


Example::

    ---
    - hosts:
        - www*
      tasks:
        - puppet.Enable


Disable
*******

* API: :class:`taboot.tasks.puppet.Disable`
* Keys

  * `None`


The ``Disable`` class creates a lockfile that prevents puppet from
performing any manual or automatic catalog runs. This is equivalent to
``puppetd --disable``.


Syntax::

    ---
      tasks:
        - puppet.Disable


Example::

    ---
    - hosts:
        - www*
      tasks:
        - puppet.Disable

