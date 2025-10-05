Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "cmd /c npx -y @playwright/mcp@latest --port 30045", 0
Set WshShell = Nothing