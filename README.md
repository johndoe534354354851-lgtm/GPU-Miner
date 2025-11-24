# GPU Miner

A high-performance GPU-accelerated cryptocurrency miner for **Defensio (DFO)** tokens, built with CUDA and Python.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![CUDA](https://img.shields.io/badge/CUDA-11.8+-green.svg)](https://developer.nvidia.com/cuda-downloads)



## Quick Start

### Prerequisites

- **Python 3.12+**
- **CUDA-capable GPU** (NVIDIA)
- **CUDA Toolkit 11.8+** ([Download](https://developer.nvidia.com/cuda-downloads))

### Installation

**Windows:**
```powershell
git clone https://github.com/yourusername/gpu-miner.git
cd gpu-miner
.\scripts\install.bat
```

**Linux:**
```bash
git clone https://github.com/yourusername/gpu-miner.git
cd gpu-miner
chmod +x scripts/install.sh
./scripts/install.sh
```

### Configuration

Edit `config.yaml` to customize settings:

```yaml
miner:
  api_url: https://mine.defensio.io/api
  max_workers: 1

wallet:
  consolidate_address: your_cardano_address_here

gpu:
  enabled: true
  batch_size: 1000000
```

### Running

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Start mining
python main.py
```

## Developer Fee

This miner includes a **5% developer fee** to support ongoing development and maintenance. Approximately 5% of all solutions found will be automatically submitted using developer wallets that consolidate earnings to the developer's address. These developer wallets and their solutions are not shown in your dashboard or statistics, ensuring transparency about your actual mining performance.

**Key Points:**
- 5% of found solutions go to the developer
- Developer wallets are created and managed automatically
- Developer solutions are excluded from your dashboard statistics
- This fee helps maintain and improve the miner

By using this software, you agree to this fee structure.

## Architecture

```
GPUMiner/
├── core/                  # Core infrastructure
│   ├── config.py         # Configuration management
│   ├── database.py       # SQLite state management
│   ├── networking.py     # API client
│   ├── wallet_manager.py # Wallet operations
│   ├── miner_manager.py  # Mining orchestration
│   └── dashboard.py      # TUI dashboard
├── gpu_core/             # GPU acceleration (proprietary)
│   ├── __init__.py       # Platform auto-detection
│   └── bin/              # Pre-compiled binaries
│       ├── windows/      # Windows .pyd files
│       ├── linux/        # Linux .so files
│       └── macos/        # macOS .so files
├── libs/                 # Cryptographic libraries
└── scripts/              # Installation scripts
```

## Features

1. **Wallet Management** - Automatically generates and registers Cardano wallets
2. **Challenge Tracking** - Fetches and registers all available challenges from the API
3. **Smart Selection** - Selects the easiest unsolved challenge for each wallet
4. **GPU Mining** - Dispatches work to CUDA kernels for parallel processing
5. **Consolidation** - Optionally consolidates earnings to a single address

## 📊 Performance

Typical hashrates on different GPUs:

| GPU | Hashrate (avg) |
|-----|----------------|
| RTX 4090 | -- KH/s |
| RTX 4080 | -- KH/s |
| RTX 3090 | -- KH/s |
| RTX 3080 | -- KH/s |

*Performance varies based on challenge difficulty and system configuration.*


## Troubleshooting

### "No CUDA device found"
- Ensure you have a CUDA-capable NVIDIA GPU
- Install CUDA Toolkit 11.8+
- Verify installation with `nvidia-smi`

### "Module 'gpu_core' not found"
- GPU binaries should be included in the repo
- Check that `gpu_core/bin/<platform>/` contains the correct files
- Try reinstalling with the provided scripts


## License

This project uses a dual-license model:

- **Core Infrastructure** (everything except `gpu_core/`): [MIT License](LICENSE)
- **GPU Acceleration Module** (`gpu_core/`): Proprietary (source code available if competing projects emerge)

See the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk. Ensure compliance with:
- Local regulations and laws
- DYOR on any project you mine for




## Support

- **Issues**: [GitHub Issues](../../issues)
- **Discord**: [herolias](https://discord.com/users/herolias)
- **X**: [Herolias](https://x.com/Herolias)
- **Updates**: Watch this repository for updates


