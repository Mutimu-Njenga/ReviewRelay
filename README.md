# ReviewRelay

ReviewRelay is a test-first foundation for a GitHub pull-request review
service. The current milestone accepts signed GitHub webhook requests,
rejects invalid signatures, persists delivery IDs, and exposes a health endpoint.

## Current scope

Implemented:

- `GET /health`
- `POST /webhooks/github`
- `X-Hub-Signature-256` verification using SHA-256 HMAC
- constant-time signature comparison
- rejection of malformed non-ASCII signature headers before persistence
- SQLite-backed delivery ID persistence and duplicate-delivery responses
- tests for health, signatures, missing headers, persistence, and duplicates

Not yet implemented:

- background queue and worker
- pull-request review rules
- GitHub API comments
- deployment

The service records a verified delivery once and returns `"status": "duplicate"`
for a repeated delivery ID. It does not yet perform downstream review work.

## Local setup on Windows PowerShell

```powershell
cd $HOME\Projects\ReviewRelay
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
$env:GITHUB_WEBHOOK_SECRET = "development-secret"
```

For local testing, the SQLite database path can be set with
`REVIEWRELAY_DB_PATH`; otherwise the app uses its configured default path.

If PowerShell blocks virtual-environment activation, use the interpreter
directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

## Run tests

```powershell
python -m pytest -q
```

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Then open:

- API documentation: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/health`

## Why the raw request body matters

GitHub signs the exact bytes sent in the webhook request. Parsing and
re-serializing JSON can change whitespace, ordering, or encoding. The
HMAC must therefore be computed from `await request.body()` before any
transformation.

## Security boundary

Never commit a real webhook secret. `.env` is ignored by Git, and the
repository includes only `.env.example`.
