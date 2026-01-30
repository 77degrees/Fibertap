from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.family_member import FamilyMemberCreate, FamilyMemberResponse

router = APIRouter()


@router.get("/", response_model=list[FamilyMemberResponse])
async def list_family_members(db: AsyncSession = Depends(get_db)):
    """List all family members being monitored."""
    # TODO: Implement
    return []


@router.post("/", response_model=FamilyMemberResponse)
async def create_family_member(
    member: FamilyMemberCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new family member to monitor."""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{member_id}", response_model=FamilyMemberResponse)
async def get_family_member(member_id: int, db: AsyncSession = Depends(get_db)):
    """Get details for a specific family member."""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{member_id}")
async def delete_family_member(member_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a family member from monitoring."""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")
