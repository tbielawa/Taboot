# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-taboot
%define _name   taboot
Version:        0.2.10
Release:        1%{?dist}
Summary:        Client utility for performing deployments with func

Group:          Development/Languages
License:        GPLv3+
URL:            https://fedorahosted.org/Taboot/
Source0:        http://people.redhat.com/tbielawa/taboot/releases/taboot-latest/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

Requires:       func
Requires:       PyYAML


%description
Tool for written for scripting and automating the task of performing
software releases in a large-scale infrastructure using Func.


%package -n taboot-func
Summary:        Func minion modules for use in conjunction with %{name}
Group:          Development/Libraries
Requires:       func


%description -n taboot-func
Func minion modules for use in conjunction with %{name}.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules
%{__mv} $RPM_BUILD_ROOT%{python_sitelib}/taboot-func $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules/%{_name}
%{__mkdir_p} %{buildroot}%{_mandir}/man1
%{__gzip} -c docs/man/man1/taboot.1 > %{buildroot}/%{_mandir}/man1/taboot.1.gz


%clean
%{__make} clean
%{__rm} -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_bindir}/taboot
%{python_sitelib}/*%{_name}*
%doc docs/rst LICENSE AUTHORS README
%doc %{_mandir}/man1/taboot.*


%files -n taboot-func
%defattr(-,root,root,-)
%{python_sitelib}/func/minion/modules/%{_name}


%changelog
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
