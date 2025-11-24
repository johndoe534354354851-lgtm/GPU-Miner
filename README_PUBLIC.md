# GPU Miner

A high-performance GPU-accelerated miner for Midnight (NIGHT) and Defensio (DFO) tokens.

## Features

- 🚀 **GPU Acceleration** - CUDA-powered mining for maximum performance
- 💾 **SQLite State Management** - Robust wallet and solution tracking
- 📊 **Real-time Dashboard** - Monitor hashrate, solutions, and wallet status
- 🔄 **Auto-Wallet Management** - Automatic wallet creation and rotation
- 💰 **Consolidation Support** - Automatic token consolidation to your address
- 🎯 **Smart Challenge Selection** - Mines the easiest unsolved challenges first
- 📈 **Historical Challenge Support** - Works on challenges up to 24h old

## Installation

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (NVIDIA)
- CUDA Toolkit 11.8+

### Quick Start

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

## Configuration

Edit `config.yaml`:

```yaml
miner:
  api_url: https://mine.defensio.io/api
  max_workers: 1

wallet:
  consolidate_address: your_address_here

gpu:
  enabled: true
  batch_size: 1000000
```

## Usage

```powershell
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux

# Run the miner
python main.py
```

## GPU Acceleration Module

The GPU acceleration module (`gpu_core/`) is **proprietary** and distributed separately:

- **Open Source Users**: The miner will work in CPU-only mode
- **GPU Module Access**: Contact for commercial licensing or download pre-built binaries from [Releases](../../releases)

### Installing GPU Module (if you have access)

Place the `gpu_core/` directory in the project root:
```
GPUMiner/
├── core/
├── gpu_core/          # <- GPU acceleration module
│   ├── __init__.py
│   └── [proprietary files]
├── main.py
└── ...
```

## Features Breakdown

### Dashboard
Real-time TUI showing:
- Current hashrate (KH/s or MH/s)
- Solutions found (session and all-time)
- Active wallets and consolidation status
- Current challenge and difficulty

### Wallet Management
- Automatic wallet generation and registration
- Smart rotation to maximize mining efficiency
- Auto-consolidation to your specified address

### Challenge Tracking
- Registers all challenges seen
- Tracks which wallets solved which challenges
- Selects easiest unsolved challenges
- Supports mining older challenges (24h validity window)

## Architecture

```
GPUMiner/
├── core/              # Core infrastructure (open source)
│   ├── config.py      # Configuration management
│   ├── database.py    # SQLite state management
│   ├── networking.py  # API client
│   ├── wallet_manager.py  # Wallet operations
│   ├── miner_manager.py   # Mining orchestration
│   └── dashboard.py   # TUI dashboard
├── gpu_core/          # GPU acceleration (proprietary)
│   ├── engine.py      # GPU process manager
│   └── kernels.py     # CUDA kernels
├── libs/              # Cryptographic libraries
├── scripts/           # Installation scripts
└── main.py            # Entry point
```

## Troubleshooting

### Common Issues

**"No CUDA device found"**
- Ensure you have a CUDA-capable GPU
- Install CUDA Toolkit 11.8+
- Verify with `nvidia-smi`

**"Module 'gpu_core' not found"**
- GPU module not installed
- Miner will run in CPU-only mode (slower)

**Ctrl+C doesn't stop miner**
- Known issue on some systems
- Force quit with Task Manager / `kill` command
- Fixed in latest version

## Performance

Typical performance on RTX 4090:
- ~500 MH/s on easiest challenges
- ~100+ MH/s on moderate difficulty
- Scales with difficulty

## License

- **Core Infrastructure**: MIT License (open source)
- **GPU Module**: Proprietary (commercial license required)

## Contributing

Contributions to the core infrastructure are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [Report a bug](../../issues)
- Discussions: [Ask questions](../../discussions)

## Disclaimer

This software is provided as-is. Use at your own risk. Ensure compliance with mining pool terms of service and local regulations.
