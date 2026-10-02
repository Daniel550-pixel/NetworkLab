# NetworkLab Virtual Network

## Virtual network baseline

NetworkLab uses a **VirtualBox host-only network** as the initial stage-lab network.

| Component | Value |
|---|---|
| Network name | NetworkLab-Lab |
| Network | 192.168.77.0/24 |
| Host endpoint | 192.168.77.1 |
| DHCP range | 192.168.77.100–192.168.77.200 |
| Internet access | Disabled |
| Physical LAN bridge | Disabled |

This creates an isolated Layer-2 virtual segment on the Windows host. Virtual machines can later be attached to the segment without exposing the lab directly to the physical network.

## Create

From the NetworkLab repository root in PowerShell:

```powershell
.\powershell\virtualization\New-NetworkLabVirtualNetwork.ps1
```

Preview without changing the host:

```powershell
.\powershell\virtualization\New-NetworkLabVirtualNetwork.ps1 -WhatIf
```

Inspect:

```powershell
.\powershell\virtualization\Get-NetworkLabVirtualNetwork.ps1
```

## Intended topology

The virtual network is the Layer-2 foundation for the stage lab:

```
Windows Host
  |
  +-- 192.168.77.1
  |
  +-- NetworkLab-Lab
       |
       +-- Management / test VM
       +-- Infrastructure / service VM
       +-- Client / validation VM
```

The VM layer is deliberately separate from creation of the virtual segment. This allows the network to be validated before any guest operating systems are introduced.

## Safety

Do not configure a bridged adapter for this lab. The baseline intentionally uses host-only networking so the virtual segment remains isolated from the physical LAN and Internet.
