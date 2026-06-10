#!/usr/bin/env python3
"""
AEGIS OS — Satellite Daemon
"""

import sys
import os

AEGIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if AEGIS_ROOT not in sys.path: sys.path.append(AEGIS_ROOT)

from aegis_kernel import AegisSystemKernel

class SatelliteOS(AegisSystemKernel):
    def __init__(self):
        super().__init__(persona_name="Satellite OS", body_reference="satellite")

    def boot(self):
        print("\n--- AEGIS BOOT SEQUENCE ---")
        print("Body: Satellite (Orbital Commercial)")
        print("Sovereign Status: ONLINE\n")
        
        trajectory_context = self.fetch_somatic_memory(condition="nominal")
        
        mission_id = "SAT_LEO_NX5"
        environment = "Low Earth Orbit - Station Keeping"
        live_telemetry = {
            "body_temp_c": 87.5,
            "battery_pct": 98.0,
            "omega_mag": 0.0012,
            "reaction_wheel_rpm": [4500, 4800, 4100],
            "comms_uplink": "OFFLINE"
        }
        anomaly_desc = "Critical thermal fault threshold exceeded. Body temperature climbing towards 90C. Reaction wheels dissipating heat poorly. Cloud link severed. Aegis Dark Window engaged."
        
        self.trigger_dark_window(mission_id, environment, live_telemetry, anomaly_desc, trajectory_context)

if __name__ == "__main__":
    SatelliteOS().boot()
