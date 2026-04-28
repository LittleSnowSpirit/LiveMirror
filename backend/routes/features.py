"""Feature discovery API."""

from fastapi import APIRouter, Depends

from features import feature_payload
from routes.core_auth import get_current_user


router = APIRouter(
    prefix="/api/features",
    tags=["features"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_features():
    return feature_payload()
