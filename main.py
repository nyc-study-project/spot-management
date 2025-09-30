from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health
from models.pet import PetCreate, PetRead, PetUpdate, PetReplace
from models.petshop import PetShopCreate, PetShopRead, PetShopUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
pets: Dict[UUID, PetRead] = {}
petshops: Dict[UUID, PetShopRead] = {}

app = FastAPI(
    title="Person/Address/Pet API",
    description="Demo FastAPI app using Pydantic v2 models for Person, Address, Pet, Petshop",
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

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]

# -----------------------------------------------------------------------------
# Pet endpoints
# -----------------------------------------------------------------------------
@app.post("/pets", response_model=PetRead, status_code=201)
def create_pet(pet: PetCreate):
    # Each pet gets its own UUID; stored as PetRead
    pet_read = PetRead(**pet.model_dump())
    pets[pet_read.id] = pet_read
    return pet_read

@app.get("/pets", response_model=List[PetRead])
def list_pets(
    name: Optional[str] = Query(None, description="Filter by name"),
    animal: Optional[str] = Query(None, description="Filter by animal"),
    breed: Optional[str] = Query(None, description="Filter by breed"),
):
    results = list(pets.values())

    if name is not None:
        results = [p for p in results if p.name == name]
    if animal is not None:
        results = [p for p in results if p.animal == animal]
    if breed is not None:
        results = [p for p in results if p.breed == breed]
    
    if not results: 
        raise HTTPException(status_code=404, detail="Pet not found")

    return results

@app.get("/pets/{pet_id}", response_model=PetRead)
def get_pet(pet_id: UUID):
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pets[pet_id]

@app.patch("/pets/{pet_id}", response_model=PetRead)
def update_pet(pet_id: UUID, update: PetUpdate):
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    stored = pets[pet_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    pets[pet_id] = PetRead(**stored)
    return pets[pet_id]

@app.put("/pets/{pet_id}", response_model=PetRead)
def replace_pet(pet_id: UUID, update: PetReplace):
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    pets[pet_id] = PetRead(**update.model_dump())
    return pets[pet_id]

@app.delete("/pets/{pet_id}", response_model=PetRead)
def delete_pet(pet_id: UUID):
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    deleted = pets.pop(pet_id)
    return deleted

# -----------------------------------------------------------------------------
# Petshop endpoints
# -----------------------------------------------------------------------------
@app.post("/petshops", response_model=PetShopRead, status_code=201)
def create_petshop(petshop: PetShopCreate):
    # Each petshop gets its own UUID; stored as PetShopRead
    petshop_read = PetShopRead(**petshop.model_dump())
    petshops[petshop_read.id] = petshop_read
    return petshop_read

@app.get("/petshops", response_model=List[PetShopRead])
def list_petshops(
    store_name: Optional[str] = Query(None, description="Filter by store name"),
    animal: Optional[str] = Query(None, description="Filter by animal of at least one pet"),
    city: Optional[str] = Query(None, description="Filter by city of address"),
    country: Optional[str] = Query(None, description="Filter by country of address"),
):
    results = list(petshops.values())

    if store_name is not None:
        results = [p for p in results if p.store_name == store_name]
    if city is not None:
        results = [p for p in results if p.address.city == city]
    if country is not None:
        results = [p for p in results if p.address.country == country]

    # nested pets filtering
    if animal is not None:
        results = [p for p in results if any(pet.animal == animal for pet in p.pets)]

    if not results: 
        raise HTTPException(status_code=404, detail="Petshop not found")
    return results

@app.get("/petshops/{petshop_id}", response_model=PetShopRead)
def get_petshop(petshop_id: UUID):
    if petshop_id not in petshops:
        raise HTTPException(status_code=404, detail="Petshop not found")
    return petshops[petshop_id]

@app.patch("/petshops/{petshop_id}", response_model=PetShopRead)
def update_petshop(petshop_id: UUID, update: PetShopUpdate):
    if petshop_id not in petshops:
        raise HTTPException(status_code=404, detail="Petshop not found")
    stored = petshops[petshop_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    petshops[petshop_id] = PetShopRead(**stored)
    return petshops[petshop_id]

@app.put("/petshops/{petshop_id}", response_model=PetShopRead)
def update_petshop(petshop_id: UUID, update: PetShopCreate):
    if petshop_id not in petshops:
        raise HTTPException(status_code=404, detail="Petshop not found")
    petshops[petshop_id] = PetShopRead(
        id = petshop_id, 
        store_name = update.store_name, 
        pets=update.pets, 
        address=update.address, 
        created_at=petshops[petshop_id].created_at,
        updated_at=datetime.utcnow(),     
    )
    return petshops[petshop_id]

@app.delete("/petshops/{petshop_id}", response_model=PetShopRead)
def update_petshop(petshop_id: UUID):
    if petshop_id not in petshops:
        raise HTTPException(status_code=404, detail="Petshop not found")
    deleted = petshops.pop(petshop_id)
    return deleted


# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address/Pet/Petshop API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
