#!/usr/bin/env python3
"""
AEGIS OS: Somatic Binary Memory (.soma.bin) Indexer & Fast Telemetry Recall.

Replaces slow JSON parsing ("thermodynamically meh") with zero-copy,
64-byte L1-cache aligned binary memory mapping for microsecond recall
during Dark Window anomaly events.
"""

import os
import struct
import mmap
import hashlib
from typing import Dict, Any, Optional, List, Tuple

HEADER_FORMAT = "<4sHHQQ32s8s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT) # Exactly 64 bytes

FRAME_FORMAT = "<d6f2fQ16s"
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)   # Exactly 64 bytes

assert HEADER_SIZE == 64, f"Header size is {HEADER_SIZE}, must be 64 bytes"
assert FRAME_SIZE == 64, f"Frame size is {FRAME_SIZE}, must be 64 bytes"

MAGIC_BYTES = b"SOMA"
SPEC_VERSION = 1

BODY_TYPE_MAP = {
    "titanhauler": 1,
    "humanoid": 2,
    "autonomous_car": 3,
    "satellite": 4,
    "maven": 5,
    "submarine": 6,
    "autonomous_boat": 7,
    "drone": 8,
    "drone_daemon": 8,
    "mars": 9,
    "orbital": 10,
    "terran": 11,
    "mycelial": 12,
    "atheric": 13,
    "plutonian": 14,
    "asteroid": 15,
    "celestial": 16,
    "energy": 17,
    "josephson": 18,
    "reactor": 19,
    "tokamak": 20,
    "swing": 21,
    "materials": 22,
    "plasma_facing": 23,
    "forge": 24,
    "tribology": 25,
    "inverse_properties": 26,
    "autolab": 27,
    "grasp": 28,
    "fleet": 29,
    "atheric": 13,  # same id as RF substrate family
    "unknown": 0
}

REVERSE_BODY_MAP = {v: k for k, v in BODY_TYPE_MAP.items()}


def extract_domain_invariants(f: Dict[str, Any], body_type: str) -> Tuple[float, float]:
    """
    Extracts domain-native physical invariants into the 2x f32 control invariant slot.
    Eliminates semantic collapse across body domains.
    """
    b = body_type.lower()
    if b == "humanoid":
        force_torque = float(f.get("joint_torque_max", f.get("joint_torque_knee_l_pct", f.get("force", 0.0))))
        residual = float(f.get("zmp_error_m", f.get("slip_ratio", f.get("residual", 0.0))))
    elif b == "drone":
        force_torque = float(f.get("atheric_coherence", f.get("rotor_thrust_1", 1.0)))
        residual = float(f.get("lateral_position_drift_m", f.get("gg_ekf_divergence", 0.0)))
    elif b == "satellite":
        force_torque = float(f.get("battery_pct", f.get("rtg_power_w", f.get("power_rails_v", 28.0))))
        residual = float(f.get("omega_mag", f.get("body_temp_c", f.get("attitude_err_deg", 0.0))))
    elif b == "submarine":
        force_torque = float(f.get("depth_m", f.get("pressure_bar", 0.0)))
        residual = float(f.get("thermocline_gradient", f.get("sonar_refraction_err", 0.0)))
    elif b == "titanhauler":
        force_torque = float(f.get("pressure_pa", f.get("brake_temp_c", f.get("payload_mass_kg", 0.0))))
        residual = float(f.get("yield_pa", f.get("compaction", f.get("wheel_slip", 0.0))))
    elif b == "autonomous_car":
        force_torque = float(f.get("steering_angle_deg", f.get("brake_pressure", 0.0)))
        residual = float(f.get("tire_slip_ratio", f.get("hydroplane_risk", f.get("slam_slip_m", 0.0))))
    elif b == "autonomous_boat":
        force_torque = float(f.get("speed_knots", f.get("thrust_n", 0.0)))
        residual = float(f.get("wave_height_m", f.get("cavitation_idx", 0.0)))
    elif b == "maven":
        force_torque = float(f.get("fuel_kg", f.get("friis_path_loss", f.get("battery_pct", 100.0))))
        residual = float(f.get("omega_mag", f.get("target_offset_deg", f.get("hop_channel", 0.0))))
    elif b in ("materials", "inverse_properties"):
        force_torque = float(f.get("von_mises_stress_mpa", f.get("force", 0.0)))
        residual = float(f.get("safety_margin", f.get("residual", 0.0)))
    elif b == "plasma_facing":
        force_torque = float(f.get("thermal_stress_mpa", f.get("force", 0.0)))
        residual = float(f.get("ablation_recession_depth_mm", f.get("residual", 0.0)))
    elif b == "forge":
        force_torque = float(f.get("forge_aligned_peak_stress_mpa", f.get("force", 0.0)))
        residual = float(f.get("forge_aligned_safety_margin", f.get("residual", 0.0)))
    elif b == "tribology":
        force_torque = float(f.get("flash_temperature_k", f.get("force", 0.0)))
        residual = float(f.get("cumulative_galling_wear_um", f.get("residual", 0.0)))
    elif b in ("grasp", "autolab"):
        force_torque = float(f.get("final_commanded_force_n", f.get("force", 0.0)))
        residual = float(f.get("tactile_friction_margin", f.get("slip_velocity_m_s", f.get("residual", 0.0))))
    elif b == "fleet":
        force_torque = float(f.get("calculated_stopping_distance_m", f.get("force", 0.0)))
        residual = float(f.get("comms_latency_ms", f.get("residual", 0.0)))
    elif b == "atheric":
        force_torque = float(f.get("average_snr_db", f.get("force", 0.0)))
        residual = float(f.get("channel_resonance_coherence", f.get("residual", 0.0)))
    else:
        force_torque = float(f.get("force", f.get("torque", f.get("beta", 0.0))))
        residual = float(f.get("residual", f.get("slip", f.get("z_shear", 0.0))))

    return force_torque, residual


def pack_soma_binary_file(
    out_path: str,
    body_type: str,
    trajectories_data: List[Dict[str, Any]],
    master_proof_hex: str = ""
) -> Optional[str]:
    """
    Packs trajectory data into a 64-byte aligned .soma.bin binary telemetry memory file.
    Rejects zero-frame hollow banks to enforce zero-trust data integrity.
    """
    body_id = BODY_TYPE_MAP.get(body_type.lower(), 0)
    traj_count = len(trajectories_data)
    
    total_frames = 0
    all_frame_bytes = []
    
    for traj in trajectories_data:
        frames_list = traj.get("data", [])
        proof_hex = traj.get("proof_hash", "")
        
        # Valid proof hex check
        try:
            proof_bytes_16 = bytes.fromhex(proof_hex[:32]) if len(proof_hex) >= 32 else b"\x00" * 16
        except ValueError:
            proof_bytes_16 = hashlib.sha256(proof_hex.encode("utf-8")).digest()[:16]
            
        if len(proof_bytes_16) < 16:
            proof_bytes_16 = proof_bytes_16.ljust(16, b"\x00")
            
        for i, f in enumerate(frames_list):
            total_frames += 1
            t = float(f.get("t", i * 0.001))
            
            pos = f.get("center", f.get("pos", [0.0, 0.0, 0.0]))
            if isinstance(pos, (int, float)):
                pos = [float(pos), 0.0, 0.0]
            elif len(pos) < 3:
                pos = list(pos) + [0.0] * (3 - len(pos))
                
            vel = f.get("vel", [0.0, 0.0, 0.0])
            if isinstance(vel, (int, float)):
                vel = [float(vel), 0.0, 0.0]
            elif len(vel) < 3:
                vel = list(vel) + [0.0] * (3 - len(vel))
                
            force_torque, residual = extract_domain_invariants(f, body_type)
            flags = 1 if f.get("is_anomaly", False) else 0
            
            frame_bin = struct.pack(
                FRAME_FORMAT,
                t,
                float(pos[0]), float(pos[1]), float(pos[2]),
                float(vel[0]), float(vel[1]), float(vel[2]),
                force_torque, residual,
                flags,
                proof_bytes_16
            )
            all_frame_bytes.append(frame_bin)

    # Reject zero-frame hollow banks (no hollow shell files)
    if total_frames == 0 or not all_frame_bytes:
        return None
            
    # Calculate non-zero master proof seal over binary frames
    payload_hash = hashlib.sha256(b"".join(all_frame_bytes)).hexdigest()
    try:
        master_proof_32 = bytes.fromhex(master_proof_hex[:64]) if len(master_proof_hex) >= 64 else bytes.fromhex(payload_hash)
    except ValueError:
        master_proof_32 = bytes.fromhex(payload_hash)
        
    if len(master_proof_32) < 32:
        master_proof_32 = master_proof_32.ljust(32, b"\x00")
        
    master_proof_hex = master_proof_32.hex()
        
    header_bin = struct.pack(
        HEADER_FORMAT,
        MAGIC_BYTES,
        SPEC_VERSION,
        body_id,
        traj_count,
        total_frames,
        master_proof_32,
        b"\x00" * 8
    )
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as fp:
        fp.write(header_bin)
        for fb in all_frame_bytes:
            fp.write(fb)
            
    return master_proof_hex


class SomaticBinaryMemory:
    """
    Zero-Copy Fast Binary Telemetry Memory Indexer.
    Maps .soma.bin files into memory and accesses binary frames at microsecond speed.
    """
    def __init__(self, corpus_root: str):
        self.corpus_root = corpus_root
        self._path_cache: Dict[str, str] = {}

    def read_soma_binary_header(self, bin_path: str) -> Optional[Dict[str, Any]]:
        """Reads 64-byte header of a .soma.bin file instantly."""
        if not os.path.exists(bin_path) or os.path.getsize(bin_path) < HEADER_SIZE + FRAME_SIZE:
            return None # Rejects hollow banks under size header + 1 frame
            
        with open(bin_path, "rb") as f:
            header_data = f.read(HEADER_SIZE)
            
        magic, ver, body_id, traj_count, frame_count, proof_bytes, _ = struct.unpack(
            HEADER_FORMAT, header_data
        )
        if magic != MAGIC_BYTES or frame_count == 0:
            return None
            
        return {
            "version": ver,
            "body_type": REVERSE_BODY_MAP.get(body_id, "unknown"),
            "trajectory_count": traj_count,
            "frame_count": frame_count,
            "proof_hash": proof_bytes.hex(),
            "path": bin_path
        }

    def _find_newest_bin(self, body_type: str, condition: str) -> Optional[str]:
        cache_key = f"{body_type}:{condition}"
        if cache_key in self._path_cache and os.path.exists(self._path_cache[cache_key]):
            return self._path_cache[cache_key]

        body_dir = os.path.join(self.corpus_root, body_type)
        if not os.path.exists(body_dir):
            return None

        bin_files = []
        stack = [body_dir]
        condition_lower = condition.lower()
        
        while stack:
            curr = stack.pop()
            try:
                with os.scandir(curr) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.name.endswith(".soma.bin"):
                            bin_files.append(entry.path)
            except OSError:
                continue

        matched_files = [f for f in bin_files if condition_lower in f.lower()]
        if not matched_files:
            matched_files = bin_files

        if not matched_files:
            return None

        # Filter out any hollow 64-byte banks
        valid_bins = [f for f in matched_files if os.path.getsize(f) >= HEADER_SIZE + FRAME_SIZE]
        if not valid_bins:
            return None

        newest_bin = max(valid_bins, key=os.path.getmtime)
        self._path_cache[cache_key] = newest_bin
        return newest_bin

    def fetch_latest_somatic_frame(self, body_type: str, condition: str = "nominal") -> Optional[Dict[str, Any]]:
        """
        Fast zero-copy memory lookup for the specified body and condition.
        Returns recalled somatic trajectory context in microseconds.
        """
        newest_bin = self._find_newest_bin(body_type, condition)
        if not newest_bin:
            return None

        meta = self.read_soma_binary_header(newest_bin)
        if not meta:
            return None

        file_size = os.path.getsize(newest_bin)
        if file_size < HEADER_SIZE + FRAME_SIZE:
            return meta

        # Zero-copy mmap last frame read
        with open(newest_bin, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                last_frame_offset = file_size - FRAME_SIZE
                frame_bytes = mm[last_frame_offset:file_size]
                
                t, px, py, pz, vx, vy, vz, force_inv, res_inv, flags, proof_seal = struct.unpack(
                    FRAME_FORMAT, frame_bytes
                )
                
                meta["last_frame"] = {
                    "t": t,
                    "position": [px, py, pz],
                    "velocity": [vx, vy, vz],
                    "force_torque": force_inv,
                    "residual_slip": res_inv,
                    "flags": flags,
                    "rolling_seal": proof_seal.hex()
                }

        return meta
