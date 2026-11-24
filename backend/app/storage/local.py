import sqlite3
import asyncio
import json
from typing import Optional, List, Any
from app.storage.base import StorageBackend
from app.models.user import User
from app.models.provider import Provider
from app.models.job import Job, WorkloadType, JobStatus
from app.models.credit import CreditTransaction, TransactionType

class LocalStorage(StorageBackend):
    def __init__(self, db_path: str = "./ramshare.db"):
        self.db_path = db_path
        self._sync_conn: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()

    def _get_connection(self) -> sqlite3.Connection:
        if self._sync_conn is None:
            self._sync_conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._sync_conn.row_factory = sqlite3.Row
        return self._sync_conn

    def _run_query(self, query: str, params: tuple = ()) -> List[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                self._create_tables_sync(conn)
                cursor = conn.cursor()
                cursor.execute(query, params)
            else:
                raise
        if query.strip().upper().startswith(("SELECT", "PRAGMA")):
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        else:
            conn.commit()
            return [{"rowcount": cursor.rowcount}]

    def _create_tables_sync(self, conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            roles TEXT NOT NULL DEFAULT '["consumer"]',
            credit_balance REAL NOT NULL DEFAULT 500.0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS providers (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            machine_name TEXT NOT NULL,
            os_type TEXT,
            os_version TEXT,
            architecture TEXT,
            total_cpu_cores INTEGER,
            total_ram_mb REAL,
            total_disk_gb REAL,
            available_cpu_percent REAL,
            available_ram_mb REAL,
            available_disk_gb REAL,
            max_cpu_percent REAL,
            max_ram_mb REAL,
            max_concurrent_jobs INTEGER,
            current_job_count INTEGER DEFAULT 0,
            is_online INTEGER DEFAULT 1,
            is_sharing INTEGER DEFAULT 1,
            last_heartbeat TEXT NOT NULL,
            registered_at TEXT NOT NULL,
            reliability_score REAL DEFAULT 1.0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            consumer_id TEXT NOT NULL,
            provider_id TEXT,
            job_name TEXT NOT NULL,
            workload_type TEXT NOT NULL,
            status TEXT NOT NULL,
            required_ram_mb REAL NOT NULL,
            required_cpu_cores INTEGER NOT NULL,
            max_execution_time INTEGER NOT NULL,
            input_params TEXT,
            input_file_key TEXT,
            result_file_key TEXT,
            error_log TEXT,
            execution_time_seconds REAL,
            actual_cpu_percent REAL,
            actual_ram_mb REAL,
            estimated_credits REAL,
            final_credits REAL,
            created_at TEXT NOT NULL,
            assigned_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 2,
            FOREIGN KEY (consumer_id) REFERENCES users(id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            job_id TEXT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            idempotency_key TEXT UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        conn.commit()

    async def _execute(self, query: str, params: tuple = ()) -> List[dict]:
        async with self._lock:
            return await asyncio.to_thread(self._run_query, query, params)

    async def initialize(self) -> None:
        await self._execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            roles TEXT NOT NULL DEFAULT '["consumer"]',
            credit_balance REAL NOT NULL DEFAULT 500.0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """)
        await self._execute("""
        CREATE TABLE IF NOT EXISTS providers (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            machine_name TEXT NOT NULL,
            os_type TEXT,
            os_version TEXT,
            architecture TEXT,
            total_cpu_cores INTEGER,
            total_ram_mb REAL,
            total_disk_gb REAL,
            available_cpu_percent REAL DEFAULT 0.0,
            available_ram_mb REAL DEFAULT 0.0,
            available_disk_gb REAL DEFAULT 0.0,
            max_cpu_percent REAL DEFAULT 50.0,
            max_ram_mb REAL DEFAULT 2048.0,
            max_concurrent_jobs INTEGER DEFAULT 2,
            current_job_count INTEGER DEFAULT 0,
            is_online INTEGER DEFAULT 0,
            is_sharing INTEGER DEFAULT 0,
            last_heartbeat TEXT,
            registered_at TEXT NOT NULL,
            reliability_score REAL DEFAULT 1.0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        await self._execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            consumer_id TEXT NOT NULL,
            provider_id TEXT,
            job_name TEXT NOT NULL,
            workload_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            required_ram_mb REAL NOT NULL,
            required_cpu_cores INTEGER NOT NULL DEFAULT 1,
            max_execution_time INTEGER NOT NULL DEFAULT 300,
            input_params TEXT DEFAULT '{}',
            input_file_key TEXT,
            result_file_key TEXT,
            result_summary TEXT,
            estimated_credits REAL NOT NULL DEFAULT 0.0,
            actual_credits REAL,
            idempotency_key TEXT UNIQUE,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 2,
            FOREIGN KEY (consumer_id) REFERENCES users(id)
        )
        """)
        await self._execute("""
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            job_id TEXT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            idempotency_key TEXT UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

    # User operations
    async def create_user(self, user: User) -> User:
        await self._execute(
            """INSERT INTO users (id, username, email, hashed_password, roles, credit_balance, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user.id, user.username, user.email, user.hashed_password, json.dumps(user.roles),
             user.credit_balance, 1 if user.is_active else 0, user.created_at)
        )
        return user

    def _row_to_user(self, row: dict) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            roles=json.loads(row["roles"]),
            credit_balance=row["credit_balance"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"]
        )

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        rows = await self._execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self._row_to_user(rows[0]) if rows else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        rows = await self._execute("SELECT * FROM users WHERE username = ?", (username,))
        return self._row_to_user(rows[0]) if rows else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        rows = await self._execute("SELECT * FROM users WHERE email = ?", (email,))
        return self._row_to_user(rows[0]) if rows else None

    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        set_clauses = []
        values = []
        for k, v in kwargs.items():
            if k == "roles":
                v = json.dumps(v)
            elif k == "is_active":
                v = 1 if v else 0
            set_clauses.append(f"{k} = ?")
            values.append(v)
        values.append(user_id)
        if set_clauses:
            await self._execute(f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?", tuple(values))
        return await self.get_user_by_id(user_id)

    async def list_users(self) -> List[User]:
        rows = await self._execute("SELECT * FROM users")
        return [self._row_to_user(r) for r in rows]

    # Provider operations
    def _row_to_provider(self, row: dict) -> Provider:
        return Provider(
            id=row["id"],
            user_id=row["user_id"],
            machine_name=row["machine_name"],
            os_type=row["os_type"],
            os_version=row["os_version"],
            architecture=row["architecture"],
            total_cpu_cores=row["total_cpu_cores"],
            total_ram_mb=row["total_ram_mb"],
            total_disk_gb=row["total_disk_gb"],
            available_cpu_percent=row["available_cpu_percent"],
            available_ram_mb=row["available_ram_mb"],
            available_disk_gb=row["available_disk_gb"],
            max_cpu_percent=row["max_cpu_percent"],
            max_ram_mb=row["max_ram_mb"],
            max_concurrent_jobs=row["max_concurrent_jobs"],
            current_job_count=row["current_job_count"],
            is_online=bool(row["is_online"]),
            is_sharing=bool(row["is_sharing"]),
            last_heartbeat=row["last_heartbeat"],
            registered_at=row["registered_at"],
            reliability_score=row["reliability_score"]
        )

    async def create_provider(self, provider: Provider) -> Provider:
        await self._execute(
            """INSERT INTO providers (
                id, user_id, machine_name, os_type, os_version, architecture,
                total_cpu_cores, total_ram_mb, total_disk_gb,
                available_cpu_percent, available_ram_mb, available_disk_gb,
                max_cpu_percent, max_ram_mb, max_concurrent_jobs, current_job_count,
                is_online, is_sharing, last_heartbeat, registered_at, reliability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                provider.id, provider.user_id, provider.machine_name, provider.os_type,
                provider.os_version, provider.architecture, provider.total_cpu_cores,
                provider.total_ram_mb, provider.total_disk_gb, provider.available_cpu_percent,
                provider.available_ram_mb, provider.available_disk_gb, provider.max_cpu_percent,
                provider.max_ram_mb, provider.max_concurrent_jobs, provider.current_job_count,
                1 if provider.is_online else 0, 1 if provider.is_sharing else 0,
                provider.last_heartbeat, provider.registered_at, provider.reliability_score
            )
        )
        return provider

    async def get_provider_by_id(self, provider_id: str) -> Optional[Provider]:
        rows = await self._execute("SELECT * FROM providers WHERE id = ?", (provider_id,))
        return self._row_to_provider(rows[0]) if rows else None

    async def get_providers_by_user(self, user_id: str) -> List[Provider]:
        rows = await self._execute("SELECT * FROM providers WHERE user_id = ?", (user_id,))
        return [self._row_to_provider(r) for r in rows]

    async def update_provider(self, provider_id: str, **kwargs) -> Optional[Provider]:
        set_clauses = []
        values = []
        for k, v in kwargs.items():
            if k in ("is_online", "is_sharing"):
                v = 1 if v else 0
            set_clauses.append(f"{k} = ?")
            values.append(v)
        values.append(provider_id)
        if set_clauses:
            await self._execute(f"UPDATE providers SET {', '.join(set_clauses)} WHERE id = ?", tuple(values))
        return await self.get_provider_by_id(provider_id)

    async def list_providers(self, online_only: bool = False) -> List[Provider]:
        if online_only:
            rows = await self._execute("SELECT * FROM providers WHERE is_online = 1 AND is_sharing = 1")
        else:
            rows = await self._execute("SELECT * FROM providers")
        return [self._row_to_provider(r) for r in rows]

    async def delete_provider(self, provider_id: str) -> bool:
        res = await self._execute("DELETE FROM providers WHERE id = ?", (provider_id,))
        return res[0]["rowcount"] > 0

    # Job operations
    def _row_to_job(self, row: dict) -> Job:
        return Job(
            id=row["id"],
            consumer_id=row["consumer_id"],
            provider_id=row["provider_id"],
            job_name=row["job_name"],
            workload_type=WorkloadType(row["workload_type"]),
            status=JobStatus(row["status"]),
            required_ram_mb=row["required_ram_mb"],
            required_cpu_cores=row["required_cpu_cores"],
            max_execution_time=row["max_execution_time"],
            input_params=json.loads(row["input_params"]) if row["input_params"] else {},
            input_file_key=row["input_file_key"],
            result_file_key=row["result_file_key"],
            result_summary=row["result_summary"],
            estimated_credits=row["estimated_credits"],
            actual_credits=row["actual_credits"],
            idempotency_key=row["idempotency_key"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error_message=row["error_message"],
            retry_count=row["retry_count"],
            max_retries=row["max_retries"]
        )

    async def create_job(self, job: Job) -> Job:
        await self._execute(
            """INSERT INTO jobs (
                id, consumer_id, provider_id, job_name, workload_type, status,
                required_ram_mb, required_cpu_cores, max_execution_time, input_params,
                input_file_key, result_file_key, result_summary, estimated_credits,
                actual_credits, idempotency_key, created_at, started_at, completed_at,
                error_message, retry_count, max_retries
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job.id, job.consumer_id, job.provider_id, job.job_name, job.workload_type.value,
                job.status.value, job.required_ram_mb, job.required_cpu_cores, job.max_execution_time,
                json.dumps(job.input_params), job.input_file_key, job.result_file_key,
                job.result_summary, job.estimated_credits, job.actual_credits, job.idempotency_key,
                job.created_at, job.started_at, job.completed_at, job.error_message,
                job.retry_count, job.max_retries
            )
        )
        return job

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        rows = await self._execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        return self._row_to_job(rows[0]) if rows else None

    async def get_jobs_by_consumer(self, consumer_id: str, limit: int = 50, offset: int = 0) -> List[Job]:
        rows = await self._execute(
            "SELECT * FROM jobs WHERE consumer_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (consumer_id, limit, offset)
        )
        return [self._row_to_job(r) for r in rows]

    async def get_jobs_by_provider(self, provider_id: str, limit: int = 50, offset: int = 0) -> List[Job]:
        rows = await self._execute(
            "SELECT * FROM jobs WHERE provider_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (provider_id, limit, offset)
        )
        return [self._row_to_job(r) for r in rows]

    async def update_job(self, job_id: str, **kwargs) -> Optional[Job]:
        set_clauses = []
        values = []
        for k, v in kwargs.items():
            if k == "input_params":
                v = json.dumps(v)
            elif hasattr(v, "value"):
                v = v.value
            set_clauses.append(f"{k} = ?")
            values.append(v)
        values.append(job_id)
        if set_clauses:
            await self._execute(f"UPDATE jobs SET {', '.join(set_clauses)} WHERE id = ?", tuple(values))
        return await self.get_job_by_id(job_id)

    async def list_jobs(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Job]:
        if status:
            rows = await self._execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (status, limit, offset)
            )
        else:
            rows = await self._execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
        return [self._row_to_job(r) for r in rows]

    async def get_job_by_idempotency_key(self, key: str) -> Optional[Job]:
        rows = await self._execute("SELECT * FROM jobs WHERE idempotency_key = ?", (key,))
        return self._row_to_job(rows[0]) if rows else None

    # Credit operations
    def _row_to_txn(self, row: dict) -> CreditTransaction:
        return CreditTransaction(
            id=row["id"],
            user_id=row["user_id"],
            job_id=row["job_id"],
            transaction_type=TransactionType(row["transaction_type"]),
            amount=row["amount"],
            balance_after=row["balance_after"],
            description=row["description"] or "",
            created_at=row["created_at"],
            idempotency_key=row["idempotency_key"]
        )

    async def create_transaction(self, txn: CreditTransaction) -> CreditTransaction:
        await self._execute(
            """INSERT INTO credit_transactions (
                id, user_id, job_id, transaction_type, amount, balance_after,
                description, created_at, idempotency_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                txn.id, txn.user_id, txn.job_id, txn.transaction_type.value,
                txn.amount, txn.balance_after, txn.description, txn.created_at,
                txn.idempotency_key
            )
        )
        return txn

    async def get_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[CreditTransaction]:
        rows = await self._execute(
            "SELECT * FROM credit_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        )
        return [self._row_to_txn(r) for r in rows]

    async def get_transaction_by_idempotency_key(self, key: str) -> Optional[CreditTransaction]:
        rows = await self._execute("SELECT * FROM credit_transactions WHERE idempotency_key = ?", (key,))
        return self._row_to_txn(rows[0]) if rows else None

    async def update_user_balance(self, user_id: str, new_balance: float) -> bool:
        res = await self._execute("UPDATE users SET credit_balance = ? WHERE id = ?", (new_balance, user_id))
        return res[0]["rowcount"] > 0
