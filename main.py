from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import PositiveInt 
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Table, MetaData, select, insert, update, delete
from sqlalchemy.orm import sessionmaker

from models.studyspot import StudySpotCreate, StudySpotRead, StudySpotUpdate
from models.address import AddressRead
from models.amenities import AmenitiesRead
from models.health import Health

port = int(os.environ.get("FASTAPIPORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set!")

# SQLAlchemy setup for MySQL
engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()



# Spot management: study spot listings with location, amenities (WiFi, outlets, seating), and hours.
# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
studyspots: Dict[UUID, StudySpotRead] = {}
addresses: Dict[UUID, AddressRead] = {}
amenities: Dict[UUID, AmenitiesRead] = {}

app = FastAPI(
    title="StudySpot API",
    description="Demo FastAPI app using Pydantic v2 models for Study Spot",
    version="0.1.0",
)


def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

# -----------------------------------------------------------------------------
# StudySpots endpoints
# -----------------------------------------------------------------------------

@app.post("/study-spots", response_model=StudySpotRead, status_code=201)
def create_studyspot(studyspot: StudySpotCreate):
    if studyspot.id in studyspots:
        raise HTTPException(status_code=400, detail="Studyspot with this ID already exists")
    studyspots[studyspot.id] = StudySpotRead(**studyspot.model_dump())
    return studyspots[studyspot.id]

@app.get("/study-spots", response_model=List[StudySpotRead])
def list_studyspots(
    name: Optional[str] = Query(None, description="Filter by name"),
    wifi: Optional[str] = Query(None, description="Filter by wifi"),
    outlets: Optional[bool] = Query(None, description="Filter by outlets"),
    seating: Optional[PositiveInt] = Query(None, description="Filter by number of seating"),
    refreshments: Optional[str] = Query(None, description="Filter by refreshments"),
    city: Optional[str] = Query(None, description="Filter by city"),
):
    results = list(studyspots.values())
    if name is not None:
        results = [a for a in results if a.name == name]
    if wifi is not None:
        results = [a for a in results if a.amenity.wifi == wifi]
    if outlets is not None:
        results = [a for a in results if a.amenity.outlets == outlets]
    if seating is not None:
        results = [a for a in results if a.amenity.seating == seating]
    if refreshments is not None:
        results = [a for a in results if a.amenity.refreshments and refreshments.lower() in a.amenity.refreshments.lower()]
    if city is not None:
        results = [a for a in results if a.address.city == city]
    return results

@app.get("/study-spots/{studyspot_id}", response_model=StudySpotRead)
def get_studyspot(studyspot_id: UUID):
    if studyspot_id not in studyspots:
        raise HTTPException(status_code=404, detail="Study Spot not found")
    return studyspots[studyspot_id]

@app.patch("/study-spots/{studyspot_id}", response_model=StudySpotRead)
def update_studyspot(studyspot_id: UUID, update: StudySpotUpdate):
    if studyspot_id not in studyspots:
        raise HTTPException(status_code=404, detail="Study Spot not found")
    stored = studyspots[studyspot_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    studyspots[studyspot_id] = StudySpotRead(**stored)
    return studyspots[studyspot_id]

@app.delete("/study-spots/{studyspot_id}", response_model=StudySpotRead)
def delete_studyspot(studyspot_id: UUID):
    if studyspot_id not in studyspots:
        raise HTTPException(status_code=404, detail="Study Spot not found")
    deleted = studyspots.pop(studyspot_id)
    return deleted


# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Study Spot API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
