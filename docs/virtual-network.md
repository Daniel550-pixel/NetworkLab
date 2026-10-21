# NetworkLab Virtual Network

## Application-managed virtual network

The NetworkLab web application now owns the virtual-network lifecycle. VirtualBox is the virtualization backend; the repository contains the implementation and the localhost UI is the control surface.

| Component | Value |
|---|---|
| Network name | NetworkLab-Lab |
| Network | 192.168.77.0/24 |
| Host endpoint | 192.168.77.1 |
| DHCP server | 192.168.77.2 |
| DHCP range | 192.168.77.100–192.168.77.200 |
| Mode | VirtualBox host-only |
| Internet access | Disabled |
| Physical LAN bridge | Disabled |

## Control flow

`app/services/virtualization_service.py` discovers VirtualBox, creates or reuses the host-only adapter, assigns the lab address, and provisions the isolated DHCP scope.

The localhost application exposes:

- `GET /api/virtual-network` — current virtual-network state
- `POST /api/virtual-network/create` — create/reconcile the lab segment

The Command Center exposes the same operation through the **Virtual network** card.

## Intended topology

```
Windows Host
  |
  +-- 192.168.77.1
  |
  +-- NetworkLab-Lab / 192.168.77.0/24
       |
       +-- Management node
       +-- Infrastructure node
       +-- Client node
```

The next layer is guest-node provisioning. Nodes will attach to this segment through VirtualBox host-only networking.

## Safety

The lab is intentionally isolated. NetworkLab does not configure a bridged adapter, enable Internet access, or target a production network. The application remains bound to localhost.
