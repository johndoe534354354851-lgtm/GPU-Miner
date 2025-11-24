# GPU Core Binaries

This directory contains pre-compiled GPU acceleration modules for different platforms.

## Structure

```
bin/
├── windows/
│   ├── engine.cp312-win_amd64.pyd
│   └── kernels.cp312-win_amd64.pyd
├── linux/
│   ├── engine.cpython-312-x86_64-linux-gnu.so
│   └── kernels.cpython-312-x86_64-linux-gnu.so
└── macos/
    ├── engine.cpython-312-darwin.so
    └── kernels.cpython-312-darwin.so
```

## Building for Your Platform

### Windows
```powershell
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
move *.pyd gpu_core/bin/windows/
```

### Linux
```bash
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
mv *.so gpu_core/bin/linux/
```

### macOS
```bash
python -m nuitka --module gpu_core/engine.py
python -m nuitka --module gpu_core/kernels.py
mv *.so gpu_core/bin/macos/
```

## Note

These are pre-compiled binaries of the proprietary GPU acceleration code.
The source files (`engine.py`, `kernels.py`) are not included in the public repository.
