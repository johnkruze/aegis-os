#!/usr/bin/env python3
import sys
import os
import json
import time
import subprocess

AEGIS_ROOT = os.path.dirname(os.path.abspath(__file__))
SPECTRUM_ROOT = os.path.dirname(AEGIS_ROOT)

if AEGIS_ROOT not in sys.path:
    sys.path.append(AEGIS_ROOT)

from aegis_kernel import AegisSystemKernel
from integration.icp_bridge import mint_somatic_proof

class OuroborosStreamDaemon(AegisSystemKernel):
    def __init__(self):
        super().__init__("Ouroboros Marine Daemon", "submarine")
        self.chunk_size = 500  # Generate 500 trajectories per bite
        self.offset = 0
        self.tmp_out = "/tmp/ouroboros_marine_chunk.json"
        
        # The Regurgitation Pipeline (Tier 1 Extraction)
        self.regurgitation_out = os.path.join(SPECTRUM_ROOT, "data", "products", "tier1", "TIER1_OCEAN_ANOMALIES.jsonl")
        os.makedirs(os.path.dirname(self.regurgitation_out), exist_ok=True)
        
    def boot(self, daemonize=True):
        print("\n[OUROBOROS] Initializing Infinite Ingestion Stream (Marine Substrate)")
        print(f"[OUROBOROS] Chunk Size: {self.chunk_size} trajectories")
        
        while True:
            self._ingest_bite()
            if not daemonize:
                break
            time.sleep(1) # Give the system a breath

    def _ingest_bite(self):
        print(f"\n[OUROBOROS] Biting {self.chunk_size} trajectories (Offset: {self.offset}) from genesis_core...")
        cmd = ["cargo", "run", "--release", "--bin", "marine_monte_carlo", "--", str(self.chunk_size), "--out", self.tmp_out, "--offset", str(self.offset)]
        
        self.offset += self.chunk_size
        
        start = time.time()
        res = subprocess.run(cmd, cwd=os.path.join(SPECTRUM_ROOT, "G^G", "genesis_core"), capture_output=True, text=True)
        
        if res.returncode != 0:
            print("[OUROBOROS] CRITICAL: Engine failure.")
            print(res.stderr)
            time.sleep(5)
            return

        print(f"[OUROBOROS] Physics Generated in {time.time() - start:.2f}s. Digesting memory...")
        
        if not os.path.exists(self.tmp_out):
            return

        with open(self.tmp_out, 'r') as f:
            data = json.load(f)
            
        trajectories = data.get("trajectories", [])
        
        anomaly_found = False
        for traj in trajectories:
            ctx = traj.get("reasoning_context", {})
            if ctx.get("is_anomaly", False):
                anomaly_found = True
                print(f"[OUROBOROS] Anomaly Detected in {traj['id']} -> {ctx.get('anomaly_type')}")
                
                # Execute Sovereign Reasoning
                live_telemetry = traj.get("data", [])[-1] if traj.get("data") else {}
                
                manifest = self.trigger_dark_window(
                    mission_id=traj['id'],
                    environment="Ocean/Marine",
                    live_telemetry=live_telemetry,
                    anomaly_desc=f"{ctx.get('anomaly_type')}: {ctx.get('failure_mode')}",
                    trajectory_context={
                        "parent_trajectory_id": traj['id'],
                        "scenario": traj.get('scenario'),
                        "score": traj.get('score'),
                        "physics_proof": traj.get('proof_hash')
                    }
                )
                
                if manifest:
                    mint_somatic_proof(traj.get("proof_hash"), 1, os.environ.get("AEGIS_NETWORK", "local"))
                    
                    # -- REGURGITATION PROTOCOL --
                    print(f"[OUROBOROS] Regurgitating anomaly {traj['id']} to Tier 1 product payload...")
                    try:
                        with open(self.regurgitation_out, 'a') as rf:
                            rf.write(json.dumps(traj) + "\n")
                    except Exception as e:
                        print(f"[OUROBOROS] Regurgitation failed: {e}")
                            
                break # Only process one anomaly per bite to maintain stream velocity

        if not anomaly_found and len(trajectories) > 0:
            print(f"[OUROBOROS] Bite digested nominally. Minting Proof-of-Physics for {len(trajectories)} SOMA...")
            anchor_hash = trajectories[-1].get("proof_hash", "UNKNOWN")
            mint_somatic_proof(anchor_hash, len(trajectories), os.environ.get("AEGIS_NETWORK", "local"))

        # BURN THE MEMORY
        if os.path.exists(self.tmp_out):
            os.remove(self.tmp_out)
        print(f"[OUROBOROS] Bite {self.chunk_size} consumed and burned. Static mass: 0 bytes.")

if __name__ == "__main__":
    daemon = OuroborosStreamDaemon()
    try:
        # Pass False to daemonize if --test flag is used
        test_mode = "--test" in sys.argv
        daemon.boot(daemonize=not test_mode)
    except KeyboardInterrupt:
        print("\n[OUROBOROS] Halting infinite stream.")
