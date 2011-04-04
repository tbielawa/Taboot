AJP
^^^

* API: :class:`taboot.tasks.mod_jk`
* Classes

  * InRotation
  * OutOfRotation

The ``AJP`` module provides a uniform way to put nodes into and out of
rotation in a `mod_jk` AJP balancer. This module is a great
replacement for manually adding and removing nodes in a `jkmanage`
management panel.

.. note::

   This module requires that the ``taboot-func`` package is installed
   on the target AJP balancers.

.. note::

   This module is very specific to the original authors needs and may
   not work outside of that environment without customization.

.. seealso::

   `The Apache Tomcat Connector - LoadBalancer HowTo <http://tomcat.apache.org/connectors-doc/generic_howto/loadbalancers.html>`_
       Documentation on the Apache Tomcat Connector


InRotation
**********

* API: :class:`taboot.tasks.mod_jk.InRotation`
* Keys

  * `proxies`

    * Type: List of strings
    * Default: None
    * Required: Yes
    * Description: List of AJP proxy hostnames

The ``InRotation`` class puts an AJP node back into rotation.

Syntax::

    ---
      tasks:
        - mod_jk.InRotation:
	    proxies:
	        - proxy-hostname


Example::

    ---
    - hosts:
        - tomcat*.int.company.com
      tasks:
        - mod_jk.InRotation:
	    proxies:
                - proxyjava01.web.prod.ext.example.com
                - proxyjava02.web.prod.ext.example.com


OutOfRotation
*************

* API: :class:`taboot.tasks.mod_jk.OutOfRotation`
* Keys

  * `proxies`

    * Type: List of strings
    * Default: None
    * Required: Yes
    * Description: List of AJP proxy hostnames

The ``OutOfRotation`` class takes an AJP node out of rotation.

Syntax::

    ---
      tasks:
        - mod_jk.OutOfRotation:
	    proxies:
	        - proxy-hostname


Example::

    ---
    - hosts:
        - tomcat*.int.company.com
      tasks:
        - mod_jk.OutOfRotation:
	    proxies:
                - proxyjava01.web.prod.ext.example.com
                - proxyjava02.web.prod.ext.example.com

