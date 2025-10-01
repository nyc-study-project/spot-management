from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, PositiveInt


class AmenitiesBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Amenities ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    wifi: Optional[str] = Field(
        None,
        description="WiFi name, optional entry.",
        json_schema_extra={"example": "eduoram"},
    )
    outlets: bool = Field(
        ...,
        description="Outlet availability.",
        json_schema_extra={"example": True},
    )
    seating: PositiveInt = Field(
        ...,
        description="Seating capacity.",
        json_schema_extra={"example": 50},
    )
    refreshments: Optional[str] = Field(
        None,
        description="Food and/or drinks served, optional entry. Comma separated values.",
        json_schema_extra={"example": "pastries, fruits, soda"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "wifi": "eduoram",
                    "outlets": True,
                    "seating": 50,
                    "refreshments":"pastries, fruits, soda"
                }
            ]
        }
    }


class AmenitiesCreate(AmenitiesBase):
    """Creation payload; ID is generated server-side but present in the base model."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "11111111-1111-4111-8111-111111111111",
                    "wifi": "Columbia University",
                    "outlets": True,
                    "seating": 30,
                    "refreshments": "coffee, pastries"
                }
            ]
        }
    }


class AmenitiesUpdate(BaseModel):
    """Partial update; address ID is taken from the path, not the body."""
    wifi: Optional[str] = Field(
        None, description="WiFi name, optional entry.", json_schema_extra={"example": "NYPL Guest"}
    )
    outlets: Optional[bool] = Field(
        None, description="Outlet availability.", json_schema_extra={"example": True}
    )
    seating: Optional[PositiveInt] = Field(
        None, description="Seating capacity.", json_schema_extra={"example": 120}
    )
    refreshments: Optional[str] = Field(
        None, description="Food and/or drinks served, optional entry. Comma separated values.", json_schema_extra={"example": "water"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "wifi": "NYPL Guest",
                "outlets": True,
                "seating": 120,
                "refreshments": "water",
                }
            ]
        }
    }


class AmenitiesRead(AmenitiesBase):
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
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "wifi": "eduoram",
                    "outlets": True,
                    "seating": 20,
                    "refreshments": "soda",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
