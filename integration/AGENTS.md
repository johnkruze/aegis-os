# Aegis OS — ICP Integration

**Purpose:** ICP canister integration code for Aegis OS body daemons.

Connects Aegis body daemons to IC mainnet canisters (backend, SOMA ledger, agent).

## Files

- `icp_bridge.py` — Primary bridge: calls `record_aegis_manifest` and `record_trajectory_proof` on IC mainnet
- `workspace_bridge.py` — Workspace-level canister communication layer
- `workspace_probe.py` — Probes canister state and workspace health
- `dual_key_probe.py` — Dual-key authentication probe for canister access

## Canisters

- Backend: `ad7wi-4aaaa-aaaad-aeijq-cai`
- SOMA ledger: `mwtw4-wiaaa-aaaak-qx57a-cai`
