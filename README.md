# crypto-sentiment-bot

A local tool for personal research and learning about cryptocurrency market sentiment. It reads public information, applies a lightweight keyword classifier, and creates local reports. It is not investment advice.

## Scope

- Personal, non-commercial, read-only use only.
- No trading, custody, portfolio management, or automated order placement.
- Follow applicable laws, data-source terms, and API rules.
- Do not use this project for market manipulation, spam, access-control bypasses, or other unlawful activity.

## Data sources and usage

The project is designed for publicly accessible RSS/Atom feeds and other public, read-only APIs. It uses data to collect article metadata, clean and deduplicate text, calculate a simple sentiment score, and create a local research report.

It must not bypass login pages, CAPTCHA, access controls, or paywalls. Prefer official APIs and respect their rate limits, attribution, caching, and removal requirements.

## No publishing, messaging, or password storage

- No posts, comments, likes, reposts, or other outbound platform actions.
- No direct messages, automated replies, or user notifications.
- No trading, transfers, withdrawals, or other financial actions.
- No passwords, private keys, seed phrases, API secrets, or cookies are collected or stored.
- This MVP does not require authentication. Do not add credentials to source code, logs, or data files.

## Deleted content handling

The collector stores a source URL, title, publication time when available, and fetch time so that a record can be located. If a source removes an item, delete the corresponding local record and any derived report or cache that reproduces its content. Keep only the minimum non-content audit information needed to process a removal request. The tool cannot detect every upstream deletion; users can remove the local `data/` directory at any time.

Logs and reports should not contain passwords, tokens, or other sensitive information.

## Expected request frequency

The default polling interval is 900 seconds (15 minutes) per run. The tool fetches only the configured feeds, uses a short request timeout, stores duplicates only once, and supports a configurable interval. Respect the strictest limit published by each data provider. Stop or slow down when receiving rate-limit or access-denied responses.

## Privacy

The intended deployment is local and data-minimizing. The project does not sell or intentionally share personal data and is not designed to collect identity information. Local databases, reports, logs, and caches are controlled by the user. If a third-party API or analysis service is added, review its privacy policy and send only the minimum required public data.

## MVP quick start

Requires Python 3.10 or newer. The MVP uses only the Python standard library.

Run an offline demo:

```bash
python app.py --demo
```

This creates `data/sentiment.db` and `data/report.md`. The SQLite database keeps historical articles and prevents duplicate links from being inserted.

To read public RSS/Atom feeds:

```bash
cp config.example.json config.json
python app.py --config config.json --limit 30
```

On Windows PowerShell:

```powershell
Copy-Item config.example.json config.json
python .\app.py --config .\config.json --limit 30
```

For low-frequency continuous polling:

```powershell
python .\app.py --config .\config.json --watch
python .\app.py --config .\config.json --watch --interval 1800
```

Customize `feeds`, `interval_seconds`, `positive_words`, and `negative_words` in `config.json`. The classifier is intentionally simple: positive keywords add points, negative keywords subtract points, and zero is neutral. It is a pipeline demo, not a professional sentiment model or trading signal.

## Local dashboard and exports

After collecting at least one batch, start the local dashboard:

```powershell
python .\dashboard.py --database .\data\sentiment.db
```

Open `http://127.0.0.1:8765` in a browser. The dashboard is bound to localhost by default and exposes a read-only `/api/articles` endpoint.

Export the local database without making network requests:

```powershell
python .\export_data.py --format csv --output .\articles.csv
python .\export_data.py --format json --output .\articles.json
```

Run the standard-library test suite:

```powershell
python -m unittest -v
```

Build historical trend analytics and top-title terms:

```powershell
python .\analytics.py --database .\data\sentiment.db --days 30
```

Check configured feeds before a longer polling session:

```powershell
python .\healthcheck.py --config .\config.json
```

The health check uses read-only HTTP requests and writes `data/health.json`. The dashboard also shows daily sentiment counts and the most frequent title terms.

Create an aggregate sentiment snapshot:

```powershell
python .\snapshot.py --output-dir .\data
```

The snapshot labels the recent sample as `bullish`, `bearish`, or `mixed` from the average score. It is a descriptive research metric, not a trading signal.

Manage local retention and deletion requests:

```powershell
python .\cleanup_data.py --output-dir .\data --link "https://example.com/article"
python .\cleanup_data.py --output-dir .\data --older-than 90
```

These commands affect only the local SQLite database. Run the collector again to regenerate the Markdown report after deletion.

## Layered architecture

The implementation is organized around small layers under `crypto_sentiment/`:

```text
crypto_sentiment/
  config.py       settings and validation
  models.py       Article domain model
  text.py         text normalization
  analyzer.py     pure sentiment scoring
  feeds.py        RSS/Atom transport and parsing
  repository.py   SQLite persistence
  reporting.py    Markdown report generation
  service.py      application orchestration
app.py            CLI composition root
dashboard.py      local read-only HTTP presentation
analytics.py      historical analytics command
healthcheck.py    feed diagnostics command
export_data.py    local export command
```

The dependency direction is intentional: domain and analysis code do not know about SQLite or HTTP, while the application service coordinates the adapters. This makes it easier to replace the feed source, storage backend, or sentiment model independently.

## Disclaimer

Sentiment results can be noisy, delayed, biased, or wrong. Outputs are for personal research only and are not investment, legal, tax, or other professional advice. Users are responsible for their own decisions and consequences.
