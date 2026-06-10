#!/usr/bin/env python3
import os
import subprocess
import time

AEGIS_ROOT = os.path.dirname(os.path.abspath(__file__))
BODIES_DIR = os.path.join(AEGIS_ROOT, "bodies")

def command_fleet():
    print("═══════════════════════════════════════════════════════════")
    print("  AEGIS OS — SOVEREIGN FLEET COMMANDER")
    print("  Initiating full-fleet Dark Window anomaly simulation.")
    print("  Target: Decentralized sealing to Spectra ICP Canister.")
    print("═══════════════════════════════════════════════════════════\n")

    bodies = [
        "autonomous_boat/autonomous_boat_daemon.py",
        "autonomous_car/autonomous_car_daemon.py",
        "humanoid/humanoid_daemon.py",
        "maven/maven_daemon.py",
        "satellite/satellite_daemon.py",
        "submarine/submarine_daemon.py",
        "titanhauler/titanhauler_daemon.py",
    ]

    successes = 0
    start_time = time.time()

    for rel_path in bodies:
        full_path = os.path.join(BODIES_DIR, rel_path)
        body_name = rel_path.split('/')[0].upper()
        
        print(f"\n>>>>> [DEPLOYING] {body_name} Daemon <<<<<")
        try:
            result = subprocess.run(["python3", full_path], capture_output=False)
            if result.returncode == 0:
                successes += 1
        except Exception as e:
            print(f"Failed to execute {body_name}: {e}")
            
        time.sleep(2) # Breathing room between MLX inferences

    print("\n═══════════════════════════════════════════════════════════")
    print(f"  FLEET COMMANDER CYCLE COMPLETE")
    print(f"  Successful Deployments: {successes}/{len(bodies)}")
    print(f"  Total Time: {time.time() - start_time:.1f}s")
    print("═══════════════════════════════════════════════════════════")

if __name__ == "__main__":
    command_fleet()
