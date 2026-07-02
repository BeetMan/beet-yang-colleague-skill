from __future__ import annotations

import argparse
import concurrent.futures
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET


BASE = "https://beet.select"
USER_AGENT = "Mozilla/5.0 (Codex; owner-approved crawl)"


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def fetch_text(url: str, *, tries: int = 6, timeout: int = 60) -> str:
    delay = 2.0
    last = ""
    for attempt in range(tries):
        result = subprocess.run(
            [
                "curl.exe",
                "-sS",
                "-L",
                "-A",
                USER_AGENT,
                "--max-time",
                str(timeout),
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        last = result.stdout[:200] or result.stderr[:200]
        if result.returncode == 0 and "error code: 1102" not in result.stdout:
            return result.stdout
        time.sleep(delay)
        delay = min(delay * 1.7, 30)
    raise RuntimeError(f"bad response for {url}: {last!r}")


def parse_sitemap_index(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    urls: list[str] = []
    for sitemap in root:
        for child in sitemap:
            if strip_ns(child.tag) == "loc" and child.text:
                urls.append(child.text)
    return urls


def parse_sitemap(xml_text: str) -> list[dict[str, str | int]]:
    root = ET.fromstring(xml_text)
    entries: list[dict[str, str | int]] = []
    for item in root:
        loc = None
        lastmod = None
        for child in item:
            if strip_ns(child.tag) == "loc":
                loc = child.text
            elif strip_ns(child.tag) == "lastmod":
                lastmod = child.text
        if loc and lastmod:
            match = re.search(r"/posts/(\d+)$", loc)
            if match:
                entries.append({"url": loc, "id": int(match.group(1)), "datetime": lastmod})
    return entries


class PostParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_content = False
        self.content_depth = 0
        self.skip_depth = 0
        self.text_parts: list[str] = []
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        cls = attrs.get("class") or ""
        if tag == "title":
            self.in_title = True
        if tag == "div" and "leading-[1.6]" in cls and "content" in cls:
            self.in_content = True
            self.content_depth = 1
        elif self.in_content:
            self.content_depth += 1
        if self.in_content and (tag == "button" or "modal" in cls or "link_preview" in cls):
            self.skip_depth += 1
        if self.in_content and not self.skip_depth and tag == "br":
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if self.skip_depth:
            self.skip_depth -= 1
        if self.in_content:
            self.content_depth -= 1
            if self.content_depth <= 0:
                self.in_content = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.in_content and not self.skip_depth:
            self.text_parts.append(data)

    def post_text(self) -> str:
        text = "".join(self.text_parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        return text.strip()


def build_index(max_year: str) -> list[dict[str, str | int]]:
    sitemap_index = parse_sitemap_index(fetch_text(f"{BASE}/sitemap.xml"))
    entries: list[dict[str, str | int]] = []

    def load_sitemap(url: str) -> list[dict[str, str | int]]:
        return parse_sitemap(fetch_text(url))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(load_sitemap, url) for url in sitemap_index]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            entries.extend(future.result())
            if index % 100 == 0:
                print(f"sitemaps={index} entries={len(entries)}", flush=True)

    entries.sort(key=lambda entry: int(entry["id"]), reverse=True)
    selected: list[dict[str, str | int]] = []
    for entry in entries:
        selected.append(entry)
        if str(entry["datetime"]).startswith(max_year + "-"):
            break
    return selected


def crawl_posts(entries: list[dict[str, str | int]], output: Path) -> list[dict[str, str | int]]:
    if output.exists():
        posts = json.loads(output.read_text(encoding="utf-8"))
    else:
        posts = []
    seen = {int(post["id"]) for post in posts}

    for index, entry in enumerate(entries, 1):
        post_id = int(entry["id"])
        if post_id in seen:
            continue
        html = fetch_text(str(entry["url"]))
        parser = PostParser()
        parser.feed(html)
        post = {
            "id": post_id,
            "url": entry["url"],
            "datetime": entry["datetime"],
            "title": parser.title.strip(),
            "text": parser.post_text(),
        }
        posts.append(post)
        seen.add(post_id)
        if len(posts) % 50 == 0:
            output.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"saved posts={len(posts)} latest={post_id}", flush=True)
        time.sleep(0.2)

    posts.sort(key=lambda post: int(post["id"]), reverse=True)
    output.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    return posts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to-year", default="2023")
    parser.add_argument(
        "--output",
        default="colleagues/beet-yang/knowledge/beet-select-posts-through-2023.json",
    )
    parser.add_argument("--index-only", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = build_index(args.to_year)
    print(
        f"index entries={len(entries)} first={entries[0] if entries else None} "
        f"last={entries[-1] if entries else None}",
        flush=True,
    )
    if args.index_only:
        index_output = output.with_suffix(".index.json")
        index_output.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"saved index={index_output}", flush=True)
        return 0

    posts = crawl_posts(entries, output)
    print(f"done posts={len(posts)} output={output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
