# NetworkLab VM Storage

The VM storage layer provisions one empty 20 GB VDI disk for each NetworkLab VM.

| VM | Role | Disk | Format |
|---|---|---:|---|
| NetworkLab-VM01-MGMT | MGMT | 20 GB | VDI |
| NetworkLab-VM02-INFRA | INFRA | 20 GB | VDI |
| NetworkLab-VM03-CLIENT | CLIENT | 20 GB | VDI |

The storage operation is idempotent: an existing controller and attached disk are reused.

No operating-system ISO is embedded or downloaded by NetworkLab. ISO attachment remains a separate operation so the lab does not make assumptions about the required operating system.

All disks are local VirtualBox storage associated with the isolated NetworkLab-Lab VM topology.