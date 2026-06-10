#!/usr/bin/env python3
import subprocess
import time
import os

CANISTER_ALIAS = "spectra_genesis_backend"
DFX_CWD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "G^G", "spectra_genesis")

def push_manifest_to_icp(body_reference: str, mission_id: str, manifest_hash: str, max_retries: int = 3, network: str = "local"):
    """
    Pushes the Aegis OS Sovereign Manifest cryptographic hash to the ICP Spectra Canister.
    Implements exponential backoff and utilizes distinct Local Daemon Wallets.
    """
    print(f"\n[ICP BRIDGE] Securing Sovereign Decision for '{body_reference}' onchain ({network})...")
    
    # Format the Candid argument for record_aegis_manifest
    candid_arg = f'("SOLIS_PRIME", "{body_reference.upper()}", "{mission_id}", "{manifest_hash}")'
    
    env = os.environ.copy()
    env["DFX_WARNING"] = "-mainnet_plaintext_identity"
    
    for attempt in range(1, max_retries + 1):
        try:
            start_time = time.time()
            result = subprocess.run(
                ["dfx", "canister", "call", CANISTER_ALIAS, "record_aegis_manifest", candid_arg, "--identity", body_reference, "--network", network],
                capture_output=True,
                text=True,
                env=env,
                cwd=DFX_CWD
            )
            latency = int((time.time() - start_time) * 1000)
            
            if result.returncode == 0:
                print(f"[ICP BRIDGE] SUCCESS: Manifest permanently anchored to Ledger of Truth ({latency}ms).")
                return True
            else:
                err_msg = result.stderr.strip()
                print(f"[ICP BRIDGE] WARNING (Attempt {attempt}/{max_retries}): {err_msg}")
                
        except Exception as e:
            print(f"[ICP BRIDGE] ERROR (Attempt {attempt}/{max_retries}): DFX connection failed - {e}")
            
        if attempt < max_retries:
            backoff_secs = 2 ** attempt
            print(f"[ICP BRIDGE] Rate limiting or network error. Retrying in {backoff_secs}s...")
            time.sleep(backoff_secs)
            
    print(f"[ICP BRIDGE] CRITICAL FAILURE: Could not anchor manifest for {mission_id} after {max_retries} attempts.")
    return False

def mint_somatic_proof(run_hash: str, trajectory_count: int, network: str = "local"):
    """
    Calls the spectra_genesis_backend to mint SOMA based on proof-of-physics.
    Tokens are minted directly to The Citadel (default dfx identity).
    """
    print(f"\n[SOMA BRIDGE] Minting Proof-of-Physics for run {run_hash[:8]}... ({trajectory_count} trajectories)")
    
    try:
        citadel_principal = subprocess.run(["dfx", "identity", "get-principal"], capture_output=True, text=True, cwd=DFX_CWD).stdout.strip()
        ledger_principal = subprocess.run(["dfx", "canister", "id", "soma_ledger", "--network", network], capture_output=True, text=True, cwd=DFX_CWD).stdout.strip()
    except Exception as e:
        print(f"[SOMA BRIDGE] ERROR: Unable to retrieve required principals - {e}")
        return False

    candid_arg = f'("SOLIS_PRIME", "{run_hash}", {trajectory_count}, principal "{citadel_principal}", principal "{ledger_principal}")'
    
    env = os.environ.copy()
    try:
        result = subprocess.run(
            ["dfx", "canister", "call", CANISTER_ALIAS, "mint_somatic_proof", candid_arg, "--network", network],
            capture_output=True,
            text=True,
            env=env,
            cwd=DFX_CWD
        )
        if result.returncode == 0:
            print(f"[SOMA BRIDGE] SUCCESS: Minted {trajectory_count} SOMA to Citadel! Response: {result.stdout.strip().replace(chr(10), ' ')}")
            return True
        else:
            print(f"[SOMA BRIDGE] WARNING: Minting Failed - {result.stderr.strip()}")
    except Exception as e:
        print(f"[SOMA BRIDGE] ERROR: Mint execution failed - {e}")
    
    return False

def fund_daemon_from_citadel(daemon_principal: str, amount: float = 10.0, network: str = "local"):
    """
    The Citadel transfers SOMA to a newly spawned daemon to unstake the gating lock.
    """
    amount_e8s = int(amount * 100_000_000)
    print(f"\n[SOMA BRIDGE] Citadel funding Daemon {daemon_principal} with {amount} SOMA...")
    
    candid_arg = f'(record {{ to = record {{ owner = principal "{daemon_principal}"; subaccount = null; }}; amount = {amount_e8s}; fee = null; memo = null; from_subaccount = null; created_at_time = null; }})'
    
    env = os.environ.copy()
    try:
        result = subprocess.run(
            ["dfx", "canister", "call", "soma_ledger", "icrc1_transfer", candid_arg, "--network", network],
            capture_output=True,
            text=True,
            env=env,
            cwd=DFX_CWD
        )
        if result.returncode == 0:
            print(f"[SOMA BRIDGE] SUCCESS: Daemon funded! Response: {result.stdout.strip().replace(chr(10), ' ')}")
            return True
        else:
            print(f"[SOMA BRIDGE] WARNING: Funding failed - {result.stderr.strip()}")
    except Exception as e:
         print(f"[SOMA BRIDGE] ERROR: Funding execution failed - {e}")
    return False

