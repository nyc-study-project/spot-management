from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID
from pydantic import PositiveInt 

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.studyspot import StudySpotCreate, StudySpotRead, StudySpotUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.amenities import AmenitiesCreate, AmenitiesRead, AmenitiesUpdate
from models.health import Health

port = int(os.environ.get("FASTAPIPORT", 8000))

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

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

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

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

@app.delete("/addresses/{address_id}", response_model=AddressRead)
def delete_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    deleted = addresses.pop(address_id)
    return deleted


# -----------------------------------------------------------------------------
# Amenities endpoints
# -----------------------------------------------------------------------------

@app.post("/amenities", response_model=AmenitiesRead, status_code=201)
def create_amenities(amenity: AmenitiesCreate):
    if amenity.id in amenities:
        raise HTTPException(status_code=400, detail="Amenity with this ID already exists")
    amenities[amenity.id] = AmenitiesRead(**amenity.model_dump())
    return amenities[amenity.id]

@app.get("/amenities", response_model=List[AmenitiesRead])
def list_amenities(
    wifi: Optional[str] = Query(None, description="Filter by wifi"),
    outlets: Optional[bool] = Query(None, description="Filter by outlets"),
    seating: Optional[PositiveInt] = Query(None, description="Filter by number of seating"),
    refreshments: Optional[str] = Query(None, description="Filter by refreshments"),
):
    results = list(amenities.values())

    if wifi is not None:
        results = [a for a in results if a.wifi == wifi]
    if outlets is not None:
        results = [a for a in results if a.outlets == outlets]
    if seating is not None:
        results = [a for a in results if a.seating == seating]
    if refreshments is not None:
        results = [a for a in results if a.refreshments and refreshments.lower() in a.refreshments.lower()]

    return results

@app.get("/amenities/{amenities_id}", response_model=AmenitiesRead)
def get_amenities(amenities_id: UUID):
    if amenities_id not in amenities:
        raise HTTPException(status_code=404, detail="Amenities not found")
    return amenities[amenities_id]

@app.patch("/amenities/{amenities_id}", response_model=AmenitiesRead)
def update_amenities(amenities_id: UUID, update: AmenitiesUpdate):
    if amenities_id not in amenities:
        raise HTTPException(status_code=404, detail="Amenities not found")
    stored = amenities[amenities_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    amenities[amenities_id] = AmenitiesRead(**stored)
    return amenities[amenities_id]

@app.delete("/amenities/{amenities_id}", response_model=AmenitiesRead)
def delete_amenities(amenities_id: UUID):
    if amenities_id not in amenities:
        raise HTTPException(status_code=404, detail="Amenities not found")
    deleted = amenities.pop(amenities_id)
    return deleted

# -----------------------------------------------------------------------------
# StudySpots endpoints
# -----------------------------------------------------------------------------

@app.post("/studyspots", response_model=StudySpotRead, status_code=201)
def create_studyspot(studyspot: StudySpotCreate):
    if studyspot.id in studyspots:
        raise HTTPException(status_code=400, detail="Studyspot with this ID already exists")
    studyspots[studyspot.id] = StudySpotRead(**studyspot.model_dump())
    return studyspots[studyspot.id]

@app.get("/studyspots", response_model=List[StudySpotRead])
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

@app.get("/studyspots/{studyspot_id}", response_model=StudySpotRead)
def get_studyspot(studyspot_id: UUID):
    if studyspot_id not in studyspots:
        raise HTTPException(status_code=404, detail="Study Spot not found")
    return studyspots[studyspot_id]

@app.patch("/studyspots/{studyspot_id}", response_model=StudySpotRead)
def update_studyspot(studyspot_id: UUID, update: StudySpotUpdate):
    if studyspot_id not in studyspots:
        raise HTTPException(status_code=404, detail="Study Spot not found")
    stored = studyspots[studyspot_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    studyspots[studyspot_id] = StudySpotRead(**stored)
    return studyspots[studyspot_id]

@app.delete("/studyspots/{studyspot_id}", response_model=StudySpotRead)
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
