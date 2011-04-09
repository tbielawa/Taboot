Concurrency
^^^^^^^^^^^

* Required: No (has default)
* Argument type: Integer
* Default: 1

``concurrency`` lets you specify the number of hosts this script can
operate on at once. This is great if you need to perform rolling
restarts or updates. In those cases you can omit this key, as the
default value is 1::

    concurrency: 5
