# RAMShare Provider Agent Guide

The RAMShare Provider Desktop Agent is a lightweight, secure background worker that monitors your computer's CPU and RAM availability, advertises capacity to the marketplace, and executes containerized workloads safely.

---

## 1. Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13.
- **Docker Engine**: Docker Desktop (macOS/Windows) or Docker Engine (Linux).
- **RAM**: Minimum 4GB total RAM (at least 1GB allocatable to RAMShare).

---

## 2. Installation

1. Navigate to the `provider-agent` directory:
   ```bash
   cd provider-agent
   pip install -r requirements.txt
   ```

2. Optional: Install the agent as an executable CLI tool:
   ```bash
   pip install -e .
   ```

---

## 3. Launching the Agent

### Quick Start
```bash
python3 -m agent.main start
```

### Advanced Parameters
```bash
python3 -m agent.main start \
  --api-url http://localhost:8000 \
  --max-cpu 60.0 \
  --max-ram 4096.0 \
  --max-jobs 2
```

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `--api-url` | `http://localhost:8000` | Address of RAMShare backend |
| `--max-cpu` | `50.0` | Maximum percentage of CPU RAMShare may consume |
| `--max-ram` | `2048.0` | Maximum megabytes of RAM allocatable to workloads |
| `--max-jobs` | `2` | Maximum concurrent container workloads |

---

## 4. Terminal Interactive Commands
Once started, the agent displays a live status dashboard and accepts commands:
- `status`: Show live CPU usage, available RAM, and earned credit statistics.
- `jobs`: List currently executing workloads.
- `stop`: Temporarily pause sharing (leaves agent online without accepting new jobs).
- `start`: Resume sharing capacity.
- `exit`: Gracefully shut down active workloads, deregister from queue, and exit.

---

## 5. System Diagnostics
Run diagnostics to verify local hardware detection and Docker integration:
```bash
python3 -m agent.main info
```
