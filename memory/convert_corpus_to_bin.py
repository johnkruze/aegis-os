#!/usr/bin/env python3
"""
convert_corpus_to_bin.py: Converts legacy JSON trajectory files in data/corpus/
into 64-byte L1-cache aligned .soma.bin zero-copy binary telemetry memory banks.
"""

import os
import json
import time
from soma_binary_memory import pack_soma_binary_file

SPECTRUM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_ROOT = os.path.join(SPECTRUM_ROOT, "data", "corpus")

def transcode_corpus():
    print(f"====================================================================")
    print(f"  TRANSCODING LEGACY CORPUS JSON → SOMATIC 64B BINARY STREAMS (.soma.bin)")
    print(f"  Target: {CORPUS_ROOT}")
    print(f"====================================================================\n")
    
    total_json = 0
    total_bin = 0
    start_time = time.time()

    for root, dirs, files in os.walk(CORPUS_ROOT):
        for f in files:
            if f.endswith(".json") and not f.endswith(".soma.bin"):
                total_json += 1
                json_path = os.path.join(root, f)
                bin_path = json_path.rsplit(".", 1)[0] + ".soma.bin"

                try:
                    with open(json_path, "r") as fp:
                        dataset = json.load(fp)

                    trajectories = dataset.get("trajectories", [])
                    if not trajectories:
                        continue

                    # Identify body type from path or metadata
                    body_type = "unknown"
                    path_parts = root.split(os.sep)
                    for p in path_parts:
                        p_clean = p.lower()
                        if p_clean in ["titanhauler", "humanoid", "autonomous_car", "satellite", "maven", "submarine", "autonomous_boat", "drone", "mars", "orbital", "terran", "mycelial", "atheric", "plutonian", "asteroid", "celestial", "energy", "josephson", "reactor", "tokamak", "swing"]:
                            body_type = p_clean
                            break

                    master_proof = dataset.get("dataset_metadata", {}).get("generator", "")
                    proof_hex = pack_soma_binary_file(bin_path, body_type, trajectories, master_proof)
                    
                    json_size = os.path.getsize(json_path)
                    bin_size = os.path.getsize(bin_path)
                    ratio = (1.0 - bin_size / json_size) * 100 if json_size > 0 else 0
                    
                    total_bin += 1
                    print(f"  ✔ [PACKED] {os.path.relpath(bin_path, CORPUS_ROOT)}")
                    print(f"     JSON: {json_size/1024:.1f} KB → BIN: {bin_size/1024:.1f} KB ({ratio:.1f}% space compression)")
                except Exception as e:
                    print(f"  ✘ [FAIL] {json_path}: {e}")

    elapsed = time.time() - start_time
    print(f"\n====================================================================")
    print(f"  TRANSCODING COMPLETE")
    print(f"  Processed {total_bin}/{total_json} files in {elapsed:.2f}s")
    print(f"====================================================================")

if __name__ == "__main__":
    transcode_corpus()
