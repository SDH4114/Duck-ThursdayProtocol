using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;
using DOA.Core.Models;
using DOA.Core.Services;

namespace DOA.Desktop;

public partial class MainWindow : Window
{
    private readonly CommandDispatcher _dispatcher;

    private readonly List<string> _history = new();
    private int _historyIndex = -1;

    public MainWindow()
    {
        InitializeComponent();

        var pathService = new PathService();
        var noteService = new NoteService(pathService);
        var shellService = new ShellService();
        var systemService = new SystemService();

        _dispatcher = new CommandDispatcher(noteService, shellService, systemService);

        InputBox.KeyDown += InputBoxOnKeyDown;

        AppendOutputBlock("DOA Core desktop online. Type 'help' for commands.");

        this.Opened += (_, _) => InputBox.Focus();
    }

    // ===================== РЕНДЕР СТРОК ======================

    /// <summary>
    /// Эхо команды пользователя: "> something" (белый, без D.O.A.)
    /// </summary>
    private void AppendCommandEcho(string text)
    {
        var line = new TextBlock
        {
            Text = $"> {text}",
            Foreground = Brushes.White,
            FontFamily = new FontFamily("SF Mono, Consolas, Monaco, Courier New, monospace"),
            FontSize = 13
        };
        ConsolePanel.Children.Add(line);
    }

    /// <summary>
    /// Блок обычного вывода: первая строка "D.O.A.> ...", остальные просто с отступом.
    /// </summary>
    private void AppendOutputBlock(string text)
    {
        if (string.IsNullOrEmpty(text))
            return;

        var lines = text.Replace("\r\n", "\n").Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            var lineText = lines[i];
            string display;

            if (i == 0)
                display = $"D.O.A.> {lineText}";
            else
                display = $"         {lineText}"; // 9 пробелов под "D.O.A.>"

            var tb = new TextBlock
            {
                Text = display,
                Foreground = new SolidColorBrush(Color.Parse("#89d185")),
                FontFamily = new FontFamily("SF Mono, Consolas, Monaco, Courier New, monospace"),
                FontSize = 13
            };
            ConsolePanel.Children.Add(tb);
        }
    }

    /// <summary>
    /// Блок ошибок: первая строка "D.O.A.> ...", остальные с отступом, красным.
    /// </summary>
    private void AppendErrorBlock(string text)
    {
        if (string.IsNullOrEmpty(text))
            return;

        var lines = text.Replace("\r\n", "\n").Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            var lineText = lines[i];
            string display;

            if (i == 0)
                display = $"D.O.A.> {lineText}";
            else
                display = $"         {lineText}";

            var tb = new TextBlock
            {
                Text = display,
                Foreground = new SolidColorBrush(Color.Parse("#F48771")),
                FontFamily = new FontFamily("SF Mono, Consolas, Monaco, Courier New, monospace"),
                FontSize = 13
            };
            ConsolePanel.Children.Add(tb);
        }
    }

    // ===================== ОБРАБОТКА ВВОДА ======================

    private void InputBoxOnKeyDown(object? sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter)
        {
            var raw = InputBox.Text ?? string.Empty;
            InputBox.Text = string.Empty;

            if (string.IsNullOrWhiteSpace(raw))
                return;

            _history.Insert(0, raw);
            _historyIndex = -1;

            AppendCommandEcho(raw);
            HandleCommand(raw);

            e.Handled = true;
        }
        else if (e.Key == Key.Up)
        {
            if (_history.Count == 0) return;
            if (_historyIndex < _history.Count - 1)
                _historyIndex++;

            InputBox.Text = _history[_historyIndex];
            InputBox.CaretIndex = InputBox.Text!.Length;
            e.Handled = true;
        }
        else if (e.Key == Key.Down)
        {
            if (_historyIndex > 0)
            {
                _historyIndex--;
                InputBox.Text = _history[_historyIndex];
            }
            else
            {
                _historyIndex = -1;
                InputBox.Text = string.Empty;
            }

            InputBox.CaretIndex = InputBox.Text!.Length;
            e.Handled = true;
        }
    }

    // ===================== ЛОГИКА КОМАНД ======================

    private void HandleCommand(string raw)
    {
        var trimmed = raw.Trim();

        if (trimmed == "clear")
        {
            ConsolePanel.Children.Clear();
            return;
        }

        if (trimmed == "help")
        {
            var helpText = new StringBuilder();
            helpText.AppendLine("Commands:");
            helpText.AppendLine("  system.info");
            helpText.AppendLine("  system.time");
            helpText.AppendLine("  note.new \"Title\" text");
            helpText.AppendLine("  note.list");
            helpText.AppendLine("  ls / pwd / git status");
            helpText.Append("  clear");
            AppendOutputBlock(helpText.ToString());
            return;
        }

        CommandResponse response;

        try
        {
            response = _dispatcher.Dispatch(new CommandRequest { Raw = raw });
        }
        catch (Exception ex)
        {
            AppendErrorBlock("Internal error: " + ex.Message);
            return;
        }

        var status = response.Status?.ToUpperInvariant() ?? "UNKNOWN";
        var message = response.Message ?? string.Empty;

        if (status == "OK")
            AppendOutputBlock($"[{status}] {message}");
        else
            AppendErrorBlock($"[{status}] {message}");

        if (response.Data is null)
            return;

        RenderData(response.Data);
    }

    // ===================== ОТРИСОВКА DATA ======================

    private void RenderData(object data)
    {
        var type = data.GetType();
        var stdoutProp = type.GetProperty("Stdout") ?? type.GetProperty("stdout");
        var stderrProp = type.GetProperty("Stderr") ?? type.GetProperty("stderr");

        // shell stdout/stderr
        if (stdoutProp != null || stderrProp != null)
        {
            var stdout = stdoutProp?.GetValue(data) as string;
            var stderr = stderrProp?.GetValue(data) as string;

            if (!string.IsNullOrWhiteSpace(stdout))
                AppendOutputBlock(stdout.TrimEnd());

            if (!string.IsNullOrWhiteSpace(stderr))
                AppendErrorBlock(stderr.TrimEnd());

            return;
        }

        // список строк
        if (data is IEnumerable<string> list)
        {
            var sb = new StringBuilder();
            foreach (var item in list)
                sb.AppendLine(item);

            AppendOutputBlock(sb.ToString().TrimEnd());
            return;
        }

        // заметка Title+Content
        var titleProp = type.GetProperty("Title");
        var contentProp = type.GetProperty("Content");

        if (titleProp != null && contentProp != null)
        {
            var title = titleProp.GetValue(data) as string;
            var content = contentProp.GetValue(data) as string;

            var sb = new StringBuilder();
            if (!string.IsNullOrEmpty(title))
                sb.AppendLine("# " + title);
            if (!string.IsNullOrEmpty(content))
                sb.Append(content);

            AppendOutputBlock(sb.ToString());
            return;
        }

        // fallback
        AppendOutputBlock(data.ToString() ?? string.Empty);
    }
}