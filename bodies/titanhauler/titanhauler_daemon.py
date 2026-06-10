#!/usr/bin/env python3
"""
AEGIS OS — Titanhauler Daemon
"""

import sys
import os

AEGIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if AEGIS_ROOT not in sys.path: sys.path.append(AEGIS_ROOT)

from aegis_kernel import AegisSystemKernel

class TitanhaulerOS(AegisSystemKernel):
    def __init__(self):
        super().__init__(persona_name="Titanhauler OS", body_reference="titanhauler")

    def boot(self):
        print("\n--- AEGIS BOOT SEQUENCE ---")
        print("Body: Titanhauler (Heavy Industrial)")
        print("Sovereign Status: ONLINE\n")
        
        # 1. Fetch memory
        trajectory_context = self.fetch_somatic_memory(condition="sand")
        
        # 2. Anomaly
        mission_id = "TH_OP_77"
        environment = "Terran Resource Extraction - Sand Sector"
        live_telemetry = {
            "track_slip_ratio_left": 0.85,
            "track_slip_ratio_right": 0.90,
            "engine_load_pct": 115.0,
            "pitch_angle_deg": -5.2,
            "soil_compaction_est": "CRITICAL",
            "comms_uplink": "OFFLINE"
        }
        anomaly_desc = "Massive track slip detected. Soil yielding beneath left tread. Cloud link severed. Aegis Dark Window engaged."
        
        # 3. Trigger
        self.trigger_dark_window(mission_id, environment, live_telemetry, anomaly_desc, trajectory_context)

if __name__ == "__main__":
    TitanhaulerOS().boot()
