

* 官方源码 ： https://gitlab.com/driverctl/driverctl



```
driverctl is a tool for manipulating and inspecting the system
device driver choices.
```

*  体系架构无关，LGPLv2协议


```
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
```


文件很少

![](./image/Pasted%20image%2020230522211312.png)


有一个systemd服务

```
[root@rocky-koji-a ~]# systemctl  cat driverctl@.service
# /usr/lib/systemd/system/driverctl@.service
[Unit]
Description=Load the driverctl override for %i
DefaultDependencies=no
Before=basic.target
RefuseManualStart=yes
RefuseManualStop=yes
ConditionPathExists=/etc/driverctl.d/%i

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/driverctl load-override %I
TimeoutStartSec=300
```

![](./image/Pasted%20image%2020230522211426.png)

* 强力依赖于udev机制
* 核心文件driverctl只有270行代码，应改不难掌握
* 只要你懂udev就行

![](./image/Pasted%20image%2020230522211517.png)
















