from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, StringConstraints

from .address import AddressBase, AddressUpdate
from .amenities import AmenitiesBase, AmenitiesUpdate
from .hours import HoursBase

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

    # Embed address (each with persistent ID)
    address: AddressBase = Field(
        description="Address linked to this study spot (carries a persistent Address ID).",
        json_schema_extra={
            "example":{
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "street": "116th and Broadway",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "longitude": -73.962459,
                "latitude": 40.807415, 
                "neighborhood": "Harlem"
            }
        },
    )
    
    # Embed amenities (each with persistent ID)
    amenity: AmenitiesBase = Field(
        description="Amenities linked to this study spot (carries a persistent Amenities ID).",
        json_schema_extra={
            "example":{
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "wifi_available": True,
                "wifi_network": "eduroam",
                "outlets": True,
                "seating": "1-5",
                "refreshments":"pastries, fruits, soda",
                "environment": ["lively", "indoor"]
            }
        },
    )

    # Embed hours (each with persistent ID)
    hour: HoursBase = Field(
        description="Hours linked to this study spot.",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "mon_start": "09:00",
                "mon_end": "18:00",
                "tue_start": "09:00",
                "tue_end": "18:00",
                "wed_start": "09:00",
                "wed_end": "18:00",
                "thu_start": "09:00",
                "thu_end": "18:00",
                "fri_start": "09:00",
                "fri_end": "18:00",
                "sat_start": "09:00",
                "sat_end": "16:00",
                "sun_start": None,
                "sun_end": None
            }
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Joe Coffee Company: Northwest Corner",
                    "address": {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "street": "116th and Broadway",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10027",
                        "longitude": -73.962459,
                        "latitude": 40.807415, 
                        "neighborhood": "Harlem"
                    },
                    "amenity": {
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "wifi_available": True,
                        "wifi_network": "eduroam",
                        "outlets": True,
                        "seating": "1-5",
                        "refreshments":"pastries, fruits, soda",
                        "environment": ["lively", "indoor"]
                    },
                    "hour": {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "mon_start": "09:00",
                        "mon_end": "18:00",
                        "tue_start": "09:00",
                        "tue_end": "18:00",
                        "wed_start": "09:00",
                        "wed_end": "18:00",
                        "thu_start": "09:00",
                        "thu_end": "18:00",
                        "fri_start": "09:00",
                        "fri_end": "18:00",
                        "sat_start": "09:00",
                        "sat_end": "16:00",
                        "sun_start": None,
                        "sun_end": None
                    }
                }
            ]
        }
    }


class StudySpotCreate(StudySpotBase):
    """Creation payload for a Study Spot."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Hungarian Pastry Shop",
                    "address": {
                        "street": "1030 Amsterdam Ave",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10025",
                        "longitude": -73.963755,
                        "latitude": 40.803614, 
                        "neighborhood": "Harlem"
                    },
                    "amenity": {
                        "wifi_available": True,
                        "wifi_network": "eduroam",
                        "outlets": False,
                        "seating": "20+",
                        "refreshments":"pastries, coffee",
                        "environment": ["lively", "indoor", "outdoor"]
                    },
                    "hour": {
                        "mon_start": "09:00",
                        "mon_end": "18:00",
                        "tue_start": "09:00",
                        "tue_end": "18:00",
                        "wed_start": "09:00",
                        "wed_end": "18:00",
                        "thu_start": "09:00",
                        "thu_end": "18:00",
                        "fri_start": "09:00",
                        "fri_end": "18:00",
                        "sat_start": "09:00",
                        "sat_end": "16:00",
                        "sun_start": None,
                        "sun_end": None
                    }
                }
            ]
        }
    }


class StudySpotUpdate(BaseModel):
    """Partial update for a StudySpot; supply only fields to change."""
    name: Optional[str] = Field(None, json_schema_extra={"example": "Hungarian Pastry Shop"})
    address: Optional[AddressUpdate] = Field(
        None,
        description="Update the address linked to this study spot.",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "street": "116th and Broadway",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "longitude": -73.962459,
                "latitude": 40.807415, 
                "neighborhood": "Harlem"
            }
        },
    )
    amenity: Optional[AmenitiesUpdate] = Field(
        None,
        description="Update the amenities linked to this study spot.",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "wifi_available": True,
                "wifi_network": "eduroam",
                "outlets": True,
                "seating": "1-5",
                "refreshments":"pastries, fruits, soda",
                "environment": ["lively", "indoor"]
            }
        },
    )
    hour: Optional[HoursBase] = Field(
        None,
        description="Update the hours linked to this study spot.",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "mon_start": "09:00",
                "mon_end": "18:00",
                "tue_start": "09:00",
                "tue_end": "18:00",
                "wed_start": "09:00",
                "wed_end": "18:00",
                "thu_start": "09:00",
                "thu_end": "18:00",
                "fri_start": "09:00",
                "fri_end": "18:00",
                "sat_start": "09:00",
                "sat_end": "16:00",
                "sun_start": None,
                "sun_end": None
            }
        }
    )


class StudySpotRead(StudySpotBase):
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
                    "address": {
                        "id": "770e8400-e29b-41d4-a716-446655441235",
                        "street": "1030 Amsterdam Ave",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10025",
                        "longitude": -73.963755,
                        "latitude": 40.803614, 
                        "neighborhood": "Harlem"
                    },
                    "amenity": {
                        "id": "770e8400-e29b-41d4-a716-446655441236",
                        "wifi_available": True,
                        "wifi_network": "eduroam",
                        "outlets": False,
                        "seating": "20+",
                        "refreshments":"pastries, coffee",
                        "environment": ["lively", "indoor", "outdoor"]
                    },
                    "hour": {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "mon_start": "09:00",
                        "mon_end": "18:00",
                        "tue_start": "09:00",
                        "tue_end": "18:00",
                        "wed_start": "09:00",
                        "wed_end": "18:00",
                        "thu_start": "09:00",
                        "thu_end": "18:00",
                        "fri_start": "09:00",
                        "fri_end": "18:00",
                        "sat_start": "09:00",
                        "sat_end": "16:00",
                        "sun_start": None,
                        "sun_end": None
                    },
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }

class StudySpotResponse(BaseModel):
    data: StudySpotRead
    links: dict