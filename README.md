# no-api-py

A tiny HTTP server that gives you a random JSON “reason” to *not* build an API.

It’s basically an excuse generator over HTTP, with:
- **Random reasons** loaded from `reasons.json`
- **Occasional rare motivation** (1% chance it says something vaguely productive)
- **Built-in rate limiting** so people can’t DDoS your vibe

Licenced under **The Unlicense**, because this is a project I did for fun.

---

## What it does

### `GET /`
Returns JSON with a `reason`.

Most of the time:
- **HTTP 406 Not Acceptable** with a random reason

Rarely (1%):
- **HTTP 200 OK** with a “fine, I’ll be productive” message and `"sigh": true`

If you spam it:
- **HTTP 429 Too Many Requests** with a `retry_after` value and a `Retry-After` header

---

## Example responses

### Normal (406)
```json
{
  "reason": "No."
}
```

### Rare productive moment (200)
```json
{
  "reason": "Ugh... fine... I'll do something productive I guess.",
  "sigh": true
}
```

### Rate-limited (429)
```json
{
  "reason": "Too many requests. Calm down.",
  "retry_after": 42
}
```

---

## Requirements

- Python **3.11+** recommended (uses modern type hints)
- A `reasons.json` file in the same directory

---

## Setup

Clone it, drop in a `reasons.json` (or use the one provided), run it.

### 1) Create `reasons.json` (optional)

Example:

```json
[
  "No.",
  "Because I said so.",
  "The vibes are off.",
  "Try again after coffee."
]
```

### 2) Run the server

```bash
python3 run.py
```

By default it listens on **port 8000**.

---

## Configuration (environment variables)

You can tune the port and rate-limiting via env vars:

| Variable | Default | Meaning |
|---|---:|---|
| `NOAPI_PORT` | `8000` | Port the server listens on |
| `NOAPI_MAX_REQUESTS` | `5` | Max requests allowed per time window per IP |
| `NOAPI_TIME_WINDOW` | `10` | Time window in seconds |
| `NOAPI_BLOCK_DURATION` | `60` | How long (seconds) an IP is blocked after exceeding the limit |

Example:

```bash
export NOAPI_PORT=9000
export NOAPI_MAX_REQUESTS=20
export NOAPI_TIME_WINDOW=10
export NOAPI_BLOCK_DURATION=30
python3 run.py
```

---

## Try it

```bash
curl -i http://localhost:8000/
```

Spam it (politely, for science):

```bash
for i in {1..10}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/; done
```

---

## Notes on behaviour

- Rate limiting is **per-client IP**.
- When you exceed the limit, you’re blocked for `NOAPI_BLOCK_DURATION` seconds.
- The server is **multi-threaded** via `ThreadingHTTPServer`.
- Shared state (`request_log`, `blocked_ips`) is guarded by a `Lock` for thread safety.

---

## Project structure

Typical layout:

```
.
├── run.py
└── reasons.json
```

---

## Inspiration

Inspired by a similar project in another language. This is the Python-flavoured version, because why not.

---

## Licence

**The Unlicense**.

Do what you want. Break it. Fix it. Ship it. Print it out and eat it.
