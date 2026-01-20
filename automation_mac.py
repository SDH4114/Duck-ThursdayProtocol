"""
AppleScript automation for terminal control and workflow execution.
Uses native terminal scripting to avoid Accessibility permission issues.
"""

import subprocess
import time
import os
from typing import Optional

from config import LauncherConfig


def run_applescript(script: str) -> tuple[bool, str]:
    """
    Execute an AppleScript and return success status and output.
    
    Returns:
        Tuple of (success: bool, output/error: str)
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "AppleScript execution timed out"
    except Exception as e:
        return False, str(e)


def run_command_in_terminal_app(directory: str, command: str) -> bool:
    """
    Run a command in Terminal.app using native AppleScript.
    No Accessibility permissions required.
    """
    # Escape for AppleScript string
    escaped_dir = directory.replace('"', '\\"')
    escaped_cmd = command.replace('"', '\\"')
    
    script = f'''
    tell application "Terminal"
        activate
        do script "cd \\"{escaped_dir}\\" && {escaped_cmd}"
    end tell
    '''
    success, error = run_applescript(script)
    if not success:
        print(f"Error: {error}")
    return success


def run_command_in_iterm(directory: str, command: str) -> bool:
    """
    Run a command in iTerm2 using native AppleScript.
    No Accessibility permissions required.
    """
    escaped_dir = directory.replace('"', '\\"')
    escaped_cmd = command.replace('"', '\\"')
    
    script = f'''
    tell application "iTerm"
        activate
        tell current window
            create tab with default profile
            tell current session
                write text "cd \\"{escaped_dir}\\" && {escaped_cmd}"
            end tell
        end tell
    end tell
    '''
    success, error = run_applescript(script)
    if not success:
        # Try creating new window if no window exists
        script = f'''
        tell application "iTerm"
            activate
            create window with default profile
            tell current window
                tell current session
                    write text "cd \\"{escaped_dir}\\" && {escaped_cmd}"
                end tell
            end tell
        end tell
        '''
        success, error = run_applescript(script)
        if not success:
            print(f"Error: {error}")
    return success


def run_command_in_ghostty(directory: str, command: str) -> bool:
    """
    Run a command in Ghostty by launching it with a command.
    Ghostty doesn't have AppleScript support, so we use subprocess.
    """
    # Ghostty can be launched with -e flag to run a command
    # We'll create a shell command that cd's and runs the agent
    full_command = f'cd "{directory}" && {command}'
    
    try:
        # First, try to open Ghostty and let it use its default shell
        # Then use the open command with a custom script approach
        subprocess.run(
            ["open", "-a", "Ghostty"],
            check=True
        )
        time.sleep(0.5)
        
        # For Ghostty, we need to use a workaround since it doesn't support AppleScript
        # Create a temporary script to run
        script_path = "/tmp/jarvisgem_cmd.sh"
        with open(script_path, "w") as f:
            f.write(f'#!/bin/bash\ncd "{directory}"\n{command}\n')
        os.chmod(script_path, 0o755)
        
        # Use osascript to open Ghostty with the script
        # This is a fallback approach using Terminal as intermediary
        result = subprocess.run(
            ["open", "-a", "Ghostty", script_path],
            capture_output=True,
            text=True
        )
        
        # If that doesn't work, fall back to opening Ghostty and using pbpaste trick
        if result.returncode != 0:
            # Copy command to clipboard and paste
            subprocess.run(
                ["bash", "-c", f'echo "cd \\"{directory}\\" && {command}" | pbcopy'],
                check=True
            )
            print("   📋 Command copied to clipboard - paste with Cmd+V in Ghostty")
            return True
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_command_in_warp(directory: str, command: str) -> bool:
    """Run a command in Warp terminal."""
    # Warp has some AppleScript support
    escaped_dir = directory.replace('"', '\\"')
    escaped_cmd = command.replace('"', '\\"')
    
    script = f'''
    tell application "Warp"
        activate
    end tell
    delay 0.5
    tell application "System Events"
        keystroke "cd \\"{escaped_dir}\\" && {escaped_cmd}"
        keystroke return
    end tell
    '''
    success, error = run_applescript(script)
    if not success:
        print(f"Error: {error}")
        # Fallback to clipboard
        subprocess.run(
            ["bash", "-c", f'echo "cd \\"{directory}\\" && {command}" | pbcopy'],
            check=True
        )
        print("   📋 Command copied to clipboard - paste with Cmd+V")
    return success


def trigger_dictation(voice_key: str = "F5") -> bool:
    """
    Trigger voice dictation by pressing the configured key.
    """
    # Map common key names to AppleScript key codes
    key_codes = {
        "F1": 122, "F2": 120, "F3": 99, "F4": 118,
        "F5": 96, "F6": 97, "F7": 98, "F8": 100,
        "F9": 101, "F10": 109, "F11": 103, "F12": 111,
        "escape": 53, "space": 49, "return": 36,
    }
    
    key = voice_key.upper() if voice_key.startswith("F") else voice_key.lower()
    code = key_codes.get(key, key_codes.get(voice_key, None))
    
    if code is None:
        print(f"   Unknown key: {voice_key}")
        return False
    
    script = f'''
    tell application "System Events"
        key code {code}
    end tell
    '''
    success, error = run_applescript(script)
    if not success:
        print(f"   Could not press key: {error}")
    return success


def run_workflow(config: LauncherConfig, trigger_voice: bool = True) -> bool:
    """
    Execute the full automation workflow using native terminal scripting.
    
    Args:
        config: Launcher configuration
        trigger_voice: Whether to trigger voice dictation at the end
    
    Returns:
        True if all steps succeeded, False otherwise
    """
    app = config.terminal_app.lower()
    directory = config.get_expanded_directory()
    command = config.agent_command
    
    print(f"🚀 Starting workflow...")
    print(f"   Terminal: {config.terminal_app}")
    print(f"   Directory: {directory}")
    print(f"   Command: {command}")
    
    # Choose the right method based on terminal app
    print("   [1/2] Launching terminal with command...")
    
    if app == "terminal":
        success = run_command_in_terminal_app(directory, command)
    elif app == "iterm" or app == "iterm2":
        success = run_command_in_iterm(directory, command)
    elif app == "ghostty":
        success = run_command_in_ghostty(directory, command)
    elif app == "warp":
        success = run_command_in_warp(directory, command)
    else:
        # Generic fallback - try Terminal.app style
        print(f"   ⚠️  Unknown terminal '{config.terminal_app}', trying generic approach...")
        success = run_command_in_terminal_app(directory, command)
    
    if not success:
        print("   Failed to launch terminal")
        return False
    
    if trigger_voice:
        print(f"   Waiting for terminal to focus...")
        time.sleep(3.0)  # Longer wait for terminal + agent to start
        print(f"   Pressing voice key: {config.voice_key} (code: {get_key_code(config.voice_key)})")
        trigger_dictation(config.voice_key)
    
    print("   Done")
    return True


def get_key_code(voice_key: str) -> int:
    """Get key code for debugging."""
    key_codes = {
        "F1": 122, "F2": 120, "F3": 99, "F4": 118,
        "F5": 96, "F6": 97, "F7": 98, "F8": 100,
        "F9": 101, "F10": 109, "F11": 103, "F12": 111,
    }
    key = voice_key.upper() if voice_key.startswith("F") else voice_key
    return key_codes.get(key, -1)


if __name__ == "__main__":
    # Test the automation
    from config import load_config
    config = load_config()
    run_workflow(config, trigger_voice=False)
