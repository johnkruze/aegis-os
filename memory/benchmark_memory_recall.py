#!/usr/bin/env python3
"""
benchmark_memory_recall.py: Direct thermodynamic benchmark comparing legacy JSON parsing
against 64-byte zero-copy binary mmap memory recall.
"""

import os
import sys
import time
import json
import mmap
import struct

AEGIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECTRUM_ROOT = os.path.dirname(AEGIS_ROOT)
AEGIS_MEMORY = os.path.join(AEGIS_ROOT, "memory")

if AEGIS_MEMORY not in sys.path:
    sys.path.append(AEGIS_MEMORY)

from soma_binary_memory import SomaticBinaryMemory, FRAME_FORMAT, FRAME_SIZE, HEADER_SIZE

def run_benchmark():
    corpus_root = os.path.join(SPECTRUM_ROOT, "data", "corpus")
    binary_mem = SomaticBinaryMemory(corpus_root)

    print("====================================================================")
    print("  AEGIS OS: THERMODYNAMIC MEMORY RECALL BENCHMARK")
    print("  Direct Comparison: Legacy JSON Parse vs 64B Zero-Copy Binary mmap")
    print("====================================================================\n")

    test_files = [
        ("TITANHAULER", os.path.join(corpus_root, "titanhauler", "2026-03-10", "nominal", "humanoid_monte_carlo_1773179305_100.json")),
        ("HUMANOID", os.path.join(corpus_root, "humanoid", "2026-03-10", "nominal", "humanoid_monte_carlo_1773179305_100.json")),
        ("MARS (100k)", os.path.join(corpus_root, "mars", "mars_monte_carlo_1785876189_100000.json")),
        ("PLUTONIAN (100k)", os.path.join(corpus_root, "plutonian", "plutonian_monte_carlo_1785876428_100000.json")),
        ("ORBITAL (1k)", os.path.join(corpus_root, "orbital", "orbital_monte_carlo_1772928680_1000.json")),
    ]

    for label, json_path in test_files:
        if not os.path.exists(json_path):
            continue

        bin_path = json_path.rsplit(".", 1)[0] + ".soma.bin"
        if not os.path.exists(bin_path):
            continue

        json_size = os.path.getsize(json_path) / 1024.0 / 1024.0 # MB
        bin_size = os.path.getsize(bin_path) / 1024.0 / 1024.0   # MB

        # Benchmark 1: Legacy JSON Parsing
        t0 = time.perf_counter()
        with open(json_path, 'r') as f:
            data_json = json.load(f)
            last_traj_json = data_json.get("trajectories", [{}])[-1]
        t_json = (time.perf_counter() - t0) * 1_000_000.0 # microseconds

        # Benchmark 2: Zero-Copy 64B Binary mmap
        t1 = time.perf_counter()
        with open(bin_path, 'rb') as f:
            size = os.path.getsize(bin_path)
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                frame_bytes = mm[size - FRAME_SIZE:size]
                last_frame = struct.unpack(FRAME_FORMAT, frame_bytes)
        t_bin = (time.perf_counter() - t1) * 1_000_000.0 # microseconds

        speedup = (t_json / t_bin) if t_bin > 0 else 0
        
        print(f"Memory Bank: [{label}] (JSON: {json_size:.1f} MB | BIN: {bin_size:.1f} MB)")
        print(f"  ├─ 64B Zero-Copy mmap Read: {t_bin:10.2f} µs")
        print(f"  ├─ Legacy JSON Parse Time:  {t_json:10.2f} µs")
        print(f"  └─ Thermodynamic Speedup:   {speedup:10.1f}x FASTER\n")

if __name__ == "__main__":
    run_benchmark()
