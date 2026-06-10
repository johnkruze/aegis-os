#!/usr/bin/env python3
"""
AEGIS OS — Autonomous Boat Daemon
"""

import sys
import os

AEGIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if AEGIS_ROOT not in sys.path: sys.path.append(AEGIS_ROOT)

from aegis_kernel import AegisSystemKernel

class AutonomousBoatOS(AegisSystemKernel):
    def __init__(self):
        super().__init__(persona_name="Autonomous Boat OS", body_reference="autonomous_boat")

    def boot(self):
        print("\n--- AEGIS BOOT SEQUENCE ---")
        print("Body: Autonomous Boat (Marine Surface)")
        print("Sovereign Status: ONLINE\n")
        
        trajectory_context = self.fetch_somatic_memory(condition="nominal")
        
        mission_id = "USV_PATROL_J2"
        environment = "Surface Ocean - High Sea State"
        live_telemetry = {
            "speed_knots": 42.5,
            "wave_height_m": 4.2,
            "pitch_angle_deg": 18.5,
            "radar_contact": "UNKNOWN_VESSEL_INTERCEPT",
            "comms_uplink": "OFFLINE"
        }
        anomaly_desc = "Massive wave slam detected at high speed. Unidentified fast-moving vessel on intercept course. Starlink/Satcom hardware damaged by wave impact. Aegis Dark Window engaged."
        
        self.trigger_dark_window(mission_id, environment, live_telemetry, anomaly_desc, trajectory_context)

if __name__ == "__main__":
    AutonomousBoatOS().boot()
