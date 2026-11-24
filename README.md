# RAMShare — Decentralized Peer-to-Peer Cloud Computing Marketplace

```
  ____      _    __  __ ____  _                        
 |  _ \    / \  |  \/  / ___|| |__   __ _ _ __ ___    
 | |_) |  / _ \ | |\/| \___ \| '_ \ / _` | '__/ _ \   
 |  _ <  / ___ \| |  | |___) | | | | (_| | | |  __/   
 |_| \_\/_/   \_\_|  |_|____/|_| |_|\__,_|_|  \___|   
   Decentralized Cloud Computing Powered by Unused PC Capacity
```

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Execution-Docker%20Engine-2496ED.svg?style=flat&logo=docker)](https://www.docker.com)
[![AWS](https://img.shields.io/badge/Control%20Plane-AWS%20Serverless-FF9900.svg?style=flat&logo=amazon-aws)](https://aws.amazon.com)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg?style=flat)](https://pytest.org)

RAMShare connects people who have idle computer CPU and RAM capacity (**Providers**) with researchers, students, and developers needing cost-effective computational power (**Consumers**).

The actual computation executes directly on provider computers inside isolated Docker containers, while AWS (or a local developer adapter) acts as the coordination control plane.

---

## System Architecture

```
[Consumer Web App]
        |
        v
[FastAPI / AWS API Gateway] <---> [Cognito / Local JWT Auth]
        |
        +---> [DynamoDB / SQLite] (Users, Providers, Jobs, Credit Ledger)
        +---> [SQS / Async Queue] (Decoupled Job Dispatch Queue)
                    |
                    v
          [Matchmaking Engine] (Scores RAM, CPU, Load & Reliability)
                    |
                    v
    [Provider Desktop Agent] (Runs on Provider PC, Pull-based HTTPS)
                    |
                    v
         [Restricted Docker Sandbox] (Nobody user, zero net, resource quotas)
```

---

## Quick Start (Local Development)

### 1. Start the Backend API
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API documentation is available at `http://localhost:8000/docs`.

### 2. Start the React Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to access the full SaaS marketplace dashboard.

### 3. Start the Provider Desktop Agent
In a separate terminal:
```bash
cd provider-agent
python3 -m agent.main start
```

---

## Automated Test Suites

### Backend Unit & Integration Tests (13 Tests)
Verifies user auth, provider registration, heartbeat telemetry, job state machine, credit ledger, and the complete end-to-end peer-to-peer workload execution cycle:
```bash
python3 -m pytest backend/tests -v
```

### Provider Agent Tests (6 Tests)
Verifies resource monitoring, Docker security settings, and job runner polling:
```bash
python3 -m pytest provider-agent/tests -v
```

---

## Docker Compose Quick Launch
To start the entire backend and frontend in containerized mode:
```bash
docker compose up --build
```

---

## Documentation
- [Architecture Plan](docs/architecture.md)
- [REST API Reference](docs/api-reference.md)
- [Provider Desktop Agent Guide](docs/provider-agent-guide.md)
- [AWS SAM Deployment Guide](docs/deployment-guide.md)
- [Render Deployment Guide (Frontend + Backend)](docs/render-deployment.md)
- [Security & Sandbox Model](docs/security.md)

---

## License
MIT License. Built for decentralized, community-driven cloud computing.
# RamShare
