.. _rpm:

RPM
^^^

* API: :class:`taboot.tasks.rpm`
* Classes

  * PreManifest
  * PostManifest

The ``RPM`` module provides two utility classes used to create a log
of any RPMs installed on the target system that were changed during
the `Taboot` run.


PreManifest
***********

* API: :class:`taboot.tasks.rpm.PreManifest`
* Keys

  * `None`


The ``PreManifest`` class is best ran at the beginning of a tasks
block. When ran it saves the output of ``rpm -qa | sort`` on each of
the target machine locally. This is only useful if the
``PostManifest`` class is called at the end of the `Taboot` script.


Syntax::

    ---
      tasks:
        - rpm.PreManifest

Example::

    ---
    - hosts:
        - www*
      tasks:
        - rpm.PreManifest
	- puppet.Run
	- rpm.PostManifest


PostManifest
************

* API: :class:`taboot.tasks.rpm.PostManifest`
* Keys

  * `None`


The ``PostManifest`` class is best ran at the end of a tasks
block. When ran it will show a diff of the packages installed between
when ``PreManifest`` was ran and when ``PostManifest`` is called.

This is really useful for checking that planned updates are happening
in a `Taboot` script if they are supposed to be. There might be
package updates happening if you're doing a manual puppet catalog run,
or are triggering some other kind of automatic package updating
utility. Maybe your script is as simple as a ``PreManifest``, then a
``command.Run`` that just runs `yum -y update`, and ends with a
``PostManifest``.

Syntax::

    ---
      tasks:
        - rpm.PostManifest

Example::

    ---
    - hosts:
        - www*
      tasks:
        - rpm.PreManifest
	- puppet.Run
	- rpm.PostManifest


.. _examplepostmanifest:

Example PostManifest Output
***************************

These classes might be described best by showing a complete example.

Here is the YAML file (``mercurial-update.yaml``) that's going to be
run::

    ---
    - hosts:
        - fridge
      tasks:
        - rpm.PreManifest
        - yum.Update: {packages: [mercurial]}
        - rpm.PostManifest


This is what the output looks like. The last two lines show the
packages that changed during the `Taboot` run::


    [root@fridge yamls]# taboot mercurial-update.yaml
    fridge.bsb.local:
    2011-04-04 21:04:09 Starting Task[taboot.tasks.rpm.PreManifest('rpm -qa | sort',)]
    fridge.bsb.local:
    2011-04-04 21:04:12 Finished Task[taboot.tasks.rpm.PreManifest('rpm -qa | sort',)]:

    fridge.bsb.local:
    2011-04-04 21:04:12 Starting Task[taboot.tasks.yum.Update('yum update -y mercurial',)]
    fridge.bsb.local:
    2011-04-04 21:04:34 Finished Task[taboot.tasks.yum.Update('yum update -y mercurial',)]:

    # yum.Update output here...

    fridge.bsb.local:
    2011-04-04 21:04:34 Starting Task[taboot.tasks.rpm.PostManifest('rpm -qa | sort',)]
    fridge.bsb.local:
    2011-04-04 21:04:37 Finished Task[taboot.tasks.rpm.PostManifest('rpm -qa | sort',)]:
    - mercurial-1.7.5-1.fc14.x86_64
    + mercurial-1.8.1-2.fc14.x86_64
