Preflight
^^^^^^^^^

* Required: No
* Argument type: List
* Default: None

The ``preflight`` key defines the tasks that will be performed on each
host in ``hosts`` before the ``tasks`` body executes. The syntax of
each possible tasks varries. All of the tasks are documented in the
:ref:`tasks` section.

The preflight block is executed concurrently against all `hosts`
given. When the ``preflight`` block finishes `Taboot` will pause and
wait for confirmation before continuing.

.. versionadded:: 0.2.7
