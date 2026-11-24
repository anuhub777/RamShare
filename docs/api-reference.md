# RAMShare REST API Reference

Base URL: `http://localhost:8000` (Local) or `https://{api-id}.execute-api.{region}.amazonaws.com/dev` (AWS)

All protected endpoints require the header:
`Authorization: Bearer <jwt-token>`

---

## 1. Authentication & Users

### `POST /auth/register`
Create a new user account and receive 500 complimentary compute credits.
- **Request Body**:
  ```json
  {
    "username": "janedoe",
    "email": "jane@example.com",
    "password": "SecurePassword123",
    "roles": ["consumer", "provider"]
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "c1f7b8...",
      "username": "janedoe",
      "email": "jane@example.com",
      "roles": ["consumer", "provider"],
      "credit_balance": 500.0,
      "created_at": "2026-11-24T10:00:00Z"
    }
  }
  ```

### `POST /auth/login`
Authenticate existing user and obtain session JWT token.

### `GET /auth/me`
Retrieve currently authenticated user profile and credit balance.

---

## 2. Provider Endpoints

### `POST /providers/register`
Register a computer node into the provider network.
- **Request Body**:
  ```json
  {
    "machine_name": "Studio-Desktop",
    "os_type": "Linux",
    "os_version": "Ubuntu 22.04",
    "architecture": "x86_64",
    "total_cpu_cores": 16,
    "total_ram_mb": 32768,
    "total_disk_gb": 1000,
    "max_cpu_percent": 75.0,
    "max_ram_mb": 8192.0,
    "max_concurrent_jobs": 2
  }
  ```

### `POST /providers/heartbeat`
Send periodic telemetry update from desktop agent.
- **Request Body**:
  ```json
  {
    "provider_id": "p-12345",
    "available_cpu_percent": 82.5,
    "available_ram_mb": 6400.0,
    "available_disk_gb": 450.0,
    "current_job_count": 1
  }
  ```

### `PATCH /providers/{provider_id}/availability`
Toggle resource sharing status on or off (`{"is_sharing": true|false}`).

### `GET /providers/{provider_id}/jobs`
List workloads assigned to this specific provider.

---

## 3. Workloads & Jobs

### `POST /jobs`
Submit a new computational workload.
- **Request Body**:
  ```json
  {
    "job_name": "High-Dim Factorial Benchmark",
    "workload_type": "CPU_BENCHMARK",
    "required_ram_mb": 1024,
    "required_cpu_cores": 2,
    "max_execution_time": 180,
    "input_params": {
      "iterations": 50000
    }
  }
  ```

### `GET /jobs`
List submitted jobs for the authenticated consumer.

### `GET /jobs/{job_id}`
Retrieve live job status, assigned provider, execution logs, and output summary.

### `POST /jobs/{job_id}/cancel`
Cancel an unstarted workload and release held credits.

### `POST /jobs/{job_id}/status`
Report execution status from provider desktop agent (`RUNNING`, `COMPLETED`, `FAILED`).

---

## 4. Credits & Marketplace

### `GET /credits/balance`
Retrieve live balance.

### `GET /credits/transactions`
Retrieve audit ledger of earnings, expenditures, and refunds.

### `POST /credits/estimate`
Calculate cost estimate based on CPU, RAM, and runtime duration.

### `GET /marketplace/statistics`
Global network telemetry (online providers, active compute capacity, completed jobs).

### `GET /marketplace/resources`
Directory of all currently online provider nodes.
