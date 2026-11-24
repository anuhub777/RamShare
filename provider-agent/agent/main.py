import click
import sys
import logging
import httpx
from rich.panel import Panel
from agent.config import config
from agent.monitor import ResourceMonitor
from agent.docker_executor import DockerExecutor
from agent.heartbeat import HeartbeatSender
from agent.job_runner import JobRunner
from agent.ui import AgentUI, console

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ramshare.agent")

@click.group()
def cli():
    """RAMShare Provider Desktop Agent CLI"""
    pass

@cli.command()
@click.option("--api-url", default="http://localhost:8000", help="RAMShare Backend URL")
@click.option("--max-cpu", default=50.0, help="Max CPU % to share")
@click.option("--max-ram", default=2048.0, help="Max RAM (MB) to allocate")
@click.option("--max-jobs", default=2, help="Max concurrent jobs")
def start(api_url, max_cpu, max_ram, max_jobs):
    """Start the provider agent, register computer and share resources."""
    ui = AgentUI()
    ui.show_banner()

    monitor = ResourceMonitor()
    executor = DockerExecutor()

    # Preflight Docker Check
    docker_ok = executor.is_docker_available()
    if not docker_ok:
        console.print("[yellow]Warning: Docker engine is not currently running.[/yellow]")
        console.print("[dim]Workload execution requires Docker. Agent will still register and monitor resources.[/dim]\n")

    # 1. Login or register user
    username, password = ui.prompt_login()
    token = None
    user_data = None

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(f"{api_url}/auth/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                data = resp.json()
                token = data["access_token"]
                user_data = data["user"]
                console.print(f"[green]Authenticated as {user_data['username']}[/green]")
            else:
                console.print(f"[red]Login failed: {resp.text}[/red]")
                sys.exit(1)
    except Exception as e:
        console.print(f"[red]Could not connect to RAMShare backend at {api_url}: {e}[/red]")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}
    provider_id = None

    # 2. Check if user already has registered provider machine
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{api_url}/providers", headers=headers)
            if resp.status_code == 200:
                provs = resp.json().get("providers", [])
                my_provs = [p for p in provs if p["user_id"] == user_data["id"]]
                if my_provs:
                    provider_id = my_provs[0]["id"]
                    console.print(f"[green]Using existing registered machine: {my_provs[0]['machine_name']} ({provider_id})[/green]")
    except Exception as e:
        logger.warning(f"Could not fetch existing providers: {e}")

    # 3. Register machine if not found
    if not provider_id:
        system_info = monitor.get_system_info()
        reg_payload = ui.prompt_registration(system_info)
        reg_payload["max_cpu_percent"] = max_cpu
        reg_payload["max_ram_mb"] = max_ram
        reg_payload["max_concurrent_jobs"] = max_jobs

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{api_url}/providers/register", json=reg_payload, headers=headers)
                if resp.status_code == 201:
                    provider_id = resp.json()["id"]
                    console.print(f"[bold green]Registered new provider computer: {provider_id}[/bold green]")
                else:
                    console.print(f"[red]Registration error: {resp.text}[/red]")
                    sys.exit(1)
        except Exception as e:
            console.print(f"[red]Failed to register provider: {e}[/red]")
            sys.exit(1)

    # 4. Start Heartbeat Sender & Job Runner
    job_runner = JobRunner(
        api_url=api_url,
        token=token,
        provider_id=provider_id,
        executor=executor,
        max_concurrent=max_jobs,
        poll_interval=5
    )

    heartbeat = HeartbeatSender(
        api_url=api_url,
        token=token,
        provider_id=provider_id,
        monitor=monitor,
        interval=15,
        job_counter_callback=job_runner.get_active_count
    )

    heartbeat.start()
    job_runner.start()

    banner_msg = (
        f"[bold green]Agent Status: ONLINE[/bold green]\n"
        f"Provider ID: {provider_id}\n"
        f"Backend: {api_url}\n"
        f"Sharing limits: {max_cpu}% CPU, {max_ram}MB RAM, Max {max_jobs} jobs\n"
        f"Press Ctrl+C or type 'exit' to stop."
    )
    console.print(Panel.fit(banner_msg, title="RAMShare Provider Node Running"))

    # 5. Interactive command loop
    try:
        while True:
            cmd = input("\n[RAMShare]> ").strip().lower()
            if cmd == "status":
                ui.show_status(monitor, job_runner)
            elif cmd == "jobs":
                if job_runner.active_jobs:
                    console.print(f"[cyan]Active jobs ({len(job_runner.active_jobs)}):[/cyan]")
                    for jid, job in job_runner.active_jobs.items():
                        console.print(f" - {jid}: {job.get('job_name')} [{job.get('workload_type')}]")
                else:
                    console.print("[dim]No active jobs executing currently.[/dim]")
            elif cmd == "stop":
                with httpx.Client(timeout=5.0) as client:
                    client.patch(f"{api_url}/providers/{provider_id}/availability", json={"is_sharing": False}, headers=headers)
                console.print("[yellow]Resource sharing paused.[/yellow]")
            elif cmd == "start":
                with httpx.Client(timeout=5.0) as client:
                    client.patch(f"{api_url}/providers/{provider_id}/availability", json={"is_sharing": True}, headers=headers)
                console.print("[green]Resource sharing resumed.[/green]")
            elif cmd in ("exit", "quit", "q"):
                break
            elif cmd == "help":
                ui.show_commands()
            else:
                console.print("[dim]Unknown command. Type 'status', 'jobs', 'stop', 'start', or 'exit'.[/dim]")

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        console.print("\n[yellow]Stopping agent threads...[/yellow]")
        heartbeat.stop()
        job_runner.stop()
        try:
            with httpx.Client(timeout=3.0) as client:
                client.patch(f"{api_url}/providers/{provider_id}/availability", json={"is_sharing": False}, headers=headers)
        except Exception:
            pass
        console.print("[green]RAMShare Agent stopped safely.[/green]")

@cli.command()
def info():
    """Display local machine hardware specifications and Docker status."""
    monitor = ResourceMonitor()
    executor = DockerExecutor()

    info_data = monitor.get_system_info()
    res_data = monitor.get_available_resources()
    docker_ok = executor.is_docker_available()

    info_msg = (
        f"OS: {info_data['os_type']} {info_data['os_version']} ({info_data['architecture']})\n"
        f"CPU Cores: {info_data['total_cpu_cores']}\n"
        f"Total RAM: {info_data['total_ram_mb']} MB\n"
        f"Total Disk: {info_data['total_disk_gb']} GB\n"
        f"Available CPU: {res_data['available_cpu_percent']}%\n"
        f"Available RAM: {res_data['available_ram_mb']} MB\n"
        f"Free Disk: {res_data['available_disk_gb']} GB\n"
        f"Docker Available: {'[green]YES[/green]' if docker_ok else '[red]NO[/red]'}"
    )
    console.print(Panel.fit(info_msg, title="System Diagnostics"))

if __name__ == "__main__":
    cli()
