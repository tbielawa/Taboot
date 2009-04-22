# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-poseidon
%define _name   poseidon
Version:        0.0.1
Release:        1%{?dist}
Summary:        Client library for performing deployments with func

Group:          Development/Languages
License:        GPLv3+
URL:            https://engineering.redhat.com/trac/GIT-RE/wiki/poseidon
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

Requires:       func


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


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules/%{_name}
mv $RPM_BUILD_ROOT%{python_sitelib}/poseidon-func/* $RPM_BUILD_ROOT%{python_sitelib}/func/minion/modules/%{_name}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc docs/*rst COPYING LICENSE AUTHORS
# For noarch packages: sitelib
%{python_sitelib}/*

%files -n poseidon-func
%defattr(-,root,root,-)
%{python_sitelib}/func/minion/modules/%{_name}


%changelog
* Mon Mar 20 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-2
- Split into python-poseidon and poseidon-func

* Tue Feb 24 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-1
- Initial spec
