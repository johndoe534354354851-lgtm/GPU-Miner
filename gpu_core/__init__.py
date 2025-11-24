"""
GPU Core Module Loader

Automatically loads the correct pre-compiled binary for your platform.
"""
import sys
import os
from pathlib import Path

# Determine platform
if sys.platform == 'win32':
    platform_dir = 'windows'
    ext = '.pyd'
elif sys.platform.startswith('linux'):
    platform_dir = 'linux'
    ext = '.so'
elif sys.platform == 'darwin':
    platform_dir = 'macos'
    ext = '.so'
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

# Get Python version info
py_version = f"cp{sys.version_info.major}{sys.version_info.minor}"

# Build path to compiled modules
bin_dir = Path(__file__).parent / 'bin' / platform_dir

# Add to path so imports work
if bin_dir.exists():
    sys.path.insert(0, str(bin_dir))
    
    # Try to import
    try:
        # Import will find .pyd/.so files in bin_dir
        from engine import GPUEngine
        from kernels import CUDA_SOURCE
        
        GPU_AVAILABLE = True
        
    except ImportError as e:
        GPU_AVAILABLE = False
        GPUEngine = None
        CUDA_SOURCE = None
        print(f"Warning: Could not load GPU module for {platform_dir}: {e}")
        print(f"GPU acceleration not available. Falling back to CPU mode.")
else:
    GPU_AVAILABLE = False
    GPUEngine = None
    CUDA_SOURCE = None
    print(f"Warning: No compiled GPU module found for {platform_dir}")
    print(f"Expected location: {bin_dir}")

__all__ = ['GPUEngine', 'CUDA_SOURCE', 'GPU_AVAILABLE']
