# RAMShare Architecture Specification

## 1. Executive Summary
RAMShare is a decentralized peer-to-peer cloud computing marketplace that unlocks unused compute capacity (CPU & RAM) from personal computers. While AWS functions as the centralized coordination and control plane (API Gateway, Lambda, DynamoDB, SQS, S3, Cognito), all user workloads execute directly on provider machines inside isolated Docker containers.

```
+-----------------------------------------------------------------------------------+
|                              AWS CONTROL PLANE                                    |
|                                                                                   |
|  [Consumers] ---> [API Gateway] ---> [Lambda API Engine] <---> [Cognito Auth]    |
|                          |                   |                                    |
|                          v                   v                                    |
|                   [Amazon S3]     [Amazon DynamoDB]                              |
|                   (Artifacts)     (Users, Providers, Jobs, Credits)               |
|                                              |                                    |
|                                              v                                    |
|                                      [Amazon SQS Queue]                           |
|                                              |                                    |
|                                              v                                    |
|                                   [Matchmaking Engine]                            |
+----------------------------------------------|------------------------------------+
                                               | (Pull Model / Long Polling)
                                               v
+-----------------------------------------------------------------------------------+
|                             PROVIDER EXECUTION PLANE                              |
|                                                                                   |
|      [RAMShare Provider Desktop Agent (Python / psutil)]                          |
|         - Real-time Hardware Monitoring                                           |
|         - Safety Limits & Dynamic Auto-Pause                                      |
|         - Heartbeat Loop (Dynamic Resources)                                      |
|         - Workload Poller & Job Dispatcher                                        |
|                          |                                                        |
|                          v                                                        |
|      [Isolated Docker Container Runtime]                                          |
|         - Drop ALL Linux Capabilities (`cap_drop=['ALL']`)                        |
|         - Non-root User (`user='nobody'`)                                         |
|         - Network Access Disabled (`network_disabled=True`)                       |
|         - CPU Quotas & Memory Limits (`mem_limit`, `cpu_period`, `cpu_quota`)     |
|         - Read-Only Input Volumes & Ephemeral Result Storage                      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Pillars

### A. Coordination vs. Execution Plane Separation
- **AWS Control Plane**: Hosts user accounts, provider telemetry, job dispatch queues, and the credit transaction ledger.
- **Provider Execution Plane**: Physical compute nodes distributed globally that execute computational jobs inside hardened, resource-constrained Docker containers.

### B. Pull-Based Job Dispatch (NAT & Firewall Traversal)
Provider computers operate behind residential NATs and firewalls. RAMShare uses a **pull-based dispatch architecture**:
1. Providers poll `GET /jobs/poll/{provider_id}` over outbound HTTPS.
2. No inbound firewall rules, port forwarding, or public IP addresses are required on provider machines.

### C. Resource Matchmaking Algorithm
The Matchmaking Engine selects providers using a multi-factor scoring function:
$$\text{Score} = 0.35 \times \text{RAM Score} + 0.35 \times \text{CPU Score} + 0.15 \times \text{Reliability} + 0.15 \times \text{Load Headroom}$$
- Hard constraints reject providers that are offline, have paused sharing, are at max concurrent job capacity, or have available RAM below workload requirements.
- Provider reservation uses atomic state transitions (`MATCHING` -> `ASSIGNED`) to prevent race conditions.

### D. Dual-Mode Deployment (Local vs. AWS Cloud)
RAMShare provides complete parity between development and production environments:
| Component | Local Dev Mode (`RAMSHARE_MODE=local`) | AWS Cloud Mode (`RAMSHARE_MODE=aws`) |
| :--- | :--- | :--- |
| **Database** | SQLite + thread-safe async adapter | Amazon DynamoDB (Pay-Per-Request + GSIs) |
| **Queuing** | In-memory asyncio queue with visibility timeout | Amazon SQS with Dead Letter Queue (DLQ) |
| **Storage** | Local disk (`./ramshare-storage/`) | Amazon S3 with signed URLs |
| **Auth** | Pure Python RFC 7519 JWT + PBKDF2/bcrypt | Amazon Cognito User Pools + JWT Authorizer |
| **Compute** | Docker Engine on local machine | Docker Engine on remote provider PCs |
