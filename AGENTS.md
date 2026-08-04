# CLAUDE.md — Aegis OS

**Status:** FUNCTIONAL — dormant, will run again. 7 bodies, IC mainnet, SOMA staking.
**Layer:** 3 of 3 (G^G → Kid Cosmo → Aegis OS)
**Rust port:** `G^G/aegis_kernel/` — fleet_commander.rs + pulse_reactor.rs dispatch the Python body daemons via subprocess. Not a replacement — MLX reasoning still runs through Python.

---

## Purpose

Aegis OS is the per-body operating system. Each body daemon inherits `AegisSystemKernel`, provisions a dfx identity, checks its SOMA stake, fetches somatic memory from the G^G corpus, and triggers autonomous reasoning via Kid Cosmo when anomalies arise. Decisions are sealed as SHA-256 manifests and anchored on the Internet Computer mainnet.

---

## Architecture

```
Aegis OS/
├── aegis_kernel.py          # AegisSystemKernel base class
│                              - dfx identity provisioning (per-daemon)
│                              - SOMA staking gate (min 1.0 SOMA to reason)
│                              - Auto-fund from Citadel if understaked
│                              - Somatic memory fetch (CorpusMemory)
│                              - Dark Window handler (trigger_dark_window)
│                              - Manifest sealing (SHA-256 → local JSON + ICP)
│
├── bodies/                   # 7 body daemons (inherit kernel, body-specific telemetry only)
│   ├── titanhauler/          # Terran — 20-200T tracked hauler
│   ├── humanoid/             # Terran — bipedal locomotion
│   ├── autonomous_car/       # Terran — road dynamics
│   ├── satellite/            # Orbital — LEO station-keeping
│   ├── maven/                # Orbital — interceptor
│   ├── submarine/            # Marine — abyssal pressure
│   └── autonomous_boat/      # Marine — surface vessel
│
├── fleet_commander.py        # Master dispatcher
│                              - Runs all 7 daemons sequentially via subprocess
│                              - 2s sleep between MLX inferences
│                              - Reports success count and total time
│
├── pulse_reactor.py          # Autonomous heartbeat loop
│                              - Cycle: body_sweep.rs (100 trajs) → fleet_commander
│                              - 30-minute cadence (configurable)
│                              - --test-mode for single cycle
│                              - RotatingFileHandler → pulse.log
│
├── ouroboros_stream.py       # Infinite marine ingestion daemon
│                              - Inherits AegisSystemKernel as submarine body
│                              - 500-trajectory chunks from marine_monte_carlo
│                              - Anomaly filter → MLX reasoning → SOMA mint
│                              - Burns local data after processing (zero disk)
│                              - Appends anomalies to data/products/tier1/TIER1_OCEAN_ANOMALIES.jsonl
│
├── pilot_run.py              # Multi-domain Ouroboros pilot strike
│                              - Forces Rust ouroboros_kernel (bypasses Kid Cosmo LLM)
│                              - Forces mainnet: AEGIS_NETWORK=ic
│                              - Targets 4 domains: marine, aerial, orbital, terran
│                              - Sets kernel.staked = True (bypasses funding gate)
│                              - Use: flight test for dead-reckoning across all domains
│
├── upload_daemon.py          # R2 watcher daemon
│                              - Watches data/corpus/products/ for finalized JSON
│                              - Uploads to R2 (Cloudflare) object storage
│                              - Purges local after confirmed upload (15s poll interval)
│
├── integration/
│   ├── icp_bridge.py         # ICP economic bridge — CORE, OPERATIONAL
│   │                           - push_manifest_to_icp(): 3-retry exponential backoff
│   │                           - mint_somatic_proof(): physics proof → SOMA minting
│   │                           - fund_daemon_from_citadel(): SOMA transfers from Citadel
│   │                           - AEGIS_NETWORK env var: "local" or "ic"
│   │                           - DFX CWD: G^G/spectra_genesis
│   ├── workspace_bridge.py   # Diagnostic: Workspace Drive access via service account
│   ├── workspace_probe.py    # Diagnostic: Admin Directory API probe (gcloud credentials)
│   └── dual_key_probe.py     # Diagnostic: Domain-Wide Delegation test (kruze@aijesusbro.com)
│
├── memory/
│   └── corpus_indexer.py     # Somatic memory interface
│                              - CorpusMemory class
│                              - find_latest_trajectory(body_type, condition)
│                              - Reads from data/corpus/{body}/ (Tier 2)
│
└── manifests/                # Sealed decision manifests
                               - 4,651 local JSON files
                               - Named: manifest_{body}_{unix_timestamp}.json
                               - New manifests anchor to IC mainnet via icp_bridge
```

---

## Boot Sequence (per daemon)

1. `AegisSystemKernel.__init__()` — set persona name + body reference
2. `provision_sovereign_identity()` — create/reuse dfx identity, check SOMA balance
3. If SOMA < 1.0 → `fund_daemon_from_citadel()` (auto-fund 10 SOMA from Citadel)
4. `ReasoningAgent()` — initialize Kid Cosmo (MLX Qwen 2.5 7B)
5. `CorpusMemory()` — connect to data/corpus/
6. `boot()` — body-specific: fetch memory → build telemetry → trigger Dark Window

---

## SOMA Economics

- **Staking gate:** Daemon checks its own SOMA balance at boot. Refuses to reason if < 1.0 SOMA.
- **Auto-fund:** If understaked, requests 10 SOMA from Citadel (john_kruze_prime identity).
- **Minting:** Only `spectra_genesis_backend` canister can mint SOMA via `mint_somatic_proof`.
- **SOMA Ledger:** `mwtw4-wiaaa-aaaak-qx57a-cai` (IC mainnet, ICRC-1/2/3).
- **Network:** Set `AEGIS_NETWORK=ic` for mainnet, defaults to `local`.

---

## Running

```bash
# Single body daemon
python3 bodies/titanhauler/titanhauler_daemon.py

# Full fleet (7 bodies sequential)
python3 fleet_commander.py

# Autonomous loop (30-min cadence)
nohup python3 pulse_reactor.py > pulse.log 2>&1 &

# Single test cycle
python3 pulse_reactor.py --test-mode

# Ouroboros infinite marine stream
python3 ouroboros_stream.py          # infinite
python3 ouroboros_stream.py --test   # single bite

# Multi-domain Ouroboros pilot (forces Rust kernel + mainnet)
python3 pilot_run.py

# GCS upload watcher
python3 upload_daemon.py
```

---

## Dependencies

- Python 3.13
- Kid Cosmo runtime (`Kid Cosmo/runtime/reasoning_agent.py`)
- mlx_lm (installed at /opt/homebrew/opt/python@3.13/bin/python3.13)
- dfx CLI (for ICP identity + canister calls)
- G^G corpus data at `data/corpus/`
- R2 credentials at `~/.spectrum-secrets/` (for upload_daemon.py)
