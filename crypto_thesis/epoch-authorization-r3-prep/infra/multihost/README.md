# Multi-host deployment boundary

Copy `inventory.example.yml` to an ignored `inventory.yml` and replace all
RFC 5737 example addresses. Each host must be reachable through SSH and report
its OS, CPU, memory, disk, clock synchronization, Besu/JDK hashes, and physical
host relationship.

The current workstation has no configured WSL distribution, Hyper-V VM set,
VirtualBox/VMware manager, or remote SSH inventory. Therefore this directory is
an executable deployment design, not evidence that a multi-host environment
exists.

Formal deployment must use fresh node and role keys. Private keys and the real
inventory must never be committed.
