from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family_member import FamilyMember
from app.schemas.family_member import (
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
)

router = APIRouter()


@router.get("/", response_model=list[FamilyMemberResponse])
async def list_family_members(db: AsyncSession = Depends(get_db)):
    """List all family members being monitored."""
    result = await db.execute(select(FamilyMember).order_by(FamilyMember.name))
    return result.scalars().all()


@router.post("/", response_model=FamilyMemberResponse, status_code=201)
async def create_family_member(
    member: FamilyMemberCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new family member to monitor."""
    db_member = FamilyMember(**member.model_dump())
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)
    return db_member


@router.get("/{member_id}", response_model=FamilyMemberResponse)
async def get_family_member(member_id: int, db: AsyncSession = Depends(get_db)):
    """Get details for a specific family member."""
    result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    return member


@router.put("/{member_id}", response_model=FamilyMemberResponse)
async def update_family_member(
    member_id: int,
    member_update: FamilyMemberUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a family member's information."""
    result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")

    update_data = member_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
async def delete_family_member(member_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a family member from monitoring."""
    result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")

    await db.delete(member)
    await db.commit()
