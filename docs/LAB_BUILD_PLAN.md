# NetworkLab System Build

## Implemented system

- VirtualBox host-only network and DHCP provisioning.
- Three-role VM topology: MGMT, INFRA, CLIENT.
- VM storage/controller provisioning.
- Explicit/manual ISO attachment.
- VM lifecycle controls.
- Readiness gates.
- Continuous VirtualBox telemetry.
- Persistent incident history.
- Autonomous safe recovery.
- Architecture/control-plane state.
- Connectivity verification.
- Unified audit and evidence.

## Remaining guest-dependent work

These require an operating system to be installed in the VMs and therefore remain explicitly gated behind manual ISO installation:

1. MGMT guest configuration and administration tooling.
2. INFRA guest services (DNS/DHCP/service roles as selected for the stage).
3. CLIENT guest configuration.
4. Inter-VM service validation.
5. Guest-level evidence collection.

NetworkLab must not silently download or choose OS media.

## Automated build pipeline

prepare -> verify -> install guest OS manually -> configure guest roles -> validate services -> capture evidence

The host-side system is designed so the guest-dependent phase can be added without changing the VirtualBox control plane.
