from fastapi import FastAPI, Header, HTTPException, Request, status

from app.config import get_webhook_secret
from app.security import verify_signature


app = FastAPI(
    title="ReviewRelay",
    version="0.1.0",
    description="A test-first foundation for secure GitHub pull-request webhook processing.",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhooks/github", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
) -> dict[str, str | None]:
    raw_body = await request.body()

    try:
        secret = get_webhook_secret()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if not verify_signature(secret, raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    return {
        "status": "accepted",
        "event": x_github_event,
        "delivery": x_github_delivery,
    }
