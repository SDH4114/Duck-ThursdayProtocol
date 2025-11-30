using System.Text.Json;

namespace DOA.Core.Services;

public class ConfigService
{
    private readonly string _configPath;

    public ConfigService()
    {
        var root = Directory.GetCurrentDirectory();
        _configPath = Path.Combine(root, "Config", "doa.config.json");
        Console.WriteLine($"[DOA CONFIG] Using config: {_configPath}");
    }

    public T Load<T>()
    {
        if (!File.Exists(_configPath))
            throw new FileNotFoundException("Config file not found: " + _configPath);

        var json = File.ReadAllText(_configPath);

        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        var result = JsonSerializer.Deserialize<T>(json, options);

        if (result == null)
            throw new Exception("Failed to deserialize config file: " + _configPath);

        return result;
    }
}