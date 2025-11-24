# Quick Guide: Building and Deploying GPU Binaries

## Workflow Overview

Since the proprietary source files (`engine.py` and `kernels.py`) are excluded from the GitHub repository, **all builds must be done locally** before pushing to GitHub.

## Build Process

### 1. Build Windows Binaries (Your Current Platform)

```powershell
cd "c:\Users\Elias\Documents\Cursor Porjects\GPU Miner\GPUMiner"
.\scripts\build_modules.bat
```

This creates:
- `gpu_core/bin/windows/engine.pyd`
- `gpu_core/bin/windows/kernels.pyd`

### 2. Commit Binaries

```bash
git add gpu_core/bin/windows/
git commit -m "Update Windows GPU binaries"
git push
```

### 3. Build Linux/macOS Binaries (Optional)

If you have access to Linux or macOS machines:

```bash
chmod +x scripts/build_modules.sh
./scripts/build_modules.sh
git add gpu_core/bin/linux/   # or macos/
git commit -m "Update Linux GPU binaries"
git push
```

**Alternative:** Users can build their own binaries for their platform using the scripts.

## GitHub Actions

The workflow `.github/workflows/build-gpu-modules.yml` now:
- **Does NOT build** (source files aren't in repo)
- **Only verifies** existing binaries
- **Uploads** them as artifacts for releases
- **Manual trigger only**

## Current Status

✅ Windows binaries can be built locally  
⚠️ Linux/macOS binaries need to be built on those platforms (or GitHub Actions won't work for those)  
✅ Workflow won't fail anymore - it just archives what's already there

## Recommendation

For your initial release, you can:
1. Build and commit Windows binaries (you have Windows)
2. Add a note in README that Linux/macOS users should build binaries themselves
3. Later, if you get access to those platforms, add those binaries too
