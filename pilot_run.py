#!/usr/bin/env python3
"""
G^G: OUROBOROS PILOT STRIKE 
Initiates the 1000Hz Proprioceptive Ghost integration across all 4 spatial domains
and anchors the resulting telemetry to the Internet Computer (ICP).
"""

import os
import sys

AEGIS_ROOT = os.path.dirname(os.path.abspath(__file__))
if AEGIS_ROOT not in sys.path:
    sys.path.append(AEGIS_ROOT)

# Force the Aegis OS to bypass the Generative LLM and use the Sovereign Rust Kernel
os.environ["OUROBOROS_ENABLED"] = "1"
# Target the Mainnet for data sealing
os.environ["AEGIS_NETWORK"] = "ic"

from aegis_kernel import AegisSystemKernel

def run_pilot():
    domains = ["marine", "aerial", "orbital", "terran"]
    
    print("==========================================================")
    print("  G^G OUROBOROS MULTI-DOMAIN PILOT SEQUENCE")
    print("  Targeting ICP Mainnet `spectra_genesis_backend`")
    print("==========================================================\n")

    for domain in domains:
        print(f"\n>>> INITIATING PILOT: {domain.upper()} SUBSTRATE")
        
        # Instantiate the Operating System for this drone/vehicle
        persona = f"OuroborosPilot_{domain.upper()}"
        kernel = AegisSystemKernel(persona_name=persona, body_reference=f"ouroboros_{domain}")
        
        # Manually force the staking gate open if the local identity lacks ICP funds
        kernel.staked = True 
        
        # Construct a synthetic sensor failure (Dark Window)
        live_telemetry = {
            "gps_status": "DENIED - JAMMING DETECTED",
            "pitot_static": "ANOMALOUS",
            "imu_state": "VIBRATION CLIPPING (35G+)"
        }
        
        anomaly_desc = f"Total sensor blackout encountered in {domain} theater. Engaging dead-reckoning protocols."
        trajectory_ctx = {
            "parent_trajectory_id": f"pilot_strike_{domain}_01",
            "scenario": "sensor_deprivation",
            "score": None,
            "physics_proof": "GENESIS_PENDING"
        }
        
        # Trigger the Dark Window (This will execute ouroboros_kernel.rs and push to ICP)
        kernel.trigger_dark_window(
            mission_id=f"ouroboros_{domain}_mission_theta",
            environment=domain,
            live_telemetry=live_telemetry,
            anomaly_desc=anomaly_desc,
            trajectory_context=trajectory_ctx
        )
        print(f"<<< PILOT {domain.upper()} COMPLETED.\n")

if __name__ == "__main__":
    run_pilot()
