from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass


URL_RE = re.compile(r"https?://[^\s<>\"]+")
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style).*?</\1>", re.IGNORECASE | re.DOTALL)
SPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class WebResult:
    ok: bool
    text: str


class WebReader:
    def __init__(self, *, timeout_seconds: int = 20, max_chars: int = 6000) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_chars = max_chars

    def read_url(self, url: str) -> WebResult:
        if not URL_RE.fullmatch(url):
            return WebResult(ok=False, text=f"Некорректный URL: {url}")

        try:
            content_type, body = self._fetch(url)
        except OSError as exc:
            return WebResult(ok=False, text=f"Не смог прочитать сайт: {exc}")

        if "text/html" in content_type or "application/xhtml" in content_type:
            text = self._html_to_text(body)
        else:
            text = body.decode("utf-8", errors="replace")

        return WebResult(ok=True, text=f"Источник: {url}\n\n{self._trim(text)}")

    def search(self, query: str) -> WebResult:
        query = query.strip()
        if not query:
            return WebResult(ok=False, text="Напиши, что искать в интернете.")

        url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
        try:
            _, body = self._fetch(url)
        except OSError as exc:
            return WebResult(ok=False, text=f"Не смог выполнить поиск: {exc}")

        results = self._parse_duckduckgo_results(body.decode("utf-8", errors="replace"))
        if not results:
            return WebResult(ok=False, text="Поиск не вернул читаемых результатов.")

        lines = [f"Результаты поиска: {query}", ""]
        for index, (title, href, snippet) in enumerate(results[:5], start=1):
            lines.append(f"{index}. {title}")
            lines.append(href)
            if snippet:
                lines.append(snippet)
            lines.append("")
        return WebResult(ok=True, text=self._trim("\n".join(lines)))

    def extract_url(self, text: str) -> str | None:
        match = URL_RE.search(text)
        if not match:
            return None
        return match.group(0).rstrip(".,)]}")

    def _fetch(self, url: str) -> tuple[str, bytes]:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,text/plain,application/xhtml+xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "")
            return content_type, response.read(1_000_000)

    def _html_to_text(self, body: bytes) -> str:
        value = body.decode("utf-8", errors="replace")
        value = SCRIPT_STYLE_RE.sub(" ", value)
        value = TAG_RE.sub(" ", value)
        value = html.unescape(value)
        return SPACE_RE.sub(" ", value).strip()

    def _parse_duckduckgo_results(self, value: str) -> list[tuple[str, str, str]]:
        blocks = re.findall(
            r'<a rel="nofollow" class="result__a" href="(?P<href>[^"]+)">(?P<title>.*?)</a>.*?'
            r'<a class="result__snippet".*?>(?P<snippet>.*?)</a>',
            value,
            flags=re.DOTALL,
        )
        results: list[tuple[str, str, str]] = []
        for href, title, snippet in blocks:
            clean_href = html.unescape(href)
            if clean_href.startswith("//"):
                clean_href = "https:" + clean_href
            if "uddg=" in clean_href:
                parsed = urllib.parse.urlparse(clean_href)
                params = urllib.parse.parse_qs(parsed.query)
                clean_href = params.get("uddg", [clean_href])[0]
            results.append(
                (
                    self._clean_html(title),
                    clean_href,
                    self._clean_html(snippet),
                )
            )
        return results

    def _clean_html(self, value: str) -> str:
        return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", value))).strip()

    def _trim(self, value: str) -> str:
        if len(value) <= self.max_chars:
            return value
        return value[: self.max_chars] + "\n...[trimmed]"
