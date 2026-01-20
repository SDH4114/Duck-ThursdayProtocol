"""
Linux automation for terminal control and workflow execution.
Uses subprocess and standard linux tools (xdotool, wmctrl).
"""

import subprocess
import time
import shutil
import os
from config import LauncherConfig


def is_tool_available(name: str) -> bool:
    """Check if a command line tool is available."""
    return shutil.which(name) is not None


def run_command_in_gnome_terminal(directory: str, command: str) -> bool:
    """Run command in gnome-terminal."""
    try:
        subprocess.Popen([
            "gnome-terminal",
            "--", 
            "bash", "-c", f"cd \"{directory}\" && {command}; exec bash"
        ])
        return True
    except Exception as e:
        print(f"Error launching gnome-terminal: {e}")
        return False


def run_command_in_konsole(directory: str, command: str) -> bool:
    """Run command in KDE Konsole."""
    try:
        subprocess.Popen([
            "konsole",
            "--workdir", directory,
            "-e", "bash", "-c", f"{command}; exec bash"
        ])
        return True
    except Exception as e:
        print(f"Error launching konsole: {e}")
        return False


def run_command_in_xterm(directory: str, command: str) -> bool:
    """Run command in xterm."""
    try:
        subprocess.Popen([
            "xterm",
            "-e", f"cd \"{directory}\" && {command}; exec bash"
        ])
        return True
    except Exception as e:
        print(f"Error launching xterm: {e}")
        return False
        
        
def run_command_in_kitty(directory: str, command: str) -> bool:
    """Run command in kitty."""
    try:
        subprocess.Popen([
            "kitty",
            "--directory", directory,
            "bash", "-c", f"{command}; exec bash"
        ])
        return True
    except Exception as e:
        print(f"Error launching kitty: {e}")
        return False
        
        
def run_command_in_alacritty(directory: str, command: str) -> bool:
    """Run command in alacritty."""
    try:
        # Alacritty is tricky with executing commands directly securely, 
        # but modern versions support --command or -e
        subprocess.Popen([
            "alacritty",
            "--working-directory", directory,
            "-e", "bash", "-c", f"{command}; exec bash"
        ])
        return True
    except Exception as e:
        print(f"Error launching alacritty: {e}")
        return False


def run_generic_terminal(terminal_app: str, directory: str, command: str) -> bool:
    """Try to run a generic terminal with common flags."""
    # Try -e style first (common for many terminals)
    try:
        subprocess.Popen([
            terminal_app,
            "-e", f"bash -c 'cd \"{directory}\" && {command}; exec bash'"
        ])
        return True
    except FileNotFoundError:
        print(f"Terminal '{terminal_app}' not found.")
        return False
    except Exception as e:
        print(f"Error launching {terminal_app}: {e}")
        return False


def trigger_dictation() -> bool:
    """
    Trigger dictation on Linux.
    Currently a placeholder as Linux lacks a standardized dictation system.
    """
    print("   ℹ️  Voice Dictation on Linux is not yet supported universally.")
    print("   💡 Tip: Configure a custom shortcut in your Window Manager if you have a dictation tool.")
    return True  # Return true to not fail the workflow


def run_workflow(config: LauncherConfig, trigger_voice: bool = True) -> bool:
    """
    Execute the automation workflow on Linux.
    """
    app = config.terminal_app.lower()
    directory = config.get_expanded_directory()
    command = config.agent_command
    
    print(f"🚀 Starting workflow (Linux)...")
    print(f"   Terminal: {config.terminal_app}")
    print(f"   Directory: {directory}")
    print(f"   Command: {command}")
    
    success = False
    
    if app == "gnome-terminal":
        success = run_command_in_gnome_terminal(directory, command)
    elif app == "konsole":
        success = run_command_in_konsole(directory, command)
    elif app == "xterm":
        success = run_command_in_xterm(directory, command)
    elif app == "kitty":
        success = run_command_in_kitty(directory, command)
    elif app == "alacritty":
        success = run_command_in_alacritty(directory, command)
    else:
        print(f"   ⚠️  Unknown terminal '{config.terminal_app}', trying generic launch...")
        success = run_generic_terminal(config.terminal_app, directory, command)
        
    if not success:
        print("   ❌ Failed to launch terminal.")
        return False
        
    if trigger_voice:
        trigger_dictation()
        
    print("   ✅ Workflow complete!")
    return True
