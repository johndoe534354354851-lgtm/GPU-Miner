# Publishing Strategy for GPU Miner

## Approach: Private GPU Module + Public Core

Keep the GPU acceleration code private while sharing the infrastructure.

### Step 1: Update .gitignore for Public Repo

Add to `.gitignore`:
```
# GPU Core (proprietary)
gpu_core/
!gpu_core/__init__.py
!gpu_core/README.md
```

This excludes GPU code but keeps:
- An `__init__.py` stub  
- A README explaining how to get the GPU module

### Step 2: Create GPU Module Stubs

**gpu_core/__init__.py** (public):
```python
"""
GPU Acceleration Module

This module contains proprietary CUDA kernels for GPU-accelerated mining.

To obtain the GPU module:
1. Download from releases: https://github.com/yourusername/gpu-miner/releases
2. Or build from source if you have a commercial license

Without this module, the miner runs in CPU-only mode.
"""

try:
    from .engine import GPUEngine
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    GPUEngine = None
```

**gpu_core/README.md** (public):
```markdown
# GPU Acceleration Module

This directory contains the proprietary GPU acceleration code.

## Options to Get GPU Acceleration:

### Option 1: Download Pre-built Module
Download from [Releases](https://github.com/yourusername/gpu-miner/releases)

### Option 2: Commercial License
Contact for commercial licensing of source code.

### Option 3: CPU-Only Mode
The miner works without GPU acceleration, just slower.
```

### Step 3: Modify Core to Handle Missing GPU Module

Update `core/miner_manager.py`:
```python
try:
    from gpu_core.engine import GPUEngine
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logging.warning("GPU module not found. Running in CPU-only mode.")
```

### Step 4: Create Two Git Repos

**Option A: Two Separate Repos**
```bash
# Create public repo (without gpu_core)
git init gpu-miner-public
cp -r GPUMiner/* gpu-miner-public/
cd gpu-miner-public
rm -rf gpu_core/*.py gpu_core/*.cu
git add .
git commit -m "Initial public release"

# Create private repo (full source)
git init gpu-miner-private
cp -r GPUMiner/* gpu-miner-private/
cd gpu-miner-private
git add .
git commit -m "Private source with GPU core"
```

**Option B: Submodule**
```bash
# 1. Create private repo for gpu_core only
cd GPUMiner/gpu_core
git init
git add .
git commit -m "GPU core implementation"
git remote add origin git@github.com:yourusername/gpu-miner-core-private.git
git push -u origin master

# 2. In public repo, reference as submodule
cd GPUMiner
git submodule add --name gpu_core git@github.com:yourusername/gpu-miner-core-private.git gpu_core

# Users without access will see empty gpu_core/
```

### Step 5: Distribution Options

**A. Pre-compiled Binary (Recommended)**
- Compile `gpu_core/` to `.pyd` (Windows) or `.so` (Linux)
- Distribute via GitHub Releases
- Use PyInstaller or Nuitka to compile Python to binary

```bash
# Example with Nuitka
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
```

**B. Obfuscated Python**
- Use PyArmor or similar to obfuscate GPU code
- Distribute obfuscated `.py` files

```bash
pip install pyarmor
pyarmor obfuscate gpu_core/engine.py
pyarmor obfuscate gpu_core/kernels.py
```

**C. Commercial License**
- Keep source completely private
- Provide access on request with license agreement

### Step 6: Publish to GitHub

```bash
cd GPUMiner
git remote add origin https://github.com/yourusername/gpu-miner.git
git branch -M main
git push -u origin main

# Create release with pre-built binaries
gh release create v1.0.0 \
  --title "GPU Miner v1.0.0" \
  --notes "See README for installation" \
  gpu_core_windows.zip \
  gpu_core_linux.tar.gz
```

## Recommended Approach

1. **Keep current private repo with full source**
2. **Create public repo excluding `gpu_core/` (except stubs)**
3. **Distribute GPU module as pre-compiled binaries via Releases**
4. **Use README_PUBLIC.md as main README**

This gives you:
- ✅ Open source community contributions to core
- ✅ Protected proprietary GPU code
- ✅ Easy distribution via releases
- ✅ Optional commercial licensing path
