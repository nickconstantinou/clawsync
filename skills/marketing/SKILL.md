---
name: crawl4ai
description: AI-friendly web crawler for content extraction
metadata:
  {
    "openclaw":
      {
        "emoji": "🕷️",
        "requires": { "bins": ["python3", "pip"] },
      },
  }
---

# Crawl4AI - AI-Friendly Web Crawler

Use Crawl4AI to turn websites into clean, LLM-ready Markdown for RAG, content extraction, and data pipelines.

## Installation

```bash
pip install -U crawl4ai
crawl4ai-setup
crawl4ai-doctor
```

Or with Docker:
```bash
docker run -d -p 8000:8000 unclecode/crawl4ai:latest
```

## What It Does

- **LLM-Ready Markdown** — Clean, structured output with headings, tables, code blocks
- **Fast** — Async browser pool, caching, minimal hops
- **Full Control** — Sessions, proxies, cookies, user scripts
- **Adaptive Intelligence** — Learns site patterns, explores only what matters
- **Deploy Anywhere** — Zero keys needed, CLI and Docker

## Python Usage

### Basic Crawl

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com",
        )
        print(result.markdown)

asyncio.run(main())
```

### With LLM Extraction

```python
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com/products",
            extraction_strategy=LLMExtractionStrategy(
                provider="openai/gpt-4",
                prompt="Extract all product names and prices"
            ),
        )
        print(result.extracted_content)
```

### Deep Crawl

```python
from crawl4ai import AsyncWebCrawler
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://docs.example.com",
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_pages=100,
                max_depth=3
            ),
        )
        print(result.markdown)
```

## CLI Usage

```bash
# Basic crawl
crwl https://example.com -o markdown

# Deep crawl
crwl https://docs.example.com --deep-crawl bfs --max-pages 10

# With LLM extraction
crwl https://example.com/products -q "Extract all product prices"

# Using CSS selectors
crwl https://example.com -s ".product-title, .product-price"

# With session
crwl https://example.com --session my-session

# Proxy
crwl https://example.com --proxy http://proxy:8080
```

## Options

| Option | Description |
|--------|-------------|
| `--url` | Target URL |
| `-o, --output` | Output format: markdown, html, text |
| `--deep-crawl` | Strategy: bfs, dfs |
| `--max-pages` | Max pages to crawl |
| `--max-depth` | Max depth for deep crawl |
| `-q, --question` | LLM extraction question |
| `-s, --selector` | CSS selectors to extract |
| `--session` | Session name for stateful crawling |
| `--proxy` | Proxy URL |

## Use Cases

1. **Content for LLMs** — Turn any website into clean Markdown for RAG
2. **Data Extraction** — Extract structured data with CSS or LLM
3. **Research** — Deep crawl documentation or articles
4. **Monitoring** — Track changes on websites
5. **Blog Content** — Crawl articles from your sources

## Environment

Requires:
- Python 3.8+
- Playwright (installed via `crawl4ai-setup`)
- Or Docker

## Notes

- Crawl4AI is not currently installed in this environment
- Can be installed via: `pip install crawl4ai`
- For Docker: `docker run -p 8000:8000 unclecode/crawl4ai:latest`
- API available at `http://localhost:8000` when running
