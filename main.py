import os
import sys
import time
import json
import psutil
import requests
import shutil
import threading
from datetime import datetime

# Import rich components
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.text import Text
    from rich.prompt import Prompt
    from rich import print as rprint
except ImportError:
    print("Installing missing dependencies...")
    os.system(f"{sys.executable} -m pip install rich requests psutil")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.text import Text
    from rich.prompt import Prompt
    from rich import print as rprint

console = Console()
TODO_FILE = "kuchisake_todo.json"

class KuchisakeShell:
    def __init__(self):
        self.todos = self.load_todos()
        self.running = True

    def load_todos(self):
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, "r") as f:
                return json.load(f)
        return []

    def save_todos(self):
        with open(TODO_FILE, "w") as f:
            json.dump(self.todos, f, indent=4)

    def show_logo(self):
        logo = """
 ██   ██ ██    ██  ██████ ██   ██ ██ ███████  █████  ██   ██ ███████     ███████ ██   ██ ███████ ██      ██      
 ██  ██  ██    ██ ██      ██   ██ ██ ██      ██   ██ ██  ██  ██          ██      ██   ██ ██      ██      ██      
 █████   ██    ██ ██      ███████ ██ ███████ ███████ █████   █████       ███████ ███████ █████   ██      ██      
 ██  ██  ██    ██ ██      ██   ██ ██      ██ ██   ██ ██  ██  ██               ██ ██   ██ ██      ██      ██      
 ██   ██  ██████   ██████ ██   ██ ██ ███████ ██   ██ ██   ██ ███████     ███████ ██   ██ ███████ ███████ ███████ 
        """
        text = Text(logo, style="bold italic")
        # Creating a neon/violet gradient effect manually
        colored_logo = Text()
        lines = logo.split('\n')
        for i, line in enumerate(lines):
            color = f"rgb({150 + i*15}, {50}, {255})"
            colored_logo.append(line + "\n", style=color)
        
        console.print(Align.center(Panel(colored_logo, border_style="bright_magenta", padding=(1, 2))))

    def initialization_anim(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, pulse_style="bright_magenta"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("[bold purple]Initializing System Modules...", total=100)
            while not progress.finished:
                time.sleep(0.02)
                progress.update(task, advance=2)
        console.print("[bold green]✓ Systems Online[/bold green]")
        time.sleep(0.5)

    def main_menu(self):
        menu_text = Text()
        menu_text.append("\n1. [🍅] Pomodoro Method\n", style="bold white")
        menu_text.append("2. [📊] AI System Health & OS Monitor\n", style="bold white")
        menu_text.append("3. [💰] Crypto & Currency Ticker\n", style="bold white")
        menu_text.append("4. [📝] Smart Todo & Focus Manager\n", style="bold white")
        menu_text.append("5. [🧹] Log Cleaner / Temporary File Warden\n", style="bold white")
        menu_text.append("0. [🚪] Exit\n", style="bold red")

        panel = Panel(
            menu_text,
            title="[bold cyan]KUCHISAKE CONTROL CENTER[/bold cyan]",
            subtitle="[italic white]Select an option to proceed[/italic white]",
            border_style="bright_blue"
        )
        console.print(panel)

    def run_pomodoro(self, work_min=25, break_min=5):
        def timer(duration_min, label, color):
            duration_sec = duration_min * 60
            with Progress(
                TextColumn(f"[{color}]{label} [{{task.fields[status]}}]"),
                BarColumn(bar_width=None, complete_style=color),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task(label, total=duration_sec, status="Running")
                start_time = time.time()
                elapsed = 0
                paused = False
                
                # Simple non-blocking pause logic is hard in a CLI, 
                # we'll use a simple loop and check for a global/keyboard flag if possible
                # But for this version, we'll implement a simple countdown.
                while elapsed < duration_sec:
                    if not paused:
                        time.sleep(0.1)
                        elapsed = time.time() - start_time
                        progress.update(task, completed=elapsed)
                
            console.print("\a") # Beep
            console.print(f"[bold {color}]Time for {label} finished![/bold {color}]")

        console.clear()
        console.print(Panel(f"[bold red]POMODORO SESSION[/bold red]\nWork: {work_min}m | Break: {break_min}m"))
        timer(work_min, "FOCUS TIME", "bright_red")
        timer(break_min, "BREAK TIME", "bright_green")
        input("\nPress Enter to return to menu...")

    def system_monitor(self):
        console.clear()
        table = Table(title="AI System Health Monitor", border_style="bright_cyan")
        table.add_column("Component", style="cyan")
        table.add_column("Status", justify="right")
        table.add_column("Usage", justify="right")

        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = shutil.disk_usage("/")
        net = psutil.net_io_counters()

        def get_color(val):
            if val < 60: return "green"
            if val < 85: return "yellow"
            return "red"

        table.add_row("CPU", f"[{get_color(cpu)}]OK[/{get_color(cpu)}]", f"{cpu}%")
        table.add_row("Memory", f"[{get_color(mem.percent)}]{mem.percent}%[/{get_color(mem.percent)}]", f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB")
        table.add_row("Disk (Root)", f"[{get_color(disk.percent)}]{disk.percent}%[/{get_color(disk.percent)}]", f"{disk.free // (1024**3)}GB Free / {disk.total // (1024**3)}GB")
        table.add_row("Network (Sent)", "Active", f"{net.bytes_sent // (1024**2)} MB")
        table.add_row("Network (Recv)", "Active", f"{net.bytes_recv // (1024**2)} MB")

        console.print(panel := Panel(table, expand=False))
        input("\nPress Enter to return to menu...")

    def crypto_ticker(self):
        console.clear()
        with console.status("[bold green]Fetching live market data..."):
            try:
                # Fiat
                fiat = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5).json()
                usd = fiat['Valute']['USD']['Value']
                eur = fiat['Valute']['EUR']['Value']
                
                # Crypto
                crypto = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,solana&vs_currencies=usd&include_24hr_change=true", timeout=5).json()
            except Exception as e:
                console.print(f"[bold red]Error fetching data: {e}[/bold red]")
                input("\nPress Enter to return to menu...")
                return

        table = Table(title="Global Currency & Crypto Ticker", border_style="bright_yellow")
        table.add_column("Asset", style="bold")
        table.add_column("Price (USD)", justify="right")
        table.add_column("24h Change", justify="right")

        table.add_row("Bitcoin (BTC)", f"${crypto['bitcoin']['usd']:,}", f"{crypto['bitcoin']['usd_24h_change']:.2f}%")
        table.add_row("Ethereum (ETH)", f"${crypto['ethereum']['usd']:,}", f"{crypto['ethereum']['usd_24h_change']:.2f}%")
        table.add_row("Solana (SOL)", f"${crypto['solana']['usd']:,}", f"{crypto['solana']['usd_24h_change']:.2f}%")
        table.add_section()
        table.add_row("USD / RUB", f"{usd:.2f} ₽", "-")
        table.add_row("EUR / RUB", f"{eur:.2f} ₽", "-")

        console.print(Panel(table, expand=False))
        input("\nPress Enter to return to menu...")

    def todo_manager(self):
        while True:
            console.clear()
            table = Table(title="Focus Todo List", expand=True)
            table.add_column("ID", width=4)
            table.add_column("Task")
            table.add_column("Status")

            for i, todo in enumerate(self.todos):
                status = "[green]DONE[/green]" if todo['done'] else "[yellow]PENDING[/yellow]"
                task_text = Text(todo['task'])
                if todo['done']: task_text.stylize("strike green")
                table.add_row(str(i+1), task_text, status)

            console.print(table)
            console.print("\n[bold cyan]A[/bold cyan]: Add task | [bold green]D[/bold green]: Mark Done | [bold red]R[/bold red]: Remove | [bold white]Q[/bold white]: Back")
            choice = Prompt.ask("Action").lower()

            if choice == 'a':
                task = Prompt.ask("Enter task description")
                self.todos.append({"task": task, "done": False})
                self.save_todos()
            elif choice == 'd':
                idx = int(Prompt.ask("Enter ID")) - 1
                if 0 <= idx < len(self.todos):
                    self.todos[idx]['done'] = True
                    self.save_todos()
            elif choice == 'r':
                idx = int(Prompt.ask("Enter ID")) - 1
                if 0 <= idx < len(self.todos):
                    self.todos.pop(idx)
                    self.save_todos()
            elif choice == 'q':
                break

    def clean_system(self):
        console.clear()
        console.print("[bold yellow]Scanning for temporary files and logs...[/bold yellow]")
        
        paths_to_check = [
            ("/tmp", "Temporary Files"),
            ("/var/tmp", "System Temp Files"),
            ("/var/log", "System Logs")
        ]
        
        results = []
        total_size = 0

        for path, name in paths_to_check:
            if os.path.exists(path):
                try:
                    size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                               for dirpath, dirnames, filenames in os.walk(path) 
                               for filename in filenames)
                    results.append((name, path, size))
                    total_size += size
                except Exception:
                    results.append((name, path, 0))

        table = Table(title="System Cleanup Warden")
        table.add_column("Location", style="cyan")
        table.add_column("Path", style="dim")
        table.add_column("Size", justify="right")

        for name, path, size in results:
            table.add_row(name, path, f"{size / (1024**2):.2f} MB")

        console.print(table)
        console.print(f"\n[bold green]Total potentially recoverable space: {total_size / (1024**2):.2f} MB[/bold green]")
        
        confirm = Prompt.ask("Do you want to attempt cleaning (requires sudo for /var)? (y/n)", default="n")
        if confirm.lower() == 'y':
            console.print("[bold red]Note: Manual cleanup of system logs often requires root privileges.[/bold red]")
            # In a real shell we might call sudo rm -rf ...
            # For safety and portability in this script, we'll only demonstrate the intent.
            console.print("[italic]Simulating cleaning process...[/italic]")
            time.sleep(1)
            console.print("[bold green]Done! (Actual deletion skipped for safety in this demo mode)[/bold green]")
        
        input("\nPress Enter to return to menu...")

    def run(self):
        console.clear()
        self.show_logo()
        self.initialization_anim()
        
        while self.running:
            console.clear()
            self.show_logo()
            self.main_menu()
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "0"])

            if choice == "1":
                self.run_pomodoro()
            elif choice == "2":
                self.system_monitor()
            elif choice == "3":
                self.crypto_ticker()
            elif choice == "4":
                self.todo_manager()
            elif choice == "5":
                self.clean_system()
            elif choice == "0":
                console.print("[bold italic magenta]Goodbye, User. Kuchisake shutting down...[/bold italic magenta]")
                self.running = False

if __name__ == "__main__":
    try:
        shell = KuchisakeShell()
        shell.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user. Exiting...[/bold red]")
        sys.exit(0)
