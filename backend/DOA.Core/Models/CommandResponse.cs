namespace DOA.Core.Models;

public class CommandResponse
{
    // ok / error / warn
    public string Status { get; set; } = "ok";

    // Человеческое сообщение
    public string Message { get; set; } = string.Empty;

    // Дополнительные данные (например, список файлов или заметок)
    public object? Data { get; set; }
}