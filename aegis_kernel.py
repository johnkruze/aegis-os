#!/usr/bin/env python3
"""
AEGIS OS: Sovereign Kernel
The unified object-oriented base class for all Sovereign Bodies.
"""

import sys
import os
import json
import time

AEGIS_ROOT = os.path.dirname(os.path.abspath(__file__))
SPECTRUM_ROOT = os.path.dirname(AEGIS_ROOT)
KID_COSMO_RUNTIME = os.path.join(SPECTRUM_ROOT, "origins", "Kid Cosmo", "runtime")
AEGIS_MEMORY = os.path.join(AEGIS_ROOT, "memory")

# Inject paths
if KID_COSMO_RUNTIME not in sys.path: sys.path.append(KID_COSMO_RUNTIME)
if AEGIS_MEMORY not in sys.path: sys.path.append(AEGIS_MEMORY)

from reasoning_agent import ReasoningAgent
from corpus_indexer import CorpusMemory

# Link ICP
ICP_BRIDGE_PATH = os.path.join(AEGIS_ROOT, "integration")
if ICP_BRIDGE_PATH not in sys.path: sys.path.append(ICP_BRIDGE_PATH)
try:
    from icp_bridge import push_manifest_to_icp
    HAS_ICP = True
except ImportError:
    HAS_ICP = False

class AegisSystemKernel:
    def __init__(self, persona_name: str, body_reference: str):
        """
        persona_name: The display name (e.g. "Titanhauler OS")
        body_reference: The corpus lookup key (e.g. "titanhauler")
        """
        self.persona_name = persona_name
        self.body_reference = body_reference
        
        print(f"Initializing {self.persona_name} [Aegis System Kernel]...")
        
        self.staked = False
        self.principal_id = "UNKNOWN"
        self.soma_balance = 0.0
        self.provision_sovereign_identity()
        
        self.brain = ReasoningAgent()
        self.corpus_root = os.path.join(SPECTRUM_ROOT, "data", "corpus")
        self.memory = CorpusMemory(self.corpus_root)

    def provision_sovereign_identity(self):
        print(f"  [+] Provisioning Sovereign Identity for: {self.body_reference}")
        dfx_cwd = os.path.join(SPECTRUM_ROOT, "G^G", "spectra_genesis")
        import subprocess
        import re
        
        # Ensure identity exists
        subprocess.run(["dfx", "identity", "new", self.body_reference], capture_output=True)
        
        network_target = os.environ.get("AEGIS_NETWORK", "local")
        
        res = subprocess.run(["dfx", "identity", "get-principal", "--identity", self.body_reference], capture_output=True, text=True)
        self.principal_id = res.stdout.strip()
        print(f"  [+] Principal ID: {self.principal_id} ({network_target})")
        
        try:
            soma_id = subprocess.run(["dfx", "canister", "id", "soma_ledger", "--network", network_target], capture_output=True, text=True, cwd=dfx_cwd).stdout.strip()
            if soma_id:
                balance_arg = f'(record {{ owner = principal "{self.principal_id}"; }})'
                res_bal = subprocess.run(["dfx", "canister", "call", "soma_ledger", "icrc1_balance_of", balance_arg, "--network", network_target], capture_output=True, text=True, cwd=dfx_cwd)
                match = re.search(r'\((\d+(?:_\d+)*)\s*:\s*nat\)', res_bal.stdout)
                if match:
                    balance_e8s = int(match.group(1).replace('_', ''))
                    self.soma_balance = balance_e8s / 100_000_000.0
                    print(f"  [+] SOMA Stake: {self.soma_balance} SOMA")
                    if self.soma_balance >= 1.0:
                        self.staked = True
                    else:
                        print(f"  [!] Daemon lacks minimum SOMA stake ({self.soma_balance} SOMA). Requesting Citadel Funding...")
                        if HAS_ICP:
                            try:
                                from integration.icp_bridge import fund_daemon_from_citadel
                                success = fund_daemon_from_citadel(self.principal_id, 10.0, network_target)
                                if success:
                                    self.staked = True
                                    self.soma_balance += 10.0
                                    print("  [+] SOMA Stake provisioned successfully. Gating Lock removed.")
                                else:
                                    print("  [X] CRITICAL: Citadel funding failed. Execution blocked.")
                            except Exception as e:
                                print(f"  [X] CRITICAL: Failed to invoke Citadel funding: {e}")
                        else:
                            print("  [X] CRITICAL: ICP Bridge inactive. Cannot request funds.")
                else:
                    print("  [X] CRITICAL: Could not parse SOMA balance.")
            else:
                print("  [X] CRITICAL: Could not locate soma_ledger canister.")
        except Exception as e:
            print(f"  [X] Identity check failed: {e}")

    def fetch_somatic_memory(self, condition: str = "nominal") -> dict:

        print(f"Indexing Somatic Memory for '{self.body_reference}'...")
        memory_trajectory = self.memory.find_latest_trajectory(self.body_reference, condition=condition)
        
        trajectory_context = {}
        if memory_trajectory:
            print(f"  -> Recalled memory: {memory_trajectory.get('id', 'UNKNOWN')}")
            trajectory_context = {
                "parent_trajectory_id": memory_trajectory.get('id'),
                "scenario": memory_trajectory.get('scenario'),
                "score": memory_trajectory.get('score'),
                "physics_proof": memory_trajectory.get('proof_hash')
            }
        else:
            print("  -> No memory found. Operating with zero prior.")
        return trajectory_context

    def trigger_dark_window(self, mission_id: str, environment: str, live_telemetry: dict, anomaly_desc: str, trajectory_context: dict):
        if not self.staked:
            print(f"\n[BLOCKED] {self.persona_name} Cannot Execute: Insufficient SOMA Stake.")
            return None

        # Extract dynamic memory link or fallback to a timestamp to ensure uniqueness
        import datetime
        iso_stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        local_id = trajectory_context.get("parent_trajectory_id", f"NIL_{iso_stamp}")
        unique_mission = f"{mission_id}_{local_id}_{iso_stamp}"

        print("\n[!] DARK WINDOW ANOMALY DETECTED [!]")
        print("Engaging Sovereign Reasoning Protocol...\n")
        
        if os.environ.get("OUROBOROS_ENABLED") == "1":
            print("  [+] OUROBOROS KERNEL ACTIVE: Bypassing Generative Reasoning...")
            print(f"  [+] Initiating 1000Hz Dead-Reckoning Integration ({environment})...")
            import subprocess
            genesis_core_bin = os.path.join(SPECTRUM_ROOT, "G^G", "target", "release", "ouroboros_kernel")
            if os.path.exists(genesis_core_bin):
                res = subprocess.run([genesis_core_bin, environment, "60.0"], capture_output=True, text=True)
                if res.returncode == 0:
                    manifest = json.loads(res.stdout.strip())
                    manifest["mission_id"] = unique_mission
                    manifest["anomaly_desc"] = anomaly_desc
                else:
                    print("  [X] Ouroboros binary failed. Falling back to Generative LLM.")
                    manifest = self.brain.generate_manifest(
                        mission_id=unique_mission, environment=environment,
                        telemetry_snapshot=live_telemetry, anomaly_description=anomaly_desc,
                        epistemic_isolation=True, trajectory_context=trajectory_context
                    )
            else:
                print("  [X] Ouroboros binary missing. Run `cargo build --release` in G^G.")
                manifest = {}
        else:
            manifest = self.brain.generate_manifest(
                mission_id=unique_mission,
                environment=environment,
                telemetry_snapshot=live_telemetry,
                anomaly_description=anomaly_desc,
                epistemic_isolation=True,
                trajectory_context=trajectory_context
            )
        
        print("\n=== AEGIS DECISION MANIFEST ===")
        manifest_str = json.dumps(manifest, indent=2)
        print(manifest_str)
        
        # Hash the Manifest for Onchain Sealing
        import hashlib
        manifest_hash = hashlib.sha256(manifest_str.encode('utf-8')).hexdigest()
        
        out_name = f"manifest_{self.body_reference}_{int(time.time())}.json"
        out_dir = os.path.join(AEGIS_ROOT, "manifests")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, 'w') as f:
            f.write(manifest_str)
            
        print(f"\nManifest local JSON sealed and written to: {out_path}")
        print(f"Manifest SHA-256 Fingerprint: {manifest_hash}")
        
        # Dispatch to Internet Computer (The Decentralized Finishing Move)
        if HAS_ICP:
            network_target = os.environ.get("AEGIS_NETWORK", "local")
            push_manifest_to_icp(self.body_reference, unique_mission, manifest_hash, network=network_target)
            
        print(f"\n{self.persona_name}: Sovereign Cycle Complete.")
        return manifest

    def boot(self):
        """
        Override this in the child class to provide specific telemetry and anomaly logic.
        """
        raise NotImplementedError("Bodies must implement the boot sequence.")
