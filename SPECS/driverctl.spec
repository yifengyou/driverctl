%global commit	fa9dce43d1a667d6e6e26895fbed01b3b04362c9

Name:		driverctl
Version:	0.111
Release:	1%{?dist}
Summary:	Device driver control utility

Group:		System Environment/Kernel
License:	LGPLv2
URL:		https://gitlab.com/driverctl/driverctl
BuildArch:	noarch

# rpm doesn't grok the gitlab url but spectool understands this monster
Source0:	https://gitlab.com/driverctl/%{name}/repository/archive.tar.gz?ref=%{version}#/%{name}-%{version}-%{commit}.tar.gz

# for udev macros
BuildRequires: systemd
Requires(post,postun): %{_sbindir}/udevadm
Requires: coreutils udev

%description
driverctl is a tool for manipulating and inspecting the system
device driver choices.

Devices are normally assigned to their sole designated kernel driver
by default. However in some situations it may be desireable to
override that default, for example to try an older driver to
work around a regression in a driver or to try an experimental alternative
driver. Another common use-case is pass-through drivers and driver
stubs to allow userspace to drive the device, such as in case of
virtualization.

driverctl integrates with udev to support overriding
driver selection for both cold- and hotplugged devices from the
moment of discovery, but can also change already assigned drivers,
assuming they are not in use by the system. The driver overrides
created by driverctl are persistent across system reboots
by default.

%prep
%setup -q -n %{name}-%{version}-%{commit}

%install
%make_install

%files
%license COPYING
%doc README TODO
%{_sbindir}/driverctl
%{_udevrulesdir}/*.rules
%{_udevrulesdir}/../vfio_name
%{_unitdir}/driverctl@.service
%dir %{_sysconfdir}/driverctl.d
%{_datadir}/bash-completion/
%{_mandir}/man8/driverctl.8*

%post
%udev_rules_update

%postun
%udev_rules_update

%changelog
* Wed Feb 05 2020 Flavio Leitner <fbl@redhat.com> - 0.111-1
- Updated to 0.111 (#1798626)

* Mon Mar 11 2019 Timothy Redaelli <tredaelli@redhat.com> - 0.108-1
- Fix bash autocompletion (#1657020)
- Fix --no-save to do not always returns with exit code 1
- Return error code when unbinding a device from a driver fails

* Tue Nov 20 2018 Timothy Redaelli <tredaelli@redhat.com> - 0.101-1
- Rebase to driverctl-0.101-1.el7 (#1648411):
  - Fix shellcheck warnings (#1506969)
  - Install bash-completion as driverctl instead of driverctl-bash-completion.sh
  - fix load_override for non-PCI bus
  - Make sure driverctl had loaded all the overrides before basic.target (#1634160)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.95-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.95-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.95-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Timothy Redaelli <tredaelli@redhat.com> - 0.95-1
- Update to 0.95
- update URLs to new group-based location

* Fri Sep 16 2016 Panu Matilainen <pmatilai@redhat.com> - 0.91-1
- Use a relative path from udevrulesdir
- Use fedorable source url which spectool actually understands
- Move bash completions to newer standard in %%{_datadir}/bash-completion
- Use %%make_install macro
- Require /usr/sbin/udevadm for %%post and %%postun

* Fri Sep 2 2016 Panu Matilainen <pmatilai@redhat.com> - 0.74-1
- Initial package
