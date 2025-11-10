from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, PositiveInt
from enum import Enum

class Seating(Enum):
    ONE_TO_FIVE = "1-5"
    SIX_TO_TEN = "6-10"
    ELEVEN_TO_TWENTY = "11-20"
    TWENTY_PLUS = "20+"

class Environment(Enum): 
    QUIET = "quiet"
    LIVELY = "lively"
    OUTDOOR = "outdoor"
    INDOOR = "indoor"

class AmenitiesBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Amenities ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    wifi_available: bool = Field(
        ...,
        description="WiFi availability.",
        json_schema_extra={"example": True},
    )
    wifi_network: Optional[str] = Field(
        None,
        description="WiFi name, optional entry.",
        json_schema_extra={"example": "eduoram"},
    )
    outlets: bool = Field(
        ...,
        description="Outlet availability.",
        json_schema_extra={"example": True},
    )
    seating: Seating = Field(
        ...,
        description="Seating capacity.",
        json_schema_extra={"example": "1-5"},
    )
    refreshments: Optional[str] = Field(
        None,
        description="Food and/or drinks served, optional entry. Comma separated values.",
        json_schema_extra={"example": "pastries, fruits, soda"},
    )
    environment: Optional[list[Environment]] = Field(
        None,
        description="Environment of the study space, optional entry.",
        json_schema_extra={"example": ["lively", "indoor"]},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "wifi_available": True,
                "wifi_network": "eduoram",
                "outlets": True,
                "seating": "1-5",
                "refreshments":"pastries, fruits, soda",
                "environment": ["lively", "indoor"]
            }
        }
    }


class AmenitiesCreate(AmenitiesBase):
    """Creation payload; ID is generated server-side but present in the base model."""
    model_config = {
        "json_schema_extra": {
            "example": {
                "wifi_available": True,
                "wifi_network": "eduoram",
                "outlets": True,
                "seating": "1-5",
                "refreshments":"pastries, fruits, soda",
                "environment": ["lively", "indoor"]
            }
        }
    }


class AmenitiesUpdate(BaseModel):
    """Partial update; address ID is taken from the path, not the body."""
    wifi_available: Optional[bool] = Field(
        None, description="WiFi availability, optional entry.", json_schema_extra={"example": True}
    )
    wifi_network: Optional[str] = Field(
        None, description="WiFi name, optional entry.", json_schema_extra={"example": "NYPL Guest"}
    )
    outlets: Optional[bool] = Field(
        None, description="Outlet availability.", json_schema_extra={"example": True}
    )
    seating: Optional[Seating] = Field(
        None, description="Seating capacity.", json_schema_extra={"example": "20+"}
    )
    refreshments: Optional[str] = Field(
        None, description="Food and/or drinks served, optional entry. Comma separated values.", json_schema_extra={"example": "water"}
    )
    environment: Optional[list[Environment]] = Field(
        None, description="Environment of the study space.", json_schema_extra={"example": ["indoor", "quiet"]}
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "wifi_network": "NYPL Guest",
                "outlets": True,
                "refreshments": "water",
            }
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
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "wifi_available": True,
                "wifi_network": "eduoram",
                "outlets": True,
                "seating": "1-5",
                "refreshments":"pastries, fruits, soda",
                "environment": ["lively", "indoor"],
                "created_at": "2025-01-15T10:20:30Z",
                "updated_at": "2025-01-16T12:00:00Z",
            }
        }
    }
