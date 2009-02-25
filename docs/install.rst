Install
=======

Requirements
------------
 #. `python <http://www.python.org>`_ - The python programming language along with python-setuptools
 #. `distutils <http://docs.python.org/lib/module-distutils.html>`_ - Python building and packaging library

Source
------

Installing From Source
``````````````````````
- Become root (or root like) user
- :command:`./setup.py install`

RPM
---

Building An RPM
```````````````
- Edit the spec file if needed
- :command:`./setup.py sdist`
- :command:`./setup.py rpm`


Installing An RPM
`````````````````
- Become root (or a root like) user
- :command:`rpm -ivh python-poseidon*rpm`
