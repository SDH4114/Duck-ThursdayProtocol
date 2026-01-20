# Hammerspoon Integration for JarvisGem

To optimize performance and avoid permission issues with python keyboard listeners, use [Hammerspoon](https://www.hammerspoon.org/) to trigger JarvisGem.

## 1. Install Hammerspoon
Download and install from [hammerspoon.org](https://www.hammerspoon.org/).

## 2. Locate your built JarvisGem executable
After building (see below), your executable will be at:
`~/giti/Wald_AI/jarvisGem/dist/JarvisGem`

## 3. Configure Hammerspoon (`~/.hammerspoon/init.lua`)

Add this code to your `init.lua` file. This binds `Cmd + Option + L` to trigger JarvisGem.

```lua
-- JarvisGem Integration
local jarvisPath = os.getenv("HOME") .. "/giti/Duck-Of-Apocalypse/dist/JarvisGem"

hs.hotkey.bind({"cmd", "alt"}, "L", function()
  hs.notify.new({title="JarvisGem", informativeText="Launching AI Workflow..."}):send()
  
  -- Run the trigger command headlessly
  hs.execute(jarvisPath .. " trigger", true)
end)
```

## 4. Reload Config
Click the Hammerspoon icon in the menubar and select **Reload Config**.

## Why this is better?
- **Zero background CPU usage** for Python.
- **Native macOS hotkey handling** (faster, more reliable).
- **No Accessibility permissions** needed for Python to listen to keys.
