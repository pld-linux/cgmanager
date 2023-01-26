# TODO: PLDify SysV init scripts
#
# Conditional build:
%bcond_without	static_libs	# static library
#
Summary:	Linux cgroup manager
Summary(pl.UTF-8):	Zarządca linuksowych cgroup
Name:		cgmanager
Version:	0.42
Release:	1
License:	GPL v2
Group:		Daemons
#Source0Download: https://linuxcontainers.org/cgmanager/downloads/
Source0:	https://linuxcontainers.org/downloads/cgmanager/%{name}-%{version}.tar.gz
# Source0-md5:	6cf7549e91a73c56164a28ef4d2980ce
Patch0:		%{name}-glibc.patch
URL:		https://linuxcontainers.org/cgmanager/
BuildRequires:	dbus-devel >= 1.2.16
BuildRequires:	help2man
# libnih, libnih-dbus
BuildRequires:	libnih-devel >= 1.0.3
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/ldconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name}-libs = %{version}-%{release}
Requires:	dbus >= 1.2.16
Requires:	rc-scripts
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
CGManager is a central privileged daemon that manages all your cgroups
for you through a simple DBus API. It's designed to work with nested
LXC containers as well as accepting unprivileged requests including
resolving user namespaces UIDs/GIDs.

%description -l pl.UTF-8
CGManager to centralny, uprzywilejowany demon zarządzający wszystkimi
cgroupami poprzez proste API DBus. Jest zaprojektowany do pracy z
zagnieżdżonymi kontenerami LXC, a także przyjmowania
nieuprzywilejowanych żądań, w tym rozwiązywania UID-ów/GID-ów
przestrzeni nazw użytkowników.

%package libs
Summary:	Linux cgroup manager library
Summary(pl.UTF-8):	Biblioteka do zarządzania linuksowymi cgroupami
Group:		Libraries
Requires:	dbus-libs >= 1.2.16
Requires:	libnih >= 1.0.3

%description libs
Linux cgroup manager library.

%description libs -l pl.UTF-8
Biblioteka do zarządzania linuksowymi cgroupami.

%package devel
Summary:	Header files for cgmanager library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki cgmanager
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	libnih-devel >= 1.0.3

%description devel
Header files for cgmanager library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki cgmanager.

%package static
Summary:	Static cgmanager library
Summary(pl.UTF-8):	Statyczna biblioteka cgmanager
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static cgmanager library.

%description static -l pl.UTF-8
Statyczna biblioteka cgmanager.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	%{!?with_static_libs:--disable-static} \
	--with-init-script=sysvinit,systemd \
	--with-pamdir=/%{_lib}/security
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	SYSTEMD_UNIT_DIR=%{systemdunitdir}

%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/cgmanager/tests
rmdir $RPM_BUILD_ROOT%{_datadir}/cgmanager
# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libcgmanager.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add cgmanager
/sbin/chkconfig --add cgproxy
%service cgmanger restart
%service cgproxy restart
%systemd_post cgmanager.service
%systemd_post cgproxy.service

%preun
if [ "$1" = "0" ]; then
	%service -q cgproxy stop
	%service -q cgmanager stop
	/sbin/chkconfig --del cgproxy
	/sbin/chkconfig --del cgmanager
fi
%systemd_preun cgproxy.service
%systemd_preun cgmanager.service

%postun
%systemd_reload

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cgm
%attr(755,root,root) %{_sbindir}/cgmanager
%attr(755,root,root) %{_sbindir}/cgproxy
%dir %{_libexecdir}/cgmanager
%attr(755,root,root) %{_libexecdir}/cgmanager/cgm-release-agent
%attr(755,root,root) /%{_lib}/security/pam_cgm.so
%attr(754,root,root) /etc/rc.d/init.d/cgmanager
%attr(754,root,root) /etc/rc.d/init.d/cgproxy
%{systemdunitdir}/cgmanager.service
%{systemdunitdir}/cgproxy.service
%{_mandir}/man1/cgm.1*
%{_mandir}/man8/cgmanager.8*
%{_mandir}/man8/cgproxy.8*

%files libs
%defattr(644,root,root,755)
%doc ChangeLog README
%attr(755,root,root) %{_libdir}/libcgmanager.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcgmanager.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcgmanager.so
%{_includedir}/cgmanager
%{_pkgconfigdir}/libcgmanager.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libcgmanager.a
%endif
