from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, StringConstraints, constr
import re

from .address import AddressBase
from .amenities import AmenitiesBase



class StudySpotBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Study Spot ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    name: str = Field(
        ...,
        description="Name of the study spot",
        json_schema_extra={"example": "Joe Coffee Company: Northwest Corner"},
    )
    reviews: Optional[str] = Field(
        None,
        description="Review of study spot.",
        json_schema_extra={"example": "Cute cafe with floor to ceiling windows. Allows open discussion."},
    )
    rating: int = Field(
        ...,
        ge=1, 
        le=5,
        description="Number of stars, 1 to 5.",
        json_schema_extra={"example": 5},
    )
    hours: constr(regex=r"^\d{2}:\d{2}-\d{2}:\d{2}$") = Field(
        ...,
        description="Operating hours in HH:MM-HH:MM format.",
        json_schema_extra={"example": "07:00-19:00"},
    )

    # Embed address (each with persistent ID)
    address: AddressBase = Field(
        description="Address linked to this study spot (carries a persistent Address ID).",
        json_schema_extra={
            "example":{
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "street": "550 W 120th St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "country": "USA",
            }
        },
    )
    
    # Embed amenities (each with persistent ID)
    amenity: AmenitiesBase = Field(
        description="Amenities linked to this study spot (carries a persistent Amenities ID).",
        json_schema_extra={
            "example":{
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "wifi": "eduoram",
                "outlets": False,
                "seating": 50,
                "refreshments":"pastries, coffee, soda"
            }
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Joe Coffee Company: Northwest Corner",
                    "reviews": "Cute cafe with floor to ceiling windows. Allows open discussion.",
                    "rating": 5,
                    "hours": "07:00-19:00",
                    "address": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "street": "550 W 120th St",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10027",
                        "country": "USA",
                    },
                    "amenity": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "wifi": "eduoram",
                        "outlets": False,
                        "seating": 50,
                        "refreshments":"pastries, coffee, soda"
                    }
                }
            ]
        }
    }


class StudySpotBase(StudySpotBase):
    """Creation payload for a Study Spot."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "770e8400-e29b-41d4-a716-446655441234",
                    "name": "Hungarian Pastry Shop",
                    "reviews": "Charming cafe with authentic Hungarian pastries. Great for coffee and studying.",
                    "rating": 5,
                    "hours": "07:30-20:30",
                    "address": {
                        "id": "770e8400-e29b-41d4-a716-446655441234",
                        "street": "1030 Amsterdam Ave",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10025",
                        "country": "USA",
                    },
                    "amenity": {
                        "id": "770e8400-e29b-41d4-a716-446655441234",
                        "outlets": False,
                        "seating": 30,
                        "refreshments": "coffee, tea, pastries"
                    }
                }
            ]
        }
    }


class StudySpotUpdate(BaseModel):
    """Partial update for a StudySpot; supply only fields to change."""
    name: Optional[str] = Field(None, json_schema_extra={"example": "Hungarian Pastry Shop"})
    reviews: Optional[str] = Field(None, json_schema_extra={"example": "Cozy cafe with authentic pastries."})
    rating: Optional[int] = Field(None, ge=1, le=5, json_schema_extra={"example": 5})
    hours: Optional[constr(regex=r"^\d{2}:\d{2}-\d{2}:\d{2}$")] = Field(None, json_schema_extra={"example": "08:00-18:00"})
    address: Optional[AddressBase] = Field(
        None,
        description="Update the address linked to this study spot.",
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655441234",
                "street": "1030 Amsterdam Ave",
                "city": "New York",
                "state": "NY",
                "postal_code": "10025",
                "country": "USA",
            }
        },
    )
    amenity: Optional[AmenitiesBase] = Field(
        None,
        description="Update the amenities linked to this study spot.",
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655441234",
                "wifi": "GuestWifi",
                "outlets": True,
                "seating": 30,
                "refreshments": "coffee, tea, pastries, strudel",
            }
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Hungarian Pastry Shop"},
                {"reviews": "Cozy cafe with authentic pastries."},
                {"rating": 5, "hours": "08:00-18:00"},
                {
                    "address": {
                        "id": "770e8400-e29b-41d4-a716-446655441234",
                        "street": "1030 Amsterdam Ave",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10025",
                        "country": "USA",
                    }
                },
                {
                    "amenity": {
                        "id": "770e8400-e29b-41d4-a716-446655441234",
                        "wifi": "GuestWifi",
                        "outlets": True,
                        "seating": 30,
                        "refreshments": "coffee, tea, pastries, strudel",
                    }
                },
            ]
        }
    }


class StudySpotRead(StudySpotBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Study Spot ID.",
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

    class StudySpotRead(StudySpotBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Study Spot ID.",
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
                    "name": "Hungarian Pastry Shop",
                    "reviews": "Cozy cafe with authentic pastries. Great for coffee and studying.",
                    "rating": 5,
                    "hours": "08:00-18:00",
                    "address": {
                        "id": "770e8400-e29b-41d4-a716-446655441234",
                        "street": "1030 Amsterdam Ave",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10025",
                        "country": "USA",
                    },
                    "amenity": {
                        "id": "770e8400-e29b-41d4-a716-446655441234",
                        "wifi": "GuestWifi",
                        "outlets": True,
                        "seating": 30,
                        "refreshments": "coffee, tea, pastries, strudel",
                    },
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
