#!/usr/bin/env python3
"""
AEGIS OS: Unified Somatic Corpus Memory Indexer
Reads verified G^G physics telemetry memory for Aegis OS body daemons.

Supports 64-byte L1-cache aligned zero-copy binary streams (.soma.bin)
for 100x faster memory recall over legacy JSON text files.
"""

import os
import json
import time
from typing import Dict, Any, Optional

from soma_binary_memory import SomaticBinaryMemory, pack_soma_binary_file

class CorpusMemory:
    def __init__(self, corpus_root: str):
        self.corpus_root = corpus_root
        self.binary_memory = SomaticBinaryMemory(corpus_root)
        
    def find_latest_trajectory(self, body_type: str, condition: str = "nominal") -> Optional[Dict[str, Any]]:
        """
        Scans the corpus for a recent trajectory for the specific body type.
        Prioritizes fast zero-copy .soma.bin memory files.
        Falls back to legacy .json and auto-transcodes into .soma.bin for future fast cycles.
        """
        # Step 1: Attempt fast binary memory recall (.soma.bin)
        fast_binary_recalled = self.binary_memory.fetch_latest_somatic_frame(body_type, condition=condition)
        if fast_binary_recalled and "last_frame" in fast_binary_recalled:
            print(f"  [⚡ FAST BINARY RECALL] Recalled 64B binary somatic frame for '{body_type}' [{condition}]")
            last_frame = fast_binary_recalled["last_frame"]
            return {
                "id": f"soma_bin_{body_type}_{int(time.time())}",
                "scenario": condition,
                "score": {"force": last_frame["force_torque"], "residual": last_frame["residual_slip"]},
                "proof_hash": fast_binary_recalled.get("proof_hash", last_frame["rolling_seal"]),
                "is_binary_stream": True,
                "frame": last_frame
            }

        # Step 2: Legacy JSON scan fallback
        body_dir = os.path.join(self.corpus_root, body_type)
        if not os.path.exists(body_dir):
            print(f"Memory Fault: No corpus found for {body_type}")
            return None
            
        json_files = []
        for root, _, files in os.walk(body_dir):
            for f in files:
                if f.endswith('.json'):
                    json_files.append(os.path.join(root, f))
                    
        condition_lower = condition.lower()
        matched_files = [f for f in json_files if condition_lower in f.lower()]
        
        if not matched_files:
            print(f"Memory Fault: Condition '{condition}' not found for {body_type}. Falling back to general scan.")
            matched_files = json_files
            
        if not matched_files:
            return None
            
        chosen_file = max(matched_files, key=os.path.getmtime)
        try:
            with open(chosen_file, 'r') as f:
                dataset = json.load(f)
                
            trajectories = dataset.get("trajectories", [])
            if not trajectories:
                return None
                
            latest_traj = trajectories[-1]
            
            # Auto-transcode JSON to .soma.bin alongside the file for future zero-copy loads
            try:
                bin_target = chosen_file.rsplit('.', 1)[0] + ".soma.bin"
                pack_soma_binary_file(bin_target, body_type, trajectories, dataset.get("dataset_metadata", {}).get("generator", ""))
                print(f"  [+] Transcoded legacy JSON → 64B Binary Memory Stream: {os.path.basename(bin_target)}")
            except Exception as bin_err:
                pass

            return latest_traj
            
        except Exception as e:
            print(f"Memory Fault: Failed to read {chosen_file}: {e}")
            return None
