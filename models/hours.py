from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, time
from pydantic import BaseModel, Field

class HoursBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Address ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )

    mon_start: Optional[time] = Field(None, description="Monday opening time", json_schema_extra={"example": "09:00"})
    mon_end: Optional[time] = Field(None, description="Monday closing time", json_schema_extra={"example": "18:00"})

    tue_start: Optional[time] = Field(None, description="Tuesday opening time", json_schema_extra={"example": "09:00"})
    tue_end: Optional[time] = Field(None, description="Tuesday closing time", json_schema_extra={"example": "18:00"})

    wed_start: Optional[time] = Field(None, description="Wednesday opening time", json_schema_extra={"example": "09:00"})
    wed_end: Optional[time] = Field(None, description="Wednesday closing time", json_schema_extra={"example": "18:00"})

    thu_start: Optional[time] = Field(None, description="Thursday opening time", json_schema_extra={"example": "09:00"})
    thu_end: Optional[time] = Field(None, description="Thursday closing time", json_schema_extra={"example": "18:00"})

    fri_start: Optional[time] = Field(None, description="Friday opening time", json_schema_extra={"example": "09:00"})
    fri_end: Optional[time] = Field(None, description="Friday closing time", json_schema_extra={"example": "18:00"})

    sat_start: Optional[time] = Field(None, description="Saturday opening time", json_schema_extra={"example": "09:00"})
    sat_end: Optional[time] = Field(None, description="Saturday closing time", json_schema_extra={"example": "16:00"})

    sun_start: Optional[time] = Field(None, description="Sunday opening time", json_schema_extra={"example": None})
    sun_end: Optional[time] = Field(None, description="Sunday closing time", json_schema_extra={"example": None})


class HoursCreate(HoursBase):
    """Creation payload; ID is generated server-side but present in the base model."""
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
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
    }


class HoursUpdate(BaseModel):
    """Partial update; address ID is taken from the path, not the body."""
    mon_start: Optional[time] = Field(None, description="Monday opening time", json_schema_extra={"example": "09:00"})
    mon_end: Optional[time] = Field(None, description="Monday closing time", json_schema_extra={"example": "18:00"})

    tue_start: Optional[time] = Field(None, description="Tuesday opening time", json_schema_extra={"example": "09:00"})
    tue_end: Optional[time] = Field(None, description="Tuesday closing time", json_schema_extra={"example": "18:00"})

    wed_start: Optional[time] = Field(None, description="Wednesday opening time", json_schema_extra={"example": "09:00"})
    wed_end: Optional[time] = Field(None, description="Wednesday closing time", json_schema_extra={"example": "18:00"})

    thu_start: Optional[time] = Field(None, description="Thursday opening time", json_schema_extra={"example": "09:00"})
    thu_end: Optional[time] = Field(None, description="Thursday closing time", json_schema_extra={"example": "18:00"})

    fri_start: Optional[time] = Field(None, description="Friday opening time", json_schema_extra={"example": "09:00"})
    fri_end: Optional[time] = Field(None, description="Friday closing time", json_schema_extra={"example": "18:00"})

    sat_start: Optional[time] = Field(None, description="Saturday opening time", json_schema_extra={"example": "09:00"})
    sat_end: Optional[time] = Field(None, description="Saturday closing time", json_schema_extra={"example": "16:00"})

    sun_start: Optional[time] = Field(None, description="Sunday opening time", json_schema_extra={"example": None})
    sun_end: Optional[time] = Field(None, description="Sunday closing time", json_schema_extra={"example": None})

    model_config = {
        "json_schema_extra": {
            "example":{
                "mon_start": "10:00",
            },
        }
    }