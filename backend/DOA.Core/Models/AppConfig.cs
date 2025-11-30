namespace DOA.Core.Models;

public class AppConfig
{
    public required string Theme { get; set; }
    public required string NotesPath { get; set; }
    public required string LogsPath { get; set; }

    public required ShellSettings Shell { get; set; }
    public required SystemSettings System { get; set; }
}

public class ShellSettings
{
    public required string DefaultPrompt { get; set; }
    public int FontSize { get; set; }
}

public class SystemSettings
{
    public required string StartupMessage { get; set; }
}