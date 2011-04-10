Install
=======


From a source distribution
--------------------------

 #. `python <http://www.python.org>`_ - The python programming language along with python-setuptools
 #. `distutils <http://docs.python.org/lib/module-distutils.html>`_ - Python building and packaging library

With these requires met you can run the install command::

    sudo make install

If you wish to install the optional documentation you'll need some
additional packages so it can be built fully:

 #. python-sphinx
 #. asciidoc
 #. libxslt

To install the documentation you can run::

    sudo make installdocs


Bonus: Uninstall
`````````````````

Uninstalling is just as easy as installing Taboot was::

    sudo make uninstall



Building RPMs from git
----------------------

Taboot uses `tito` for building RPM releases so you'll need to install
it too to build RPMs that match whaat comes from the project.

 #. tito
 #. python-devel
 #. python-sphinx
 #. asciidoc
 #. libxslt

The easiest way to cut an rpm with is with the `testrelease` make
target::

    make testrelease

This will build an sdist, src.rpm, and rpm of whatever is checked into
the local branch. It's really handing for when working on new features.

To build the latest tagged release from a clone just run::

    make rpm

and look to /tmp/tito for the results.


Installing the RPMs
```````````````````

As long as the package requirements have been satisfied installing
RPMs is as simple as::

    sudo rpm -Uvh python-taboot-VERSION.rpm
