from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from typing import Dict, Any, Tuple

console = Console()

class AgentUI:
    def show_banner(self):
        banner = Text()
        banner.append("====================================================\n", style="bold blue")
        banner.append("              RAMShare Provider Agent               \n", style="bold cyan")
        banner.append("    Decentralized Peer-to-Peer Computing Network   \n", style="dim white")
        banner.append("====================================================\n", style="bold blue")
        console.print(banner)

    def prompt_login(self) -> Tuple[str, str]:
        console.print("[bold]Please authenticate with RAMShare[/bold]")
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        return username, password

    def prompt_registration(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        console.print("\n[bold cyan]Machine Configuration[/bold cyan]")
        machine_name = Prompt.ask("Device Name", default=f"{system_info['os_type']}-{system_info['architecture']}")
        max_cpu = float(Prompt.ask("Max CPU % to share", default="50.0"))
        max_ram = float(Prompt.ask("Max RAM (MB) to allocate", default=str(min(4096.0, system_info['total_ram_mb'] * 0.5))))
        max_jobs = int(Prompt.ask("Max Concurrent Jobs", default="2"))

        return {
            "machine_name": machine_name,
            "os_type": system_info["os_type"],
            "os_version": system_info["os_version"],
            "architecture": system_info["architecture"],
            "total_cpu_cores": system_info["total_cpu_cores"],
            "total_ram_mb": system_info["total_ram_mb"],
            "total_disk_gb": system_info["total_disk_gb"],
            "max_cpu_percent": max_cpu,
            "max_ram_mb": max_ram,
            "max_concurrent_jobs": max_jobs,
        }

    def show_status(self, monitor, job_runner=None, earned_credits: float = 0.0):
        resources = monitor.get_available_resources()
        active_count = job_runner.get_active_count() if job_runner else 0
        completed = job_runner.completed_count if job_runner else 0
        failed = job_runner.failed_count if job_runner else 0
        credits_val = job_runner.earned_credits if job_runner else earned_credits

        table = Table(title="Live Machine Status", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Status", "[bold green]ONLINE & SHARING[/bold green]")
        table.add_row("Available CPU", f"{resources['available_cpu_percent']}%")
        table.add_row("Available RAM", f"{resources['available_ram_mb']} MB")
        table.add_row("Free Disk", f"{resources['available_disk_gb']} GB")
        table.add_row("Active Workloads", str(active_count))
        table.add_row("Completed Jobs", str(completed))
        table.add_row("Failed Jobs", str(failed))
        table.add_row("Earned Credits", f"{credits_val:.2f} credits")

        console.print(table)

    def show_commands(self):
        table = Table(title="Interactive Commands", show_header=True)
        table.add_column("Command", style="bold yellow")
        table.add_column("Action", style="white")

        table.add_row("status", "Show current resources and metrics")
        table.add_row("jobs", "List active executing workloads")
        table.add_row("start", "Enable sharing mode")
        table.add_row("stop", "Pause sharing mode")
        table.add_row("exit", "Clean shutdown")

        console.print(table)
