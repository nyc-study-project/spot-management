from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, StringConstraints


class PetBase(BaseModel):
    name: str = Field(
        ...,
        description="Given name.",
        json_schema_extra={"example": "Suki"},
    )
    animal: str = Field(
        ...,
        description="Type of animal.",
        json_schema_extra={"example": "Dog"},
    )
    breed: str = Field(
        ...,
        description="Type of given animal.",
        json_schema_extra={"example": "Corgi"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Suki",
                    "animal": "Dog",
                    "breed": "Corgi",
                }
            ]
        }
    }


class PetCreate(PetBase):
    """Creation payload for a Pet."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Lucy",
                    "animal": "Cat",
                    "breed": "Ragdoll",
                }
            ]
        }
    }


class PetUpdate(BaseModel):
    """Partial update for a Pet; supply only fields to change."""
    name: Optional[str] = Field(None, json_schema_extra={"example": "Augusta"})
    animal: Optional[str] = Field(None, json_schema_extra={"example": "Turtle"})
    breed: Optional[str] = Field(None, json_schema_extra={"example": "Snapping"})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Ada", "breed": "Husky"},
            ]
        }
    }

class PetReplace(BaseModel):
    """Complete update for a Pet."""
    name: str = Field(None, json_schema_extra={"example": "Augusta"})
    animal: str = Field(None, json_schema_extra={"example": "Turtle"})
    breed: str = Field(None, json_schema_extra={"example": "Snapping"})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Augusta", 
                 "animal": "Dog",
                 "breed": "Husky"},
            ]
        }
    }


class PetRead(PetBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Pet ID.",
        json_schema_extra={"example": "99999999-9999-4999-8999-999999999999"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "99999999-9999-4999-8999-999999999999",
                    "name": "Ada",
                    "animal": "Cat",
                    "breed": "Tabby",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
