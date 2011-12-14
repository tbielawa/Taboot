.. _hosts:

Hosts
^^^^^

* Required: Yes
* Argument type: List
* Default: None

The ``hosts`` key is used to describe the target hosts for the script to
act on. The ``hosts`` key takes a list of hosts as input. Optionally you
can specify hosts as shell-like globs::

    hosts:
      - www01.web.ext.example.com
      - www02.web.ext.example.com
      - www03.web.ext.example.com

To operate on all the www* named hosts in the web subdomain you could
simplify the above list into this single shell-like glob::

    hosts:
      - www*.web.ext.example.com

Or even shorter::

    hosts: [www*.web.ext.example.com]

