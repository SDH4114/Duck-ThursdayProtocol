using DOA.Core.Models;
using DOA.Core.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<ConfigService>();
builder.Services.AddSingleton<PathService>();
builder.Services.AddSingleton<NoteService>();
builder.Services.AddSingleton<ShellService>();
builder.Services.AddSingleton<SystemService>();
builder.Services.AddSingleton<CommandDispatcher>();

var app = builder.Build();

app.UseStaticFiles(); // wwwroot

app.MapGet("/", () => Results.Redirect("/index.html"));

app.MapPost("/command", (CommandRequest request, CommandDispatcher dispatcher) =>
{
    var response = dispatcher.Dispatch(request);
    return Results.Json(response);
});

app.Run("http://localhost:7070");