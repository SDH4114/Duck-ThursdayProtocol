# 🦆 Duck

One-file AI workflow automation for macOS.

## Quick Start

**Double-click `Duck`** — that's it!

## Build From Source

```bash
# Install PyInstaller
pip3 install pyinstaller

# Build single-file executable
pyinstaller --onefile --name Duck duck.py

# Result: dist/Duck
```

## Usage

### Double-click Duck
Opens Terminal with interactive menu:
```
==================================================
          🦆  D U C K
      AI Workflow Automation
==================================================

  [1]  Trigger Duck
  [2]  Settings
  [3]  Hammerspoon Hotkey
  [4]  Exit
```

### Hammerspoon Hotkey
1. Run Duck, select [3]
2. Copy the Lua snippet
3. Paste into `~/.hammerspoon/init.lua`
4. Reload Hammerspoon
5. Press **Cmd+Alt+L** to trigger Duck headlessly

## Data Location

All settings stored in:
```
~/Desktop/duckinfo/
├── config.json    # Settings
└── times/         # Run logs
```

## Gatekeeper (First Run)

If macOS blocks the app:
1. Right-click Duck → Open
2. Click "Open" in the dialog
3. Only needed once

## Send to Friend

Just send them **one file**: `Duck`

They double-click it. Done.