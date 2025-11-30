namespace DOA.Core.Models;

public class CommandRequest
{
    // Полностью сырая строка, как её ввёл пользователь
    public string Raw { get; set; } = string.Empty;

    // Вычисляемое свойство: имя команды (первое слово)
    public string Command
    {
        get
        {
            if (string.IsNullOrWhiteSpace(Raw)) return string.Empty;
            var parts = Raw.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            return parts.Length > 0 ? parts[0].Trim().ToLowerInvariant() : string.Empty;
        }
    }

    // Вычисляемое свойство: аргументы (остальные слова)
    public List<string> Args
    {
        get
        {
            if (string.IsNullOrWhiteSpace(Raw)) return new List<string>();
            return Raw
                .Split(' ', StringSplitOptions.RemoveEmptyEntries)
                .Skip(1)
                .ToList();
        }
    }
}