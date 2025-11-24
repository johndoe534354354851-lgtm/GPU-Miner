#!/usr/bin/env python3
"""GPU Miner - Main Entry Point"""

import sys
import os
from pathlib import Path

# Ensure the script directory is in Python's module search path
# This allows imports to work regardless of where the script is run from
script_dir = Path(__file__).parent.resolve()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import time
import signal
import logging
from core.logger import setup_logging
from core.config import config
from core.miner_manager import MinerManager

def main():
    # Initialize logging
    setup_logging()
    
    logging.info("=== GPU Miner Starting ===")
    logging.info(f"API Base: {config.get('api_base')}")
    
    # Create and start miner
    manager = MinerManager()
    
    # Setup signal handler for clean shutdown
    def signal_handler(sig, frame):
        logging.info("\nShutdown requested by user")
        manager.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        manager.start()
        # Keep main thread alive
        while manager.running:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nShutdown requested by user")
    finally:
        logging.info("Shutting down...")
        manager.stop()

if __name__ == "__main__":
    main()
