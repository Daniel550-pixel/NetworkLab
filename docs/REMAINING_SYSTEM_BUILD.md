# NetworkLab Remaining System Build

## Implemented

The host-side system now exposes an OS-agnostic guest build contract for all three lab roles:

- MGMT — management and diagnostics
- INFRA — DNS, DHCP and lab services
- CLIENT — client networking and validation

The build deliberately stops at the guest boundary until an OS ISO is manually selected and installed.

## Execution chain

1. Prepare host-side network, VM topology and storage.
2. Select and attach the OS ISO manually.
3. Install the guest OS.
4. Apply the role contract.
5. Configure guest services.
6. Run host-assisted endpoint validation.
7. Run guest-to-guest validation from inside the guests.
8. Capture the evidence package.

## New runtime surfaces

- GET /api/guest/contracts
- GET /api/guest/validation
- POST /api/evidence/capture

Evidence is written to logs/evidence/ as timestamped JSON.

## Safety boundary

NetworkLab does not automatically download OS media, guess an OS, or alter guest-operating-system configuration before installation. Guest automation can be added behind the role contract once the selected guest OS and management mechanism are known.