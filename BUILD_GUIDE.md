# Cross-Platform Build Guide

## Option 1: GitHub Actions (Recommended - Automatic)

The `.github/workflows/build-gpu-modules.yml` workflow automatically builds binaries for all platforms when you push changes to `engine.py` or `kernels.py`.

**Setup:**
1. Push to GitHub
2. GitHub Actions will automatically build Windows, Linux, and macOS binaries
3. Binaries are committed back to the repo

That's it! Users can clone and run immediately.

## Option 2: Manual Building

### Prerequisites
- Access to Windows, Linux, and macOS machines (or VMs)
- Python 3.12 installed on each
- Nuitka installed: `pip install nuitka`

### Windows (Your Current System)
```powershell
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
move *.pyd gpu_core/bin/windows/
```

### Linux (WSL, VM, or Server)
```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install python3-dev gcc

# Build
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
mv *.so gpu_core/bin/linux/
```

### macOS (Mac or VM)
```bash
# Install Xcode Command Line Tools if needed
xcode-select --install

# Build
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
mv *.so gpu_core/bin/macos/
```

## Option 3: Docker for Linux Builds

If you don't have Linux, use Docker to build Linux binaries from Windows:

```powershell
# Create Dockerfile
@"
FROM python:3.12-slim
RUN apt-get update && apt-get install -y gcc python3-dev
RUN pip install nuitka
WORKDIR /build
COPY gpu_core/engine.py gpu_core/kernels.py ./
RUN python -m nuitka --module engine.py
RUN python -m nuitka --module kernels.py
"@ | Out-File -Encoding UTF8 Dockerfile

# Build and extract binaries
docker build -t gpu-builder .
docker create --name temp gpu-builder
docker cp temp:/build/engine.cpython-312-x86_64-linux-gnu.so gpu_core/bin/linux/
docker cp temp:/build/kernels.cpython-312-x86_64-linux-gnu.so gpu_core/bin/linux/
docker rm temp
```

## Current Status

✅ **Windows** - Built and ready (`gpu_core/bin/windows/`)
⏳ **Linux** - Needs building
⏳ **macOS** - Needs building

## Publishing Workflow

1. **Make changes** to `engine.py` or `kernels.py`
2. **Build for all platforms** (GitHub Actions does this automatically)
3. **Commit everything** including binaries:
   ```bash
   git add gpu_core/bin/
   git commit -m "Update GPU modules"
   git push
   ```
4. **Users clone** and it just works - no compilation needed!

## Advantages of This Approach

- ✅ **No separate downloads** - Everything in one repo
- ✅ **Cross-platform** - Works on Windows, Linux, macOS
- ✅ **Zero build time** for users - Pre-compiled
- ✅ **Source code hidden** - Only binaries included
- ✅ **Easy updates** - Git pull gets new binaries
- ✅ **Automatic** - GitHub Actions handles building
