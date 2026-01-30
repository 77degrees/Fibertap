from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class FamilyMemberBase(BaseModel):
    first_name: str
    middle_initial: str | None = None
    last_name: str
    emails: list[EmailStr] = []
    phone_numbers: list[str] = []
    addresses: list[str] = []
    date_of_birth: str | None = None

    @field_validator('emails')
    @classmethod
    def limit_emails(cls, v):
        if len(v) > 5:
            raise ValueError('Maximum 5 emails allowed')
        return v

    @field_validator('phone_numbers')
    @classmethod
    def limit_phones(cls, v):
        if len(v) > 5:
            raise ValueError('Maximum 5 phone numbers allowed')
        return v

    @field_validator('addresses')
    @classmethod
    def limit_addresses(cls, v):
        if len(v) > 5:
            raise ValueError('Maximum 5 addresses allowed')
        return v

    @field_validator('middle_initial')
    @classmethod
    def validate_middle_initial(cls, v):
        if v and len(v) > 2:
            raise ValueError('Middle initial should be 1-2 characters')
        return v.upper() if v else None


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    first_name: str | None = None
    middle_initial: str | None = None
    last_name: str | None = None
    emails: list[EmailStr] | None = None
    phone_numbers: list[str] | None = None
    addresses: list[str] | None = None
    date_of_birth: str | None = None

    @field_validator('emails')
    @classmethod
    def limit_emails(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 emails allowed')
        return v

    @field_validator('phone_numbers')
    @classmethod
    def limit_phones(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 phone numbers allowed')
        return v

    @field_validator('addresses')
    @classmethod
    def limit_addresses(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 addresses allowed')
        return v


class FamilyMemberResponse(BaseModel):
    id: int
    first_name: str
    middle_initial: str | None = None
    last_name: str
    name: str  # Legacy full name field
    emails: list[str] = []
    phone_numbers: list[str] = []
    addresses: list[str] = []
    date_of_birth: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
