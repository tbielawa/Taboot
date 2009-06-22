# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-poseidon
%define _name   poseidon
Version:        0.0.2
Release:        9%{?dist}
Summary:        Client library for performing deployments with func

Group:          Development/Languages
License:        GPLv3+
URL:            https://engineering.redhat.com/trac/GIT-RE/wiki/poseidon
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel, python-sphinx

Requires:       func, PyYAML, python-modjkapi


%description
Client library for performing deployments with func.  Provides useful
helper utilities to perform common task patterns using func.

%package -n poseidon-func
Summary:        Func minion modules for use in conjunction with %{name}
Group:          Development/Libraries
Requires:       func


%description -n poseidon-func
Func minion modules for use in conjunction with %{name}.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build
%{__python} setup.py doc


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules/%{_name}
mv $RPM_BUILD_ROOT%{python_sitelib}/poseidon-func/* $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules/%{_name}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_bindir}/poseidon
%doc docs/html COPYING LICENSE AUTHORS
# For noarch packages: sitelib
%{python_sitelib}/*

%files -n poseidon-func
%defattr(-,root,root,-)
%{python_sitelib}/func/minion/modules/%{_name}


%changelog
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
- Added poseidon script

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
- Split into python-poseidon and poseidon-func

* Tue Feb 24 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-1
- Initial spec
