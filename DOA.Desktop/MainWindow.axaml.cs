using System;
using System.Collections.Generic;
using System.Text;
using System.Timers;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using DOA.Core.Models;
using DOA.Core.Services;

namespace DOA.Desktop;

public partial class MainWindow : Window
{
    private readonly CommandDispatcher _dispatcher;

    private readonly List<string> _history = new();
    private int _historyIndex = -1;

    private TextBlock? _inputLine;
    private string _currentInput = string.Empty;
    private int _caretIndex = 0;

    private bool _cursorVisible = true;
    private readonly Timer _cursorTimer;

    public MainWindow()
    {
        InitializeComponent();

        // Инициализируем ядро DOA
        var pathService = new PathService();
        var noteService = new NoteService(pathService);
        var shellService = new ShellService();
        var systemService = new SystemService();
        _dispatcher = new CommandDispatcher(noteService, shellService, systemService);

        // Ловим клавиши и текст
        this.KeyDown += OnKeyDown;
        this.TextInput += OnTextInput;

        // Таймер мигания курсора
        _cursorTimer = new Timer(500);
        _cursorTimer.Elapsed += (_, _) =>
        {
            _cursorVisible = !_cursorVisible;
            Dispatcher.UIThread.InvokeAsync(RenderInputLine);
        };
        _cursorTimer.Start();

        AppendOutputBlock("DOA Desktop Terminal online. Type 'help'.");

        CreateInputLine();

        this.Opened += (_, _) => this.Focus();
        this.PointerPressed += (_, _) => this.Focus();
    }

    // ========================= INPUT LINE =========================

    private void CreateInputLine()
    {
        _currentInput = string.Empty;
        _caretIndex = 0;

        _inputLine = new TextBlock
        {
            FontFamily = new FontFamily("SF Mono, Consolas, Monaco, Courier New, monospace"),
            FontSize = 14,
            Foreground = Brushes.White
        };

        ConsolePanel.Children.Add(_inputLine);
        RenderInputLine();
    }

    private void RenderInputLine()
    {
        if (_inputLine == null)
            return;

        if (_caretIndex < 0) _caretIndex = 0;
        if (_caretIndex > _currentInput.Length) _caretIndex = _currentInput.Length;

        var left = _currentInput.Substring(0, _caretIndex);
        var right = _currentInput.Substring(_caretIndex);

        // ❗ Делаем тонкий курсор БЕЗ пробела
        var cursorChar = _cursorVisible ? "|" : "";

        _inputLine.Text = $"> {left}{cursorChar}{right}";
    }

    // ========================= ВВОД СИМВОЛОВ =========================

    private void OnTextInput(object? sender, TextInputEventArgs e)
    {
        if (string.IsNullOrEmpty(e.Text))
            return;

        // Вставка текста в позицию курсора
        _currentInput = _currentInput.Insert(_caretIndex, e.Text);
        _caretIndex += e.Text.Length;

        RenderInputLine();
        e.Handled = true;
    }

    // ========================= КЛАВИШИ (ENTER, СТРЕЛКИ и т.п.) =========================

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        switch (e.Key)
        {
            case Key.Enter:
                ExecuteCommand(_currentInput);
                e.Handled = true;
                break;

            case Key.Back:
                if (_caretIndex > 0 && _currentInput.Length > 0)
                {
                    _currentInput = _currentInput.Remove(_caretIndex - 1, 1);
                    _caretIndex--;
                    RenderInputLine();
                }
                e.Handled = true;
                break;

            case Key.Delete:
                if (_caretIndex < _currentInput.Length && _currentInput.Length > 0)
                {
                    _currentInput = _currentInput.Remove(_caretIndex, 1);
                    RenderInputLine();
                }
                e.Handled = true;
                break;

            case Key.Left:
                if (_caretIndex > 0)
                {
                    _caretIndex--;
                    RenderInputLine();
                }
                e.Handled = true;
                break;

            case Key.Right:
                if (_caretIndex < _currentInput.Length)
                {
                    _caretIndex++;
                    RenderInputLine();
                }
                e.Handled = true;
                break;

            case Key.Home:
                _caretIndex = 0;
                RenderInputLine();
                e.Handled = true;
                break;

            case Key.End:
                _caretIndex = _currentInput.Length;
                RenderInputLine();
                e.Handled = true;
                break;

            case Key.Up:
                if (_history.Count > 0)
                {
                    if (_historyIndex < _history.Count - 1)
                        _historyIndex++;

                    _currentInput = _history[_historyIndex];
                    _caretIndex = _currentInput.Length;
                    RenderInputLine();
                }
                e.Handled = true;
                break;

            case Key.Down:
                if (_historyIndex > 0)
                {
                    _historyIndex--;
                    _currentInput = _history[_historyIndex];
                }
                else
                {
                    _historyIndex = -1;
                    _currentInput = string.Empty;
                }
                _caretIndex = _currentInput.Length;
                RenderInputLine();
                e.Handled = true;
                break;
        }
    }

    // ========================= ВЫПОЛНЕНИЕ КОМАНДЫ =========================

    private void ExecuteCommand(string cmd)
    {
        // Фиксируем текущую строку как обычную (без курсора)
        var frozen = cmd;
        if (_inputLine != null)
        {
            _inputLine.Text = $"> {frozen}";
        }

        var trimmed = cmd.Trim();

        // Пустая строка — просто новый промпт
        if (string.IsNullOrWhiteSpace(trimmed))
        {
            CreateInputLine();
            return;
        }

        // История
        _history.Insert(0, cmd);
        _historyIndex = -1;

        // clear
        if (trimmed == "clear")
        {
            ConsolePanel.Children.Clear();
            CreateInputLine();
            return;
        }

        // help
        if (trimmed == "help")
        {
            AppendOutputBlock(
                "Commands:\n" +
                "  system.info\n" +
                "  system.time\n" +
                "  note.new \"Title\" text\n" +
                "  note.list\n" +
                "  ls / pwd / git status\n" +
                "  clear"
            );
            CreateInputLine();
            return;
        }

        // Вызов ядра
        CommandResponse response;
        try
        {
            response = _dispatcher.Dispatch(new CommandRequest { Raw = cmd });
        }
        catch (Exception ex)
        {
            AppendErrorBlock("Internal error: " + ex.Message);
            CreateInputLine();
            return;
        }

        var status = response.Status?.ToUpperInvariant() ?? "UNKNOWN";
        var message = response.Message ?? string.Empty;

        if (status == "OK")
            AppendOutputBlock($"[{status}] {message}");
        else
            AppendErrorBlock($"[{status}] {message}");

        if (response.Data is not null)
        {
            RenderData(response.Data);
        }

        // ❗ ВАЖНО: новый промпт ВСЕГДА после ответа:
        // > comand
        // D.O.A.> answer
        // > _
        CreateInputLine();
    }

    // ========================= ВЫВОД БЛОКОВ =========================

    private void AppendOutputBlock(string text)
    {
        if (string.IsNullOrEmpty(text))
            return;

        var lines = text.Replace("\r\n", "\n").Split('\n');

        for (int i = 0; i < lines.Length; i++)
        {
            var display = i == 0
                ? $"D.O.A.> {lines[i]}"
                : $"         {lines[i]}";

            ConsolePanel.Children.Add(new TextBlock
            {
                Text = display,
                Foreground = new SolidColorBrush(Color.Parse("#89d185")),
                FontFamily = new FontFamily("SF Mono, Consolas, Monaco, Courier New, monospace"),
                FontSize = 14
            });
        }
    }

    private void AppendErrorBlock(string text)
    {
        if (string.IsNullOrEmpty(text))
            return;

        var lines = text.Replace("\r\n", "\n").Split('\n');

        for (int i = 0; i < lines.Length; i++)
        {
            var display = i == 0
                ? $"D.O.A.> {lines[i]}"
                : $"         {lines[i]}";

            ConsolePanel.Children.Add(new TextBlock
            {
                Text = display,
                Foreground = new SolidColorBrush(Color.Parse("#F48771")),
                FontFamily = new FontFamily("SF Mono, Consolas, Monaco, Courier New, monospace"),
                FontSize = 14
            });
        }
    }

    // ========================= ОТРИСОВКА DATA =========================

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

        // заметка Title + Content
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