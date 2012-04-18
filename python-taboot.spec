# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-taboot
%define _name   taboot
Version:        0.4.1
Release:        1%{?dist}
Summary:        Client utility for scripted multi-system administration over Func

Group:          Development/Languages
License:        GPLv3+
URL:            https://fedorahosted.org/Taboot/
Source0:        http://people.redhat.com/tbielawa/taboot/releases/taboot-latest/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

Requires:       func
Requires:       PyYAML
%{?fc14:Requires: python-argparse}
%{?el5:Requires: python-argparse}
%{?el6:Requires: python-argparse}


%description
Tool for managing and executing tasks related to software releases and
system administration via customizable YAML scripts. A library of
prewritten tasks is built in so you can get started immediately.

Taboot uses Func for inter-system communication, eliminating hacky ssh
commands and the overhead associated with key management. Taboot can
be extended by writing your Func modules and tasks in Python.



%package -n taboot-func
Summary:        Func minion modules for use in conjunction with %{name}
Group:          Development/Libraries
Requires:       func
Requires:       python-modjkapi


%description -n taboot-func
Func minion modules for use in conjunction with %{name}.

Includes modjk - A func interface to the python-modjk API for managing
mod_jk via it's xml web api.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules
%{__mv} $RPM_BUILD_ROOT%{python_sitelib}/taboot-func $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules/%{_name}
%{__mkdir_p} %{buildroot}%{_mandir}/{man1,man5}
%{__gzip} -c docs/man/man1/taboot.1 > %{buildroot}/%{_mandir}/man1/taboot.1.gz
%{__ln_s} ./taboot.1.gz %{buildroot}/%{_mandir}/man1/tabootv.1.gz
%{__gzip} -c docs/man/man5/taboot-tasks.5 > %{buildroot}/%{_mandir}/man5/taboot-tasks.5.gz
%{__mv} share/edit-header %{buildroot}/%{_datadir}/%{_name}

%clean
%{__rm} -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_bindir}/taboot*
%{python_sitelib}/*%{_name}*
%{_datadir}/%{_name}*
%doc docs/rst LICENSE AUTHORS README
%doc %{_mandir}/man1/taboot.*
%doc %{_mandir}/man1/tabootv.*
%doc %{_mandir}/man5/taboot-tasks.*


%files -n taboot-func
%defattr(-,root,root,-)
%{python_sitelib}/func/minion/modules/%{_name}


%changelog
* Wed Apr 18 2012 Tim Bielawa <tbielawa@redhat.com> - 0.4.1-1
- RHIT1 - Password filtering

* Fri Jan 20 2012 Tim Bielawa <tbielawa@redhat.com> 0.4.0-1
- Taboot 0.4.0, the "Farewell, Friend" release

* Wed Jan 18 2012 Tim Bielawa <tbielawa@redhat.com> - 0.3.9-1rc3
- Fix vi launching with incorrect command line parameters

* Tue Jan 17 2012 Tim Bielawa <tbielawa@redhat.com> - 0.3.9-1rc2
- Fix EDITOR export in tabootv script

* Mon Jan 16 2012 Tim Bielawa <tbielawa@redhat.com> - 0.3.9-1rc1
- Major release, lots of internal code refactoring
- tbielawa@redhat.com:
  Fixes #25, Should have a guide for creating new scripts
  Fixes #26, Taboot is not DRY enough
  Fixes #28, More verbosity for debugging & development
  Fixes #33, Add functionality for strict ordering of hosts
  Fixes #34, Taboot 'edit' mode should hint at the file type and give instructions
  Fixes #35, Taboot should have a "noop" task
  Fixes #36, Preflight not doing mega concurrency as advertised
- jdetiber@redhat.com:
  Fixes #38, Escape HTML Tags in HTMLOutput
  Fixes #39, Colorize various output
  Fixes #40, Create a tabootv wrapper to make vi default EDITOR
  Fixes #41, Add server parameter to puppet (Safe)Run tasks
- abutcher@redhat.com:
  Fixes #37, Add a puppet noop task

* Thu Sep 29 2011 Tim Bielawa <tbielawa@redhat.com> 0.3.2-1
- Add Nagios (Un)SilenceHost classes (Fixes: #29) (tbielawa@redhat.com)
- Adding WaitOnInput subclass to SleepBase class for pausing until
  user input (Fixes: #30) (jason.detiberus@redhat.com)
- New HTMLOutput logger (Fixes: #31) (tbielawa@redhat.com)
- 'hacking' directory in git tree has script to make development testing easier.
- Update docs. pep8 fixes
- Make python-argparse a Requires for el6 as well

* Thu Aug 04 2011 Tim Bielawa <tbielawa@redhat.com> 0.3.1-1
- Spelling & grammar fixes all around (Fixes #23) (tbielawa@redhat.com)
- Added -E flag to edit script before running (Fixes #18)
  (jason.detiberus@redhat.com)
- Added -p flag (acts like -n in that it checks syntax, but also prints
  resulting yaml to be run onscreen) (Fixes #18) (jason.detiberus@redhat.com)
- Cleanup unnecessary documentation (tbielawa@redhat.com)
- Those are just bad ideas for a project with concurrency as a selling point
  (Remove user input modules) (tbielawa@redhat.com)
- Simplify a little example in the docs (tbielawa@redhat.com)
- Added -C flag for Concurrency, Fixed an error when -L wasn't specified and
  added CLIOutput when -L is specified and logging wasn't already set
  (Fixes #18) (jason.detiberus@redhat.com)
- Added command line flag to add logging (Fixes #18) (jason.detiberus@redhat.com)
- Add python utility to generate a graphviz dot file of the class inheritance
  graph of the python source codes. (tbielawa@redhat.com)
- Add conditional Requires on python-argparse. Update README and release notes.
  (tbielawa@redhat.com)
- Exit/continue the main load-loop sooner so we can validate YAML scripts and
  not blow up when not ran on a minion/overlord (like during testing...)
  (tbielawa@redhat.com)
- Switched argument parsing to use argparse (jason.detiberus@redhat.com)
- Fix nagios scheduling causing log-to-file to fail. (Fixes #24)
  (tbielawa@redhat.com)

* Thu Jun 23 2011 Tim Bielawa <tbielawa@redhat.com> 0.3.0-1
- Update version. 0.3.0. If Linux can do it -- so can we. (tbielawa@redhat.com)
- Now included in EPEL and Fedora. Fixes #9 (tbielawa@redhat.com)
- Correct a lot of spelling errors. Fixes #23 (Taboot maintainer has atrocious
  spelling) (tbielawa@redhat.com)
- Correctly handle YAML files with multiple YAML documents inside. Fixes #22
  (tbielawa@redhat.com)
- Better YAML loading debugging. Fixes #20 (tbielawa@redhat.com)
- Handle bad CLI options gracefully. Fixes #15 (tbielawa@redhat.com)
- Modify patch from jdetiber. Fixes #17 - sleep.Minutes not printing correct
  status message (tbielawa@redhat.com)
- Updated output for sleep.Minutes (jason.detiberus@redhat.com)
- Update man page (tbielawa@redhat.com)
- Update taboot-tasks manpage (tbielawa@redhat.com)
- Make HOST the default for downtime scheduling again (tbielawa@redhat.com)
- Updating Nagios task docs (tbielawa@redhat.com)
- Rewrite the Nagios task to use the new Func Nagios module instead of CURL.
  Fixes #6, #7, #11, #12 (tbielawa@redhat.com)
- Adding HTML versions of the man pages to the HTML docs. Fixes #13
  (tbielawa@redhat.com)

* Sun May 08 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.13-1
- Package maintenance + version bump
- Fixed spacing in the specfile changelog

* Thu May 05 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.12-1
- Version Bumpskies
- Add some misc scripts and instructions for making releases
- FIXED: modjk proxy not working. Updated puppet docs
- Added a '-s' option to skip preflight sections

* Mon May 02 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.11-1
- Nagios sys.exit()s if you lack kerberos tickets
- New tasks: puppet.{DeleteLockfile,SafeRun}
- puppet.run ignores errors to deal with puppet 2.6 changes
- Task for deleting puppet lock file.
- New man page, taboot-tasks.5. Fix up some grammar, etc, in taboot.1.

* Thu Apr 21 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.10-1
- Ceremonial .10 release. Mostly small changes.
- Change Summary wording
- pep0263 fixes pep8 Fixes
- Finally getting around to making the copyright headers uniform again.
- Maintainer scripts for automating release building

* Fri Apr 15 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.9-1
- Fix 'exit()' not being callable in python 2.4 (RHEL5) (tbielawa@redhat.com)
- Adding a script for building multiple targets (tbielawa@redhat.com)
- Changing description (tbielawa@redhat.com)
- Need the version file in the manifest when building from setup.py
  (tbielawa@redhat.com)
- Making cleaning work (tbielawa@redhat.com)
- Making build better on RHEL5 Don't build the docs at build time (Save in git
  tree) Straighten up the spec file (tbielawa@redhat.com)
- Including compiled manpage to lower buildrequires (tbielawa@redhat.com)
- Typo fix (tbielawa@redhat.com)

* Tue Apr 12 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.8-1
- Version bumpitybump (tbielawa@redhat.com)
- Specfile fixup (tbielawa@redhat.com)
- Updating example in readme (tbielawa@redhat.com)
- Attempting to get kerberos checking working (tbielawa@redhat.com)
- Add documentation about preflight block (tbielawa@redhat.com)

* Mon Apr 11 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.7-1
- Made a bad release. Fixing it up
- Add ability to run a set of preflight commands
- Updating build docs
- Enhancing Makefile with build targets
- Remove duplicate license file

* Wed Apr 06 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.6-1
- Cleaning out the RPM Lint. Adding a manpage (tbielawa@redhat.com)

* Wed Apr 06 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.5-1
- Update version in module (tbielawa@redhat.com)

* Wed Apr 06 2011 Tim Bielawa <tbielawa@redhat.com> 0.2.4-1
- Switching versioning back to the triplet form
- Smarter command line processing:
   - Handles command line options like --help
   - Adds support processing multiple release files
   - Adds support for just validating a scripts syntax via '-n'
   - Adds version string printing via -V (--version)
- Initialized to use tito

* Mon Apr  4 2011 Tim Bielawa <tbielawa@redhat.com> - 0.2-3
- Add LOTS of documentation on all the different modules.

- Also, add a new module: sleep, for pausing x minutes or seconds.

* Mon Apr  4 2011 Tim Bielawa <tbielawa@redhat.com> - 0.2-2
- Rebranding to Taboot. We are now an opensource project.

* Wed Jul 14 2010 John Eckersberg <jeckersb@redhat.com> - 0.2-1
- updated to version 0.2 which modifies the expected YAML format
  (not compatible with versions < 0.2 and vice versa)

* Fri May 14 2010 John Eckersberg <jeckersb@redhat.com> - 0.1-2
- update nagios to allow host-level downtime scheduling

* Thu May 06 2010 John Eckersberg <jeckersb@redhat.com> - 0.1-1
- mod_jk bug fixes and improvements

* Wed Aug 19 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-15
- Rewrite nagios tasks to shell out to curl for easy negotiate auth
- Remove all the contrib stuff

* Mon Aug 10 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-13
- Remove Requires on python-modjkapi

* Fri Aug 07 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-12
- Add taboot.contrib to packages in setup.py

* Mon Jun 22 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-9
- Return back string representation of exceptions for mod_jk tasks

* Fri Jun 12 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-6
- Allow LogOutput module to use stdout

* Mon Jun 08 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-5
- Add Require for modjkapi

* Mon Jun 08 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-3
- Add Require for PyYAML

* Tue Jun 02 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.2-1
- I think we're far enough to be 0.0.2
- Added taboot script

* Tue May 19 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-14
- Fix so documentation builds properly

* Mon May 18 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-13
- Rebuild for new goodness

* Tue Apr 28 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-12
- Better output

* Tue Apr 28 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-11
- Fix bug with TaskRunner._bail_failure

* Tue Apr 28 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-10
- Rebuild for documentation

* Mon Apr 27 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-9
- Bail on all hosts if one host bombs.

* Fri Apr 24 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-7
- Fix up poller task and re-architect the way sub-tasks get invoked

* Thu Apr 23 2009 Greg Blomquist <gblomqui@redhat.com> - 0.0.1-6
- Add poller task

* Wed Apr 22 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-3
- Fix bug where runner would not wait on all tasks

* Wed Apr 22 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-3
- Comment out EmailOutput since EL5 does not have email.mime

* Mon Mar 20 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-2
- Split into python-taboot and taboot-func

* Tue Feb 24 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-1
- Initial spec
