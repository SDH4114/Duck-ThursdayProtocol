namespace DOA.Core.Services;

public class PathService
{
    public string BaseFolder =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "DOA");

    public string NotesFolder => Path.Combine(BaseFolder, "notes");
    public string LogsFolder  => Path.Combine(BaseFolder, "logs");

    public PathService()
    {
        Directory.CreateDirectory(BaseFolder);
        Directory.CreateDirectory(NotesFolder);
        Directory.CreateDirectory(LogsFolder);
    }
}