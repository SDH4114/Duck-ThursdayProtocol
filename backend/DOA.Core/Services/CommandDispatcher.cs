using DOA.Core.Models;

namespace DOA.Core.Services;

public class CommandDispatcher
{
    private readonly NoteService _notes;
    private readonly ShellService _shell;
    private readonly SystemService _system;

    public CommandDispatcher(
        NoteService notes,
        ShellService shell,
        SystemService system)
    {
        _notes = notes;
        _shell = shell;
        _system = system;
    }

    public CommandResponse Dispatch(CommandRequest request)
    {
        if (request == null || string.IsNullOrWhiteSpace(request.Raw))
        {
            return new CommandResponse
            {
                Status = "error",
                Message = "Empty request."
            };
        }

        var cmd = request.Command; // первое слово в lower-case

        switch (cmd)
        {
            // ========== SYSTEM ==========

            case "system.info":
                return _system.GetInfo();

            case "system.time":
                return _system.GetTime();

            // ========== SHELL / OS ==========

            case "run":
            {
                var appName = GetAfterCommand(request.Raw, "run");
                return _shell.RunApp(appName);
            }

            case "open":
            {
                var target = GetAfterCommand(request.Raw, "open");
                return _shell.OpenTarget(target);
            }

            // ========== NOTES ==========

            case "note.new":
            {
                var (title, content) = ParseNoteNew(request.Raw);
                return _notes.CreateNote(title, content);
            }

            case "note.list":
                return _notes.ListNotes();

            case "note.open":
            {
                var title = GetAfterCommand(request.Raw, "note.open");
                return _notes.ReadNote(title);
            }

            case "note.delete":
            {
                var title = GetAfterCommand(request.Raw, "note.delete");
                return _notes.DeleteNote(title);
            }

            // ========== FALLBACK → SHELL ==========

            default:
                // Всё, что не узнали как DOA-команду → отправляем как обычный shell
                return _shell.RunShellCommand(request.Raw);
        }
    }

    /// <summary>
    /// Возвращает всё, что идёт после командного слова (run, open, note.open и т.д.)
    /// Например: "run Prism Launcher" -> "Prism Launcher"
    /// </summary>
    private static string GetAfterCommand(string raw, string commandToken)
    {
        if (string.IsNullOrWhiteSpace(raw))
            return string.Empty;

        var prefix = commandToken.Trim();
        if (!raw.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
            return string.Empty;

        var rest = raw[prefix.Length..].TrimStart();
        return rest;
    }

    /// <summary>
    /// Разбор note.new:
    /// 1) note.new "My Title" some content here
    ///    -> title = My Title, content = some content here
    /// 2) note.new Title rest of content
    ///    -> title = Title, content = rest of content
    /// </summary>
    private static (string title, string? content) ParseNoteNew(string raw)
    {
        var body = GetAfterCommand(raw, "note.new");

        if (string.IsNullOrWhiteSpace(body))
            return (string.Empty, null);

        body = body.Trim();

        if (body.StartsWith("\""))
        {
            // Ищем закрывающую кавычку
            var closing = body.IndexOf('"', 1);
            if (closing > 1)
            {
                var title = body.Substring(1, closing - 1);
                var rest = body[(closing + 1)..].Trim();
                return (title, string.IsNullOrWhiteSpace(rest) ? null : rest);
            }
        }

        // Без кавычек: первое слово — заголовок, остальное — контент
        var parts = body.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        var titleSimple = parts[0];
        var contentSimple = parts.Length > 1
            ? string.Join(' ', parts.Skip(1))
            : null;

        return (titleSimple, contentSimple);
    }
}