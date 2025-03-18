import os
import subprocess
from rich.console import Console
from trading.database import setup_database

console = Console()

def run_command(command, description):
    """Runs a command and logs output."""
    console.print(f"\n⏳ [bold yellow]{description}...[/bold yellow]\n")
    process = subprocess.run(command, shell=True)
    
    if process.returncode == 0:
        console.print(f"✅ [bold green]{description} complete![/bold green]")
    else:
        console.print(f"❌ [bold red]Error running {description}![/bold red]")

def main():
    console.print("[bold cyan]📈 Stock Market Simulator Setup & Run[/bold cyan]", justify="center")

    # Step 1: Initialize the Database
    setup_database()

    # Step 2: Fetch Real-Time Stock Data
    run_command("python -m utils.fetch_data", "Fetching real-time stock data")

    # Step 3: Train Machine Learning Models
    run_command("python -m models.train_models", "Training machine learning models")

    # Step 4: Run the CLI Trading Simulator
    console.print("\n🎮 [bold magenta]Launching the Trading Simulator...[/bold magenta]\n")
    subprocess.run("python -m ui.cli", shell=True)

if __name__ == "__main__":
    main()