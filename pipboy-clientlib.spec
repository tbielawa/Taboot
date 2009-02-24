# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           pipboy-clientlib
Version:        0.0.1
Release:        1%{?dist}
Summary:        Client library for interacting with pipboy

Group:          Development/Languages
License:        GPLv3+
URL:            https://engineering.redhat.com/trac/GIT-RE/wiki/pipboy-clientlib
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel


%description
Client library for interacting with pipboy.  Provides useful helper
utilities to perform common task patterns using pipboy.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc docs/*rst COPYING LICENSE AUTHORS
# For noarch packages: sitelib
%{python_sitelib}/*


%changelog
* Tue Feb 24 2009 John Eckersberg <jeckersb@redhat.com> - 0.0.1-1
- Initial spec
