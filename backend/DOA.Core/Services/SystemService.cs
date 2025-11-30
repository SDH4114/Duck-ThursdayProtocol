using DOA.Core.Models;
using System.Runtime.InteropServices;

namespace DOA.Core.Services;

public class SystemService
{
    public CommandResponse GetInfo()
    {
        var info = new
        {
            OS = RuntimeInformation.OSDescription,
            Architecture = RuntimeInformation.OSArchitecture.ToString(),
            Framework = RuntimeInformation.FrameworkDescription,
            MachineName = Environment.MachineName,
            UserName = Environment.UserName,
            UptimeMinutes = (int)(DateTime.Now - ProcessStartTime()).TotalMinutes
        };

        return new CommandResponse
        {
            Status = "ok",
            Message = "System info.",
            Data = info
        };
    }

    public CommandResponse GetTime()
    {
        return new CommandResponse
        {
            Status = "ok",
            Message = "Current system time.",
            Data = new { now = DateTime.Now }
        };
    }

    private DateTime ProcessStartTime()
    {
        using var p = System.Diagnostics.Process.GetCurrentProcess();
        return p.StartTime;
    }
}