#!/usr/bin/env python3
"""Transform lowlighter/metrics output into the custom README layout."""

from __future__ import annotations

import re
import sys
from pathlib import Path

WIDTH = 480
HEIGHT = 52

CUSTOM_CSS = (
    ".items-wrapper{width:100%;height:100%;display:flex;flex-direction:column;"
    "justify-content:flex-start;box-sizing:border-box;padding:0;margin:0}"
    ".items-wrapper section,.items-wrapper .row{width:100%;margin:0;padding:0}"
    ".items-wrapper .calendar{margin:0;padding:0;width:100%}"
    ".items-wrapper .calendar svg{width:100%;height:28px;margin:0}"
    ".items-wrapper .field{font-size:15px;margin:0;padding:0}"
    ".items-wrapper section>.field{margin:0}"
)


def find_generated_path() -> Path:
    for path in (
        Path("metrics_renders/metrics.generated.svg"),
        Path("metrics.generated.svg"),
    ):
        if path.exists():
            return path
    raise FileNotFoundError(
        "Generated metrics SVG not found. Expected metrics_renders/metrics.generated.svg"
    )


def extract_base_styles(source: str) -> str:
    match = re.search(r"<style>(.*?)</style>", source, re.DOTALL)
    if not match:
        raise ValueError("Could not find base styles in generated SVG")
    return match.group(1)


def extract_calendar_field(source: str) -> str:
    match = re.search(r'(<div class="field calendar">.*?</div>)', source, re.DOTALL)
    if not match:
        raise ValueError("Could not find calendar field in generated SVG")
    calendar = match.group(1)
    calendar = re.sub(r'\swidth="[^"]*"', "", calendar, count=1)
    calendar = re.sub(r'\sheight="[^"]*"', "", calendar, count=1)
    return re.sub(
        r'(<svg[^>]*viewBox="0 0 210 11")',
        r'\1 width="100%" height="28"',
        calendar,
        count=1,
    )


def extract_repos_field(source: str) -> str:
    contrib = re.search(r"Contributed to \d+ repositories", source)
    if not contrib:
        raise ValueError("Could not find repositories field in generated SVG")

    field_start = source.rfind('<div class="field">', 0, contrib.start())
    if field_start == -1:
        raise ValueError("Could not find repositories field wrapper")

    field_end = source.find("</div>", contrib.end())
    if field_end == -1:
        raise ValueError("Could not find repositories field end")

    return source[field_start : field_end + len("</div>")]


def build_svg(base_styles: str, calendar: str, repos: str) -> str:
    styles = f"{base_styles}{CUSTOM_CSS}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" class="">
    <defs>
        <style/>
    </defs>
    <style>{styles}</style>
    <style/>
    <foreignObject x="0" y="0" width="{WIDTH}" height="{HEIGHT}">
        <div xmlns="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink" class="items-wrapper">
            <section>
                <div class="row">
                    <section>
                        {calendar}
                        {repos}
                    </section>
                </div>
            </section>
        </div>
        <div xmlns="http://www.w3.org/1999/xhtml" id="metrics-end"></div>
    </foreignObject>
</svg>
"""


def main() -> int:
    source_path = find_generated_path()
    source = source_path.read_text(encoding="utf-8")
    output = build_svg(
        extract_base_styles(source),
        extract_calendar_field(source),
        extract_repos_field(source),
    )
    Path("metrics.svg").write_text(output, encoding="utf-8")
    print(f"Wrote compact metrics.svg from {source_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
