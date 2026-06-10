#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import logging

AEGIS_ROOT = os.path.dirname(os.path.abspath(__file__))
SPECTRUM_ROOT = os.path.dirname(AEGIS_ROOT)
GENESIS_CORE_DIR = os.path.join(SPECTRUM_ROOT, "G^G", "genesis_core")

# The Pulse Interval (in seconds)
# Defaulted to 30 mins (1800s). For testing, we might want this smaller, but the Swarm acts in heavy intervals.
PULSE_INTERVAL_SECONDS = 30 * 60

# Configure rotating file logging alongside console output
import logging.handlers
log_file = os.path.join(AEGIS_ROOT, "pulse.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ',
    handlers=[
        logging.handlers.RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PulseReactor")

def run_body_sweep():
    logger.info("Phase 1: Waking Physics Generation (body_sweep.rs)")
    
    # Let's target exactly 100 sweeps to keep it lightweight on every pulse 
    # but still enough variance for the daemons to pick a novel memory.
    try:
        result = subprocess.run(
            ["cargo", "run", "--release", "--bin", "body_sweep", "--", "100", "--root", "../../data/corpus"],
            cwd=GENESIS_CORE_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("Genesis Core Substrate Generated.")
            return True
        else:
            logger.warning(f"body_sweep failed.\n{result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Could not execute body_sweep: {e}")
        return False

def run_fleet_commander():
    logger.info("Phase 2: Orchestrating the Swarm (fleet_commander.py)")
    fleet_cmd_path = os.path.join(AEGIS_ROOT, "fleet_commander.py")
    try:
        result = subprocess.run(
            ["python3", fleet_cmd_path],
            cwd=AEGIS_ROOT,
            capture_output=False # We want to see it print live to console.
        )
        if result.returncode == 0:
            logger.info("Swarm Orchestration Complete. All Decisions Anchored.")
            return True
        else:
            logger.warning(f"fleet_commander returned {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"Could not execute fleet_commander: {e}")
        return False

def heartbeat_loop(interval, test_mode=False):
    pulse_number = 1
    logger.info("=" * 65)
    logger.info("SOVEREIGN PULSE REACTOR [ONLINE]")
    logger.info(f"Rate: {interval} seconds")
    logger.info("Physics Module: G^G (Native Rust)")
    logger.info("Reasoning Module: Kid Cosmo (MLX)")
    logger.info("Anchoring Module: ICP Spectra Genesis (DFX Mainnet)")
    logger.info("=" * 65)
    
    try:
        while True:
            logger.info(f">>>>> Initiating Pulse Sector {pulse_number} <<<<<")
            start = time.time()
            
            # Step 1: Synthesize Physics Memory
            run_body_sweep()
            
            # Step 2: Wake the Swarm to digest the new physical truth
            run_fleet_commander()
            
            duration = time.time() - start
            logger.info(f">>>>> Pulse {pulse_number} Concluded in {duration:.1f}s <<<<<")
            
            if test_mode:
                logger.info("Test Mode Complete. Sovereign Reactor Halting.")
                break
                
            logger.info(f"Deep Sleep... Next sequence in {interval / 60:.1f} minutes.")
            
            pulse_number += 1
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.warning("External Override Detected. Shutting Down the Swarm.")
        sys.exit(0)

if __name__ == "__main__":
    interval = PULSE_INTERVAL_SECONDS
    test_mode = "--test-mode" in sys.argv
    
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print("Invalid interval provided, defaulting to 1800s.")
            
    heartbeat_loop(interval, test_mode)
