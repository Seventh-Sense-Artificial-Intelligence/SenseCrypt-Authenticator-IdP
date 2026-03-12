from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_user
from app.schemas.product.oauth_application import (
    OAuthApplicationCreate,
    OAuthApplicationCreateResponse,
    OAuthApplicationRead,
    OAuthApplicationUpdate,
    RotateSecretResponse,
)
from app.services.product import application_service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post(
    "/", response_model=OAuthApplicationCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_application(
    data: OAuthApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        app, client_secret = await application_service.create_application(
            db, current_user.id, data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response_data = OAuthApplicationRead.model_validate(app).model_dump()
    response_data["client_secret"] = client_secret
    return OAuthApplicationCreateResponse(**response_data)


@router.get("/", response_model=list[OAuthApplicationRead])
async def list_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await application_service.list_applications(db, current_user.id)


@router.get("/{app_id}", response_model=OAuthApplicationRead)
async def get_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await application_service.get_application(db, current_user.id, app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return app


@router.put("/{app_id}", response_model=OAuthApplicationRead)
async def update_application(
    app_id: str,
    data: OAuthApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        app = await application_service.update_application(
            db, current_user.id, app_id, data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await application_service.delete_application(
        db, current_user.id, app_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )


@router.post("/{app_id}/rotate-secret", response_model=RotateSecretResponse)
async def rotate_secret(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await application_service.rotate_secret(db, current_user.id, app_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    _, client_secret = result
    return RotateSecretResponse(client_secret=client_secret)
