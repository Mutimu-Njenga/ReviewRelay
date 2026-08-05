# ReviewRelay

ReviewRelay is a test-first foundation for a GitHub pull-request review
service. The current milestone accepts signed GitHub webhook requests,
rejects invalid signatures, and exposes a health endpoint.

## Current scope

Implemented:

- `GET /health`
- `POST /webhooks/github`
- `X-Hub-Signature-256` verification using SHA-256 HMAC
- constant-time signature comparison
- tests for health, valid signatures, invalid signatures, and missing signatures

Not yet implemented:

- database persistence
- duplicate-delivery protection
- background queue and worker
- pull-request review rules
- GitHub API comments
- deployment

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
