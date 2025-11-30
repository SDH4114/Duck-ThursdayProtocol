using DOA.Core.Models;

namespace DOA.Core.Services;

public class NoteService
{
    private readonly PathService _paths;

    public NoteService(PathService paths)
    {
        _paths = paths;
    }

    private string SanitizeFileName(string name)
    {
        foreach (var c in Path.GetInvalidFileNameChars())
            name = name.Replace(c, '_');
        return name.Trim();
    }

    public CommandResponse CreateNote(string title, string? content = null)
    {
        if (string.IsNullOrWhiteSpace(title))
            return new CommandResponse { Status = "error", Message = "Title is empty." };

        var fileName = SanitizeFileName(title) + ".md";
        var fullPath = Path.Combine(_paths.NotesFolder, fileName);

        if (File.Exists(fullPath))
            return new CommandResponse { Status = "warn", Message = $"Note '{title}' already exists." };

        File.WriteAllText(fullPath, content ?? $"# {title}{Environment.NewLine}");
        return new CommandResponse
        {
            Status = "ok",
            Message = $"Note '{title}' created.",
            Data = new { path = fullPath }
        };
    }

    public CommandResponse ListNotes()
    {
        var files = Directory.GetFiles(_paths.NotesFolder, "*.md")
            .Select(Path.GetFileName)
            .ToList();

        return new CommandResponse
        {
            Status = "ok",
            Message = $"Found {files.Count} notes.",
            Data = files
        };
    }

    public CommandResponse ReadNote(string title)
    {
        var fileName = SanitizeFileName(title) + ".md";
        var fullPath = Path.Combine(_paths.NotesFolder, fileName);

        if (!File.Exists(fullPath))
            return new CommandResponse { Status = "error", Message = $"Note '{title}' not found." };

        var text = File.ReadAllText(fullPath);
        return new CommandResponse
        {
            Status = "ok",
            Message = $"Note '{title}' loaded.",
            Data = new { title, content = text }
        };
    }

    public CommandResponse DeleteNote(string title)
    {
        var fileName = SanitizeFileName(title) + ".md";
        var fullPath = Path.Combine(_paths.NotesFolder, fileName);

        if (!File.Exists(fullPath))
            return new CommandResponse { Status = "error", Message = $"Note '{title}' not found." };

        File.Delete(fullPath);
        return new CommandResponse
        {
            Status = "ok",
            Message = $"Note '{title}' deleted."
        };
    }
}