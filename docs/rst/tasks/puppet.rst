.. _puppet:

Puppet
^^^^^^

* API: :class:`taboot.tasks.puppet`
* Classes

  * Run
  * SafeRun
  * Enable
  * Disable
  * DeleteDockfile

The ``puppet`` module provides a uniform way interact with the puppet
service. This includes like enabling/disabling the daemon and manually
forcing a catalog run.


Run
***

* API: :class:`taboot.tasks.puppet.Run`
* Keys

  * ``server``

    * Type: String
    * Default: As specified in ``/etc/puppet/puppet.conf``
    * Required: No (has default)
    * Description: Puppet Master to run against

  * ``noop``

    * Type: Boolean
    * Default: ``False``
    * Required: No (has default)
    * Description: Make this a "noop", or "dry-run"


.. note::
    See the :ref:`YAML Basics document <truthiness>` for notes on
    specifying boolean values.


The ``Run`` class triggers a manual catalog run. This is equivalent to
``puppetd --test``. This will **not** abort the release if puppet
returns with a non-zero exit code. You should check out the ``SafeRun``
class if you're paranoid about that.


Syntax::

    ---
      tasks:
        - puppet.Run

        # Run against a different puppet master
        - puppet.Run: {server: my.puppet.server}
	# No operation run
	- puppet.Run: {noop: true}

Example::

    ---
    - hosts:
        - www*
      tasks:
        - puppet.Run

    ---
    - hosts:
        - www*
      tasks:
        - puppet.Run: {noop: true, server: puppetmaster01.util.foobar.com}


.. versionchanged:: 0.2.11
   Absolutely will **not** abort the release if puppet returns
   non-zero.

.. versionchanged:: 0.4.0
   Added ``server`` and ``noop`` keys.



SafeRun
*******

* API: :class:`taboot.tasks.puppet.SafeRun`
* Keys

  * Inherited from ``puppet.Run``

The ``SafeRun`` class triggers a manual catalog run. This is
equivalent to ``puppetd --test``. This **will** abort the release if
puppet returns with a non-zero exit code on systems running puppet
2.6+. You should check out the ``Run`` class if you have reasons to
ignore possible puppet errors.


Syntax::

    ---
      tasks:
        - puppet.SafeRun

        # Run against a different puppet master
        - puppet.SafeRun: {server: my.puppet.server}


Example::

    ---
    - hosts:
        - www*
      tasks:
        - puppet.SafeRun

.. versionadded:: 0.2.11


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


DeleteLockfile
**************

* API: :class:`taboot.tasks.puppet.DeleteLockfile`
* Keys

  * `None`


The ``DeleteLockfile`` class forcibly deletes a lockfile. You
shouldn't normally need this but from time to time you may find it
necessary. Try and use the ``Enable`` class when at all possible.


Syntax::

    ---
      tasks:
        - puppet.DeleteLockfile


Example::

    ---
    - hosts:
        - www*
      tasks:
        - puppet.DeleteLockfile

