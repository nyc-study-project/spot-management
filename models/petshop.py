from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, StringConstraints

from .address import AddressBase
from .pet import PetBase



class PetShopBase(BaseModel):
    store_name: str = Field(
        ...,
        description="Given name.",
        json_schema_extra={"example": "Pet Smart"},
    )

    pets: List[PetBase] = Field(
        default_factory=list,
        description="List of pets in pet shop (each carries a persistent Address ID).",
        json_schema_extra={
            "example":[
                {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "name": "Suki",
                    "animal": "Dog",
                    "breed": "Corgi",
                }
            ]
        }
    )

    address: AddressBase = Field(
        ...,
        description="Primary address of the pet shop (each carries a persistent Address ID).",
        json_schema_extra={
            "example":{
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "street": "123 Main St",
                "city": "London",
                "state": None,
                "postal_code": "SW1A 1AA",
                "country": "UK",
            }
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "store_name": "Pet Smart",
                    "pets":[
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "name": "Suki",
                            "animal": "Dog", 
                            "breed": "Corgi"
                        },
                    ],
                    "address":{
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "street": "123 Main St",
                        "city": "London",
                        "state": None,
                        "postal_code": "SW1A 1AA",
                        "country": "UK",
                    },
                }
            ]
        }
    }


class PetShopCreate(PetShopBase):
    """Creation payload for a PetShop."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "store_name": "Pet Fun",
                    "pets": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440002",
                            "name": "Tombo",
                            "animal": "Dog", 
                            "breed": "Husky"
                        }, 
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440003",
                            "name": "Pochi",
                            "animal": "Dog", 
                            "breed": "Shiba"
                        }
                    ],
                    "address":{
                        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                        "street": "1701 E St NW",
                        "city": "Washington",
                        "state": "DC",
                        "postal_code": "20552",
                        "country": "USA",
                    },
                }
            ]
        }
    }


class PetShopUpdate(BaseModel):
    """Partial update for a Pet Shop; supply only fields to change."""
    store_name: Optional[str] = Field(None, json_schema_extra={"example": "Augusta"})
    pets: Optional[List[PetBase]] = Field(
        None,
        description="Replace the entire set of pets with this list.",
        json_schema_extra={
            "example": [
                {
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbba",
                    "name": "Power",
                    "animal": "Dog", 
                    "breed": "Golden Retriever"
                }
            ]
        },
    ),
    address: Optional[AddressBase] = Field(
        None,
        description="Replace the address with the given address.",
        json_schema_extra={
            "example":{
                "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                "street": "10 Downing St",
                "city": "London",
                "state": None,
                "postal_code": "SW1A 2AA",
                "country": "UK",
            }
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "address":{
                        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                        "street": "10 Downing St",
                        "city": "London",
                        "state": None,
                        "postal_code": "SW1A 2AA",
                        "country": "UK",
                    }
                },
            ]
        }
    }


class PetShopRead(PetShopBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Person ID.",
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
                    "store_name": "Lovely Pets",
                    "pets": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "name": "Rover",
                            "animal": "Dog", 
                            "breed": "Bull Dog"
                        }, 
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "name": "Luce",
                            "animal": "Cat", 
                            "breed": "Tabby"
                        }
                    ],
                    "address":{
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "street": "123 Main St",
                        "city": "London",
                        "state": None,
                        "postal_code": "SW1A 1AA",
                        "country": "UK",
                    },
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
