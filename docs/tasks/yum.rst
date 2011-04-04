Yum
^^^

* API: :class:`taboot.tasks.yum`
* Classes

  * Install
  * Remove
  * Update

The ``yum`` module lets you perform common tasks right in your
`Taboot` scripts.


Install
*******

* API: :class:`taboot.tasks.yum.Install`
* Keys

  * ``packages``

    * Type: List of strings
    * Default: None
    * Required: Yes
    * Description: Names of the packages to install


Syntax::

    ---
      tasks:
        # Normal form
        - yum.Install:
	    packages:
	        - package-name

	# Abbreviated form
        - yum.Install: {packages: [package-name]}


Example 1::

    ---
    - hosts:
        - www*
      tasks:
        - yum.Install: {packages: [httpd, php5, screen]}


Example 2::

    ---
    - hosts:
        - www*
      tasks:
        - yum.Install:
	    packages:
	        - httpd
		- php5
		- screen


Remove
******

* API: :class:`taboot.tasks.yum.Remove`
* Keys

  * ``packages``

    * Type: List of strings
    * Default: None
    * Required: Yes
    * Description: Names of packages to remove


Syntax::

    ---
      tasks:
        # Normal form
        - yum.Remove:
	    packages:
	        - package-name

	# Abbreviated form
        - yum.Remove: {packages: [package-name]}


Example 1::

    ---
    - hosts:
        - www*
      tasks:
        - yum.Remove: {packages: [httpd, php5, screen]}


Example 2::

    ---
    - hosts:
        - www*
      tasks:
        - yum.Remove:
	    packages:
	        - httpd
		- php5
		- screen


Update
******

* API: :class:`taboot.tasks.yum.Update`
* Keys

  * ``packages``

    * Type: List of strings
    * Default: Update all packages
    * Required: No (has default)
    * Description: Names of packages to update


Syntax::

    ---
      tasks:
        # Normal form
        - yum.Update:
	    packages:
	        - package-name

	# Abbreviated form
        - yum.Update: {packages: [package-name]}


Example 1::

    ---
    - hosts:
        - www*
      tasks:
        - yum.Update: {packages: [httpd, php5, screen]}


Example 2::

    ---
    - hosts:
        - www*
      tasks:
        - yum.Update:
	    packages:
	        - httpd
		- php5
		- screen
