from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.oidc.challenge_service import (
    get_challenge_status,
    submit_challenge,
    submit_challenge_demo,
    refresh_challenge,
)

router = APIRouter()


class SubmitRequest(BaseModel):
    signed_challenge: str
    certificate: str


@router.get("/challenge/{challenge_id}/status")
async def challenge_status(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await get_challenge_status(db, challenge_id)
    if result is None:
        return JSONResponse({"error": "Challenge not found"}, status_code=404)
    return result


@router.post("/challenge/{challenge_id}/submit")
async def challenge_submit(
    challenge_id: str,
    body: SubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await submit_challenge(
        db, challenge_id, body.signed_challenge, body.certificate
    )
    if "error" in result:
        return JSONResponse(
            {"error": result["error"]}, status_code=result["status_code"]
        )
    return {"redirect_url": result["redirect_url"]}


@router.post("/challenge/{challenge_id}/demo-submit")
async def challenge_demo_submit(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await submit_challenge_demo(db, challenge_id)
    if "error" in result:
        return JSONResponse(
            {"error": result["error"]}, status_code=result["status_code"]
        )
    return {"redirect_url": result["redirect_url"]}


@router.post("/challenge/{challenge_id}/refresh")
async def challenge_refresh(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await refresh_challenge(db, challenge_id)
    if "error" in result:
        return JSONResponse(
            {"error": result["error"]}, status_code=result["status_code"]
        )
    return {
        "challenge_id": result["challenge_id"],
        "qr_svg": result["qr_svg"],
        "expire_seconds": result["expire_seconds"],
    }
