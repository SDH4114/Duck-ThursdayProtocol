-- Duck Of Apocalypse - Hammerspoon Config
-- Add this to ~/.hammerspoon/init.lua

local duckPath = os.getenv("HOME") .. "/giti/Duck-Of-Apocalypse/duck"

-- Cmd+Alt+L to trigger Duck
hs.hotkey.bind({"cmd", "alt"}, "L", function()
    hs.execute(duckPath .. " trigger", true)
end)

-- Reload on save
hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", function(files)
    for _, file in pairs(files) do
        if file:sub(-4) == ".lua" then
            hs.reload()
            return
        end
    end
end):start()

hs.alert.show("Duck loaded")
