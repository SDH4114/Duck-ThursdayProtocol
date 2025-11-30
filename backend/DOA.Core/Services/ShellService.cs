using System.Diagnostics;
using DOA.Core.Models;

namespace DOA.Core.Services;

public class ShellService
{
    public CommandResponse RunApp(string appName)
    {
        if (string.IsNullOrWhiteSpace(appName))
        {
            return new CommandResponse
            {
                Status = "error",
                Message = "App name is empty."
            };
        }

        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "open",
                UseShellExecute = false
            };

            psi.ArgumentList.Add("-a");
            psi.ArgumentList.Add(appName);

            Process.Start(psi);

            return new CommandResponse
            {
                Status = "ok",
                Message = $"App '{appName}' launched."
            };
        }
        catch (Exception ex)
        {
            return new CommandResponse
            {
                Status = "error",
                Message = $"Failed to launch app '{appName}': {ex.Message}"
            };
        }
    }

    public CommandResponse OpenTarget(string target)
    {
        if (string.IsNullOrWhiteSpace(target))
        {
            return new CommandResponse
            {
                Status = "error",
                Message = "Target is empty."
            };
        }

        try
        {
            bool isUrl = target.Contains("://", StringComparison.OrdinalIgnoreCase)
                         || target.Contains(".com", StringComparison.OrdinalIgnoreCase)
                         || target.Contains(".az", StringComparison.OrdinalIgnoreCase)
                         || target.StartsWith("www.", StringComparison.OrdinalIgnoreCase);

            var psi = new ProcessStartInfo
            {
                FileName = "open",
                UseShellExecute = false
            };

            psi.ArgumentList.Add(target);

            Process.Start(psi);

            var kind = isUrl ? "URL" : "path";
            return new CommandResponse
            {
                Status = "ok",
                Message = $"Opened {kind} '{target}'."
            };
        }
        catch (Exception ex)
        {
            return new CommandResponse
            {
                Status = "error",
                Message = $"Failed to open '{target}': {ex.Message}"
            };
        }
    }

    public CommandResponse RunShellCommand(string raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
        {
            return new CommandResponse
            {
                Status = "error",
                Message = "Empty shell command."
            };
        }

        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "/bin/zsh",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            psi.ArgumentList.Add("-lc");
            psi.ArgumentList.Add(raw);

            using var proc = new Process { StartInfo = psi };
            proc.Start();

            string stdout = proc.StandardOutput.ReadToEnd();
            string stderr = proc.StandardError.ReadToEnd();

            proc.WaitForExit();
            int exitCode = proc.ExitCode;

            string status = exitCode == 0 ? "ok" : "error";
            string msg = exitCode == 0
                ? $"Shell command executed successfully (exit {exitCode})."
                : $"Shell command failed (exit {exitCode}).";

            return new CommandResponse
            {
                Status = status,
                Message = msg,
                Data = new
                {
                    command = raw,
                    stdout,
                    stderr,
                    exitCode
                }
            };
        }
        catch (Exception ex)
        {
            return new CommandResponse
            {
                Status = "error",
                Message = $"Exception while running shell command: {ex.Message}"
            };
        }
    }
}