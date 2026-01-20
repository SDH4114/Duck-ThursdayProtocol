#!/usr/bin/env python3
"""
Duck Of Apocalypse - AI Workflow Automation Tool (Single File Edition)
Simple TUI and CLI for launching AI agents with voice input.
"""

import sys
import os
import typer
# import rich  # Implicitly used

# Add current directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from config import (
    LauncherConfig, 
    load_config, 
    save_config, 
    get_available_terminals,
    get_available_agents
)
from automation import run_workflow

app = typer.Typer(help="Duck - AI Workflow Automation")
console = Console()


def display_header():
    """Display the launcher header."""
    console.print(Panel("Duck Of Apocalypse", style="bold yellow"))


def display_menu():
    """Display the main menu."""
    menu = Table(show_header=False, box=box.SIMPLE)
    menu.add_column("Option", style="cyan")
    menu.add_column("Description")
    
    menu.add_row("[1]", "Trigger")
    menu.add_row("[2]", "Settings")
    menu.add_row("[3]", "Hammerspoon Info")
    menu.add_row("[4]", "Exit")
    
    console.print(menu)


def display_config(config: LauncherConfig):
    """Display current configuration."""
    table = Table(title="Settings", box=box.SIMPLE)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Directory", config.target_directory)
    table.add_row("Terminal", config.terminal_app)
    table.add_row("Agent", config.agent_command)
    table.add_row("Voice Key", config.voice_key)
    
    console.print(table)


def settings_menu(config: LauncherConfig) -> LauncherConfig:
    """Display and handle the settings menu."""
    while True:
        console.clear()
        display_header()
        display_config(config)
        
        menu = Table(show_header=False, box=box.SIMPLE)
        menu.add_column("Option", style="cyan")
        menu.add_column("Setting")
        
        menu.add_row("[1]", "Directory")
        menu.add_row("[2]", "Terminal")
        menu.add_row("[3]", "Agent Command")
        menu.add_row("[4]", "Voice Key")
        menu.add_row("[5]", "Save & Return")
        menu.add_row("[6]", "Cancel")
        
        console.print(menu)
        
        choice = Prompt.ask("Option", choices=["1", "2", "3", "4", "5", "6"], default="5")
        
        if choice == "1":
            config.target_directory = Prompt.ask("Directory", default=config.target_directory)
        elif choice == "2":
            terminals = get_available_terminals()
            console.print(f"[dim]{', '.join(terminals)}[/dim]")
            config.terminal_app = Prompt.ask("Terminal", default=config.terminal_app)
        elif choice == "3":
            agents = get_available_agents()
            console.print(f"[dim]{', '.join(agents)}[/dim]")
            config.agent_command = Prompt.ask("Agent", default=config.agent_command)
        elif choice == "4":
            console.print("[dim]Examples: F5, F6, escape, space[/dim]")
            config.voice_key = Prompt.ask("Voice Key", default=config.voice_key)
        elif choice == "5":
            save_config(config)
            console.print("[green]Saved[/green]")
            return config
        elif choice == "6":
            return load_config()
    
    return config


@app.command()
def trigger(voice: bool = True):
    """
    Headless trigger for Hammerspoon.
    """
    config = load_config()
    run_workflow(config, trigger_voice=voice)


@app.command()
def tui():
    """Start the interactive TUI."""
    config = load_config()
    
    console.clear()
    display_header()
    display_config(config)
    
    while True:
        display_menu()
        
        try:
            choice = Prompt.ask("Option", choices=["1", "2", "3", "4"], default="1")
        except KeyboardInterrupt:
            choice = "4"
        
        if choice == "1":
            console.print("Launching...")
            run_workflow(config, trigger_voice=True)
            
        elif choice == "2":
            config = settings_menu(config)
            console.clear()
            display_header()
            display_config(config)

        elif choice == "3":
            console.print()
            console.print("[bold]Hammerspoon Setup:[/bold]")
            console.print('hs.hotkey.bind({"cmd", "alt"}, "L", function()', style="dim")
            console.print('    hs.execute("/path/to/Duck trigger", true)', style="dim")
            console.print('end)', style="dim")
            console.print()
            
        elif choice == "4":
            console.print("Bye")
            break


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Entry point."""
    if ctx.invoked_subcommand is None:
        tui()


if __name__ == "__main__":
    app()
