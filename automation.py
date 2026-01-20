"""
Automation module facade.
Dispatches to the correct platform implementation (macOS or Linux).
"""

import sys
import platform

# Detect Platform
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

if IS_MACOS:
    from automation_mac import run_workflow as run_workflow_mac, trigger_dictation as trigger_dictation_mac
    
    def run_workflow(config, trigger_voice=True):
        return run_workflow_mac(config, trigger_voice)
        
    def trigger_dictation():
        return trigger_dictation_mac()

elif IS_LINUX:
    from automation_linux import run_workflow as run_workflow_linux, trigger_dictation as trigger_dictation_linux
    
    def run_workflow(config, trigger_voice=True):
        return run_workflow_linux(config, trigger_voice)
        
    def trigger_dictation():
        return trigger_dictation_linux()

else:
    # Windows or other - minimal fallback
    def run_workflow(config, trigger_voice=True):
        print(f"❌ Platform '{sys.platform}' is not currently supported.")
        return False
        
    def trigger_dictation():
        return False
