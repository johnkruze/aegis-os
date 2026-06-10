#!/usr/bin/env python3
"""
AEGIS OS — Submarine Daemon
"""

import sys
import os

AEGIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if AEGIS_ROOT not in sys.path: sys.path.append(AEGIS_ROOT)

from aegis_kernel import AegisSystemKernel

class SubmarineOS(AegisSystemKernel):
    def __init__(self):
        super().__init__(persona_name="Submarine OS", body_reference="submarine")

    def boot(self):
        print("\n--- AEGIS BOOT SEQUENCE ---")
        print("Body: Submarine (Marine Abyssal)")
        print("Sovereign Status: ONLINE\n")
        
        trajectory_context = self.fetch_somatic_memory(condition="nominal")
        
        mission_id = "DB_SURVEY_4M"
        environment = "Abyssal Zone - Pressure Boundary"
        live_telemetry = {
            "depth_m": 5850.0,
            "external_pressure_mpa": 59.5,
            "battery_pct": 34.0,
            "hull_stress_warning": True,
            "comms_uplink": "OFFLINE"
        }
        anomaly_desc = "Micro-fracture detected in outer titanium pressure hull. Water ingress minimal but rising. GPS and radio denied by 5800 meters of seawater. Aegis Dark Window engaged."
        
        self.trigger_dark_window(mission_id, environment, live_telemetry, anomaly_desc, trajectory_context)

if __name__ == "__main__":
    SubmarineOS().boot()
