from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class Neighborhood(str, Enum):
    FINANCIAL_DISTRICT = "Financial District (FiDi)"
    TRIBECA = "Tribeca"
    SOHO = "SoHo"
    CHINATOWN = "Chinatown"
    LOWER_EAST_SIDE = "Lower East Side"
    GREENWICH_VILLAGE = "West Village"
    EAST_VILLAGE = "East Village"
    CHELSEA = "Chelsea"
    FLATIRON_DISTRICT = "Flatiron District"
    MIDTOWN = "Midtown"
    UPPER_WEST_SIDE = "Upper West Side"
    UPPER_EAST_SIDE = "Upper East Side"
    HARLEM = "Harlem"
    WASHINGTON_HEIGHTS = "Washington Heights"
    INWOOD = "Inwood"

class AddressBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Address ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    street: str = Field(
        ...,
        description="Street address and number.",
        json_schema_extra={"example": "116th and Broadway"},
    )
    city: str = Field(
        default="New York",
        description="City (fixed).",
        json_schema_extra={"example": "New York"},
    )
    state: str = Field(
        default="NY",
        description="State (fixed).",
        json_schema_extra={"example": "NY"},
    )
    postal_code: str = Field(
        ...,
        description="ZIP code.",
        json_schema_extra={"example": "10027"},
    )
    longitude: Optional[float] = Field(
        None,
        description="Optional longitude value.",
        json_schema_extra={"example": -73.962459},
    )
    latitude: Optional[float] = Field(
        None,
        description="Optional latitude value.",
        json_schema_extra={"example": 40.807415},
    )
    neighborhood: Neighborhood = Field(
        ...,
        description="Neighborhood.",
        json_schema_extra={"example": "Harlem"},
    )


    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "street": "116th and Broadway",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "longitude": -73.962459,
                "latitude": 40.807415, 
                "neighborhood": "Harlem"
            }
        }
    }


class AddressCreate(AddressBase):
    """Creation payload; ID is generated server-side but present in the base model."""
    model_config = {
        "json_schema_extra": {
            "example": {
                "street": "116th and Broadway",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "neighborhood": "Harlem"
            }
        }
    }


class AddressUpdate(BaseModel):
    """Partial update; address ID is taken from the path, not the body."""
    street: Optional[str] = Field(
        None, description="Street address and number.", json_schema_extra={"example": "116th and Broadway"}
    )
    city: Optional[str] = Field(
        None, description="City or locality.", json_schema_extra={"example": "New York"}
    )
    state: Optional[str] = Field(
        None, description="State/region code if applicable.", json_schema_extra={"example": "NY"}
    )
    postal_code: Optional[str] = Field(
        None, description="Postal or ZIP code.", json_schema_extra={"example": "10027"}
    )
    neighborhood: Optional[Neighborhood] = Field(
        None, description="Neighborhood.", json_schema_extra={"example": "Harlem"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "street": "116th and Broadway",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10027"
                },
                {"city": "New York"},
            ]
        }
    }


class AddressRead(AddressBase):
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
                "street": "116th and Broadway",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "longitude": -73.962459,
                "latitude": 40.807415, 
                "neighborhood": "Harlem",
                "created_at": "2025-01-15T10:20:30Z",
                "updated_at": "2025-01-16T12:00:00Z",
            }
        }
    }
