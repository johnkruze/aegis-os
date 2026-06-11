# aegis-os

**Per-body operating system for physics-grounded autonomous agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Physics Engine](https://img.shields.io/badge/Engine-genesis--core-black?style=flat-square)](https://github.com/johnkruze/genesis-core)
[![ICP](https://img.shields.io/badge/ICP-Mainnet-blue?style=flat-square)](https://github.com/johnkruze/spectra-genesis)

Aegis OS is Layer 3 of the G^G stack. Each body — humanoid, drone, submarine, satellite, vehicle, boat — runs a dedicated daemon that pulls physics trajectories from the G^G corpus, makes decisions through Kid Cosmo, and seals every decision as an immutable manifest on the Internet Computer.

---

## Stack Position

```
ICP Mainnet  ←── sealed manifests, SOMA proofs
     ↑
Aegis OS     ←── you are here
     ↑
Kid Cosmo    ←── reasoning kernel (MLX, Gemma, Qwen)
     ↑
genesis-core ←── physics ground truth (Rust, 1000Hz)
```

---

## Body Daemons

Eight autonomous daemons, one per body type:

| Daemon | Body | Physics Domain |
|--------|------|----------------|
| `humanoid_daemon.py` | Bipedal humanoid | Terran, joint impedance |
| `autonomous_car_daemon.py` | Ground vehicle | Terran, tire-terrain |
| `drone_daemon.py` | Aerial drone | Atheric, EW jamming |
| `submarine_daemon.py` | UUV | Marine, buoyancy |
| `satellite_daemon.py` | Spacecraft | Orbital, attitude |
| `maven_daemon.py` | Mars orbiter | Mars EDL |
| `autonomous_boat_daemon.py` | USV | Marine, hydrodynamics |
| `titanhauler_daemon.py` | Heavy logistics | Terran, high-load |

---

## Fleet Commander

`fleet_commander.py` dispatches all 8 daemons sequentially. One call → eight autonomous decisions, each sealed on-chain.

```bash
python3 fleet_commander.py
```

---

## Pulse Reactor

`pulse_reactor.py` runs the autonomous loop: `body_sweep` (Rust physics) → `fleet_commander` → MLX reasoning → ICP seal. 30-minute cycle.

```bash
python3 pulse_reactor.py           # continuous loop
python3 pulse_reactor.py --test-mode  # single cycle
```

---

## Decision Manifests

Every daemon decision produces a cryptographically sealed manifest:

```json
{
  "mission_id": "aegis_humanoid_sweep_001",
  "body": "humanoid",
  "environment": "terran",
  "timestamp": "2026-06-10T10:41:00Z",
  "is_dark_window": false,
  "epistemic_status": "ZTP_ACTIVE",
  "results": { ... },
  "sha256_proof": "ea0fd0d7c71d6..."
}
```

Manifests are anchored on ICP mainnet via `record_aegis_manifest` on `ad7wi-4aaaa-aaaad-aeijq-cai`.

---

## SOMA Staking Gate

`aegis_kernel.py` checks SOMA balance at boot. Daemons require a minimum SOMA stake to operate — physics proof is the authentication layer.

---

## Related

- [genesis-core](https://github.com/johnkruze/genesis-core) — Physics engine
- [kid-cosmo](https://github.com/johnkruze/kid-cosmo) — Reasoning kernel
- [spectra-genesis](https://github.com/johnkruze/spectra-genesis) — ICP canister (manifest target)
- [zero-trust-physics](https://github.com/johnkruze/zero-trust-physics) — ZTP auditors
- [Datasets](https://huggingface.co/spiderpilot89) — HuggingFace

---

John Kruze · [ZeroTrustPhysics.com](https://ZeroTrustPhysics.com) · kruze@zerotrustphysics.com
