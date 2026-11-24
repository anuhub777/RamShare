# RAMShare Security & Isolation Model

Executing user-supplied computation on remote computers requires defense-in-depth security. RAMShare enforces rigorous multi-layered boundaries.

---

## 1. Workload Isolation Policy
The Docker runtime restricts container execution using the following constraints:

```python
container = client.containers.run(
    image=approved_image,
    privileged=False,                        # 1. No privileged access
    network_disabled=True,                   # 2. Zero network egress/ingress
    user="nobody",                           # 3. Non-root user execution
    cap_drop=["ALL"],                        # 4. Drop all Linux capabilities
    security_opt=["no-new-privileges:true"], # 5. Prevent privilege escalation
    mem_limit=f"{required_ram}m",            # 6. Hard memory limit
    cpu_period=100000,                       # 7. CPU quota enforcement
    cpu_quota=int(cores * 100000),
    volumes={
        input_dir: {"bind": "/input", "mode": "ro"}, # 8. Read-only input mounts
        output_dir: {"bind": "/output", "mode": "rw"}
    },
    tmpfs={"/tmp": "size=64M,noexec"}        # 9. Noexec temporary storage
)
```

### Key Protections
1. **No Arbitrary Shell Code**: Consumers cannot submit arbitrary shell commands. Workloads are strictly confined to predefined, cryptographically vetted templates (`CPU_BENCHMARK`, `MEMORY_BENCHMARK`, `DATA_PROCESSING`, `ML_INFERENCE`).
2. **Network Isolation**: Workload containers have `network_disabled=True`. They cannot communicate with the local host network, local devices, or the public internet.
3. **No Host Filesystem Exposure**: Workloads mount only an ephemeral, freshly created scratch directory. The host root, home directory, and Docker daemon socket are never mounted.
4. **Non-Root Execution**: Containers run under the unprivileged `nobody` UID (65534).
5. **Dropped Linux Capabilities**: All kernel capabilities (`NET_ADMIN`, `SYS_ADMIN`, `SYS_PTRACE`) are dropped.

---

## 2. Realistic Isolation Disclaimers
While Docker provides robust Linux namespace and cgroup boundaries, Docker alone is not a hardware virtualization boundary. Kernel-level vulnerabilities in the host OS kernel could theoretically allow container escapes. In production enterprise deployments, providers should run workloads within microVM technologies such as **AWS Firecracker**, **gVisor**, or isolated virtualization sandboxes.

---

## 3. Financial & Credit Safety
- **Atomic Double-Entry Transactions**: Credit deductions and provider reward allocations occur in atomic database operations.
- **Idempotency Keys**: Every job submission and balance transfer includes an idempotency hash (`idempotency_key = sha256(user + job + type)`) to prevent duplicate executions or double-billing caused by message retries.
- **Zero Real-Money Risk**: The MVP uses an internal credit economy without real-money banking transactions.
