from __future__ import annotations

import os
import math
import socket
import json
import hashlib
import requests
import httpx
import googlemaps
from datetime import datetime, time
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import RowMapping
from psycopg2.extras import Json

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks

from models.hours import HoursBase
from models.studyspot import StudySpotCreate, StudySpotRead, StudySpotResponse
from models.address import AddressRead, Neighborhood
from models.amenities import AmenitiesRead, Seating, Environment
from models.health import Health


from fastapi import Request, Response, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback

# -----------------------------------------------------------------------------
# Create DB Queries
# -----------------------------------------------------------------------------
# UUID PRIMARY KEY,
#     name TEXT NOT NULL,
#     street TEXT,                                
#     city TEXT,
#     state TEXT,
#     postal_code TEXT,
#     latitude DOUBLE PRECISION,
#     longitude DOUBLE PRECISION,
#     neighborhood TEXT,
#     wifi_available BOOLEAN,
#     wifi_network TEXT,
#     outlets BOOLEAN,
#     seating TEXT,
#     refreshments TEXT,
#     environment JSONB,
#     created_at TIMESTAMP DEFAULT NOW(),
#     updated_at TIMESTAMP DEFAULT NOW()
# );
# CREATE TABLE hours (
#     hour_id UUID PRIMARY KEY,
#     studyspot_id UUID REFERENCES studyspots(id),                                
#     mon_start TIME,
#     mon_end TIME,
#     tue_start TIME,
#     tue_end TIME,
#     wed_start TIME,
#     wed_end TIME,
#     thu_start TIME,
#     thu_end TIME,
#     fri_start TIME,
#     fri_end TIME,
#     sat_start TIME,
#     sat_end TIME,
#     sun_start TIME,
#     sun_end TIME
# );

# -----------------------------------------------------------------------------
# Cloud Run Connection
# -----------------------------------------------------------------------------

def get_connection():
    try:
        env = os.environ.get("ENV", "local")

        if env == "local":
            user = "erikoy"
            password = "columbia25"
            host = "127.0.0.1"
            port = 5432
            database = "spot_db"

            connection_str = (f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
        else:
            user=os.environ["DB_USER"]
            password=os.environ["DB_PASS"]
            database=os.environ["DB_NAME"]
            unix_socket=f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}"

            connection_str = (
                f"postgresql+psycopg2://{user}:{password}@/{database}"
                f"?host={unix_socket}"
            )
        engine = create_engine(connection_str, pool_pre_ping=True)
        Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        return Session

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

Session = get_connection()

# -----------------------------------------------------------------------------
# Database Connection
# -----------------------------------------------------------------------------
def execute_query(queries: List[Tuple[str, dict]], fetchone=False):
    try: 
        with Session() as session, session.begin():
            results = []
            for query, params in queries:
                result = session.execute(text(query), params or {})

                if query.strip().upper().startswith("SELECT"):
                    rows = result.mappings().fetchone() if fetchone else result.mappings().all()

                    if not rows: 
                        id = params.get("id")
                        raise HTTPException(status_code=404, detail=f"Study spot {id} not found.")
                    results = rows
                else:
                    results.append(result.rowcount)
            return results[0] if len(results)==1 else results

    except HTTPException: 
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")

    
# -----------------------------------------------------------------------------
# FastAPI Setup
# -----------------------------------------------------------------------------
port = int(os.environ.get("PORT", 8000))
app = FastAPI(title="StudySpot API", description="Study Spot API", version="0.1.0")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Logs the body that caused a 422 validation error, without altering response format.
    """
    try:
        body = await request.json()
    except Exception:
        body = "<unreadable body>"

    print("\n🚨 422 Validation Error at:", request.url)
    print("Raw body received:\n", json.dumps(body, indent=2))
    print("Validation errors:\n", exc.errors())
    print("Traceback:\n", traceback.format_exc())

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": body,  # include raw body in response to debug shape
        },
    )


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
def make_health(echo: Optional[str], path_echo: Optional[str] = None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo,
    )


@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None)):
    return make_health(echo=echo)


@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(path_echo: str, echo: str | None = Query(None)):
    return make_health(echo=echo, path_echo=path_echo)

# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------
def generate_etag(data):
    # should be different for each call
    return hashlib.md5(data.encode('utf-8')).hexdigest()

class DayOfWeek(str, Enum):
    mon = "mon"
    tue = "tue"
    wed = "wed"
    thu = "thu"
    fri = "fri"
    sat = "sat"
    sun = "sun"

def build_url(page_number, page_size, request):
    query_params = dict(request.query_params)
    query_params["page"] = page_number
    query_params["page_size"] = page_size
    query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
    return f"{request.url.path}?{query_string}"
# -----------------------------------------------------------------------------
# StudySpots
# -----------------------------------------------------------------------------
@app.post("/studyspots", response_model=StudySpotResponse, status_code=201)
async def create_studyspot(studyspot: StudySpotCreate, request: Request, response: Response):
    spot_id = str(uuid4())

    try:
        queries = [
            (
                """
                INSERT INTO studyspots(
                    id, name, street, city, state, postal_code, latitude, longitude, neighborhood, 
                    wifi_available, wifi_network, outlets, seating, refreshments, environment, created_at, updated_at
                ) 
                VALUES (
                    :id, :name, :street, :city, :state, :postal_code, :latitude, :longitude, :neighborhood, 
                    :wifi_available, :wifi_network, :outlets, :seating, :refreshments, :environment, NOW(), NOW()
                )
                """, 
                {
                    "id": spot_id, 
                    "name": studyspot.name, 
                    "street": studyspot.address.street, 
                    "city": studyspot.address.city, 
                    "state": studyspot.address.state, 
                    "postal_code": studyspot.address.postal_code, 
                    "latitude": getattr(studyspot.address, "latitude", None),
                    "longitude": getattr(studyspot.address, "longitude", None),
                    "neighborhood": (
                        studyspot.address.neighborhood.value 
                        if isinstance(studyspot.address.neighborhood, Enum)
                        else studyspot.address.neighborhood
                    ),
                    "wifi_available": studyspot.amenity.wifi_available,
                    "wifi_network": getattr(studyspot.amenity, "wifi_network", None),
                    "outlets": studyspot.amenity.outlets,
                    "seating": (
                        studyspot.amenity.seating.value 
                        if isinstance(studyspot.amenity.seating, Enum)
                        else studyspot.amenity.seating
                    ),
                    "refreshments": getattr(studyspot.amenity, "refreshments", None),
                    "environment": Json([
                        env.value if isinstance(env, Enum) else env
                        for env in (studyspot.amenity.environment or [])
                    ]),
                }
            ),
            (
                """
                INSERT INTO hours(
                    hour_id, studyspot_id, mon_start, mon_end, tue_start, tue_end,
                    wed_start, wed_end, thu_start, thu_end, fri_start, fri_end,
                    sat_start, sat_end, sun_start, sun_end
                ) 
                VALUES (
                    :hour_id, :studyspot_id, :mon_start, :mon_end, :tue_start, :tue_end,
                    :wed_start, :wed_end, :thu_start, :thu_end, :fri_start, :fri_end,
                    :sat_start, :sat_end, :sun_start, :sun_end
                )
                """, 
                {
                    "hour_id": str(uuid4()), 
                    "studyspot_id": spot_id,
                    "mon_start": getattr(studyspot.hour, "mon_start", None),
                    "mon_end": getattr(studyspot.hour, "mon_end", None),
                    "tue_start": getattr(studyspot.hour, "tue_start", None),
                    "tue_end": getattr(studyspot.hour, "tue_end", None),
                    "wed_start": getattr(studyspot.hour, "wed_start", None),
                    "wed_end": getattr(studyspot.hour, "wed_end", None),
                    "thu_start": getattr(studyspot.hour, "thu_start", None),
                    "thu_end": getattr(studyspot.hour, "thu_end", None),
                    "fri_start": getattr(studyspot.hour, "fri_start", None),
                    "fri_end": getattr(studyspot.hour, "fri_end", None),
                    "sat_start": getattr(studyspot.hour, "sat_start", None),
                    "sat_end": getattr(studyspot.hour, "sat_end", None),
                    "sun_start": getattr(studyspot.hour, "sun_start", None),
                    "sun_end": getattr(studyspot.hour, "sun_end", None),
                }
            ),
            (
                """
                SELECT *
                FROM studyspots s
                JOIN hours h ON s.id = h.studyspot_id
                WHERE s.id = :id
                """, 
                {"id": spot_id}
            )
        ]

        spot = execute_query(queries, fetchone=True)  
        if not spot:
            raise HTTPException(status_code=500, detail="Failed to create new study spot.")

        response.headers["Location"] = f"/studyspots/{spot_id}"
        result =  StudySpotRead(
            id=spot["id"],
            name=spot["name"],
            address=AddressRead(
                street=spot["street"],
                city=spot["city"],
                state=spot["state"],
                postal_code=spot["postal_code"],
                latitude=spot.get("latitude"),
                longitude=spot.get("longitude"),
                neighborhood=Neighborhood(spot.get("neighborhood")),
            ),
            amenity=AmenitiesRead(
                wifi_available=bool(spot["wifi_available"]),
                wifi_network=spot.get("wifi_network"),
                outlets=bool(spot["outlets"]),
                seating=Seating(spot["seating"]),
                refreshments=spot["refreshments"],
                environment= [Environment(env) for env in spot.get("environment")],
            ),
            hour=HoursBase(
                mon_start=spot["mon_start"], mon_end=spot["mon_end"],
                tue_start=spot["tue_start"], tue_end=spot["tue_end"],
                wed_start=spot["wed_start"], wed_end=spot["wed_end"],
                thu_start=spot["thu_start"], thu_end=spot["thu_end"],
                fri_start=spot["fri_start"], fri_end=spot["fri_end"],
                sat_start=spot["sat_start"], sat_end=spot["sat_end"],
                sun_start=spot["sun_start"], sun_end=spot["sun_end"],
            ),
            created_at=spot["created_at"],
            updated_at=spot["updated_at"],
        )
        return {
            "data": result,
            "links": [
                {
                    "href": "self",
                    "rel": f"/studyspots/{spot_id}",
                    "geocode": f"/studyspots/{spot_id}/geocode",
                    "type" : "GET"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/studyspots", response_model=List[StudySpotResponse], status_code=200)
def list_studyspots(
    request: Request,
    name: Optional[str] = Query(None),
    neighborhood: Optional[Neighborhood] = Query(None),
    wifi: Optional[bool] = Query(None),
    outlets: Optional[bool] = Query(None),
    seating: Optional[Seating] = Query(None),
    refreshments: Optional[str] = Query(None),
    environment: Optional[Environment] = Query(None),
    open_day: Optional[DayOfWeek] = Query(None),
    open_now: Optional[bool] = Query(None),
    page: int=1, 
    page_size: int=10
):
    now = datetime.now()
    current_day = now.strftime("%a").lower()[:3]
    current_time = now.time()

    try:
        query = """
            SELECT * FROM studyspots s
            JOIN hours h ON s.id = h.studyspot_id
            WHERE 1=1
        """
        params = {"page_size": page_size, "offset": (page-1)*page_size}

        if name:
            query += " AND name LIKE :name"
            params["name"]=f"%{name}%"
        if neighborhood: 
            query += " AND neighborhood = :neighborhood"
            params["neighborhood"] = neighborhood.value if isinstance(neighborhood, Enum) else neighborhood
        if wifi is not None:
            query += " AND wifi_available = :wifi_available"
            params["wifi_available"]=wifi
        if outlets is not None:
            query += " AND outlets = :outlets"
            params["outlets"]=outlets
        if seating:
            query += " AND seating = :seating"
            params["seating"] = seating.value if isinstance(seating, Enum) else seating
        if refreshments:
            query += " AND refreshments LIKE :refreshments"
            params["refreshments"]=f"%{refreshments}%"
        if environment:
            query += " AND s.environment @> :environment"
            params["environment"] = Json(environment.value if isinstance(environment, Enum) else environment)
        if open_day: 
            query += f" AND h.{open_day.value}_start IS NOT NULL"
        if open_now: 
            query += f" AND h.{current_day}_start <= :current_time AND h.{current_day}_end >= :current_time"
            params["current_time"] = current_time

        base_query = query + " LIMIT :page_size OFFSET :offset"
        count_query = "SELECT COUNT(*) AS total FROM (" + query + ") AS sub"

        results = execute_query([(base_query, params)]) or []
        if isinstance(results, RowMapping):
            results = [results]        

        total_len = execute_query([(count_query, params)])["total"]
        total_pages = max(1, math.ceil(total_len / page_size))
        
        items = []
        links = []
        for spot in results:
            items.append(
                StudySpotRead(
                    id=spot["id"],
                    name=spot["name"],
                    address=AddressRead(
                        street=spot["street"],
                        city=spot["city"],
                        state=spot.get("state", "NY"),
                        postal_code=spot.get("postal_code", "00000"),
                        latitude=spot.get("latitude"),
                        longitude=spot.get("longitude"),
                        neighborhood= spot.get("neighborhood"),
                    ),
                    amenity=AmenitiesRead(
                        wifi_available=bool(spot["wifi_available"]),
                        wifi_network=spot.get("wifi_network"),
                        outlets=bool(spot["outlets"]),
                        seating=spot["seating"],
                        refreshments=spot["refreshments"],
                        environment = [Environment(env) for env in spot.get("environment")],
                    ),
                    hour=HoursBase(
                        mon_start=spot["mon_start"], mon_end=spot["mon_end"],
                        tue_start=spot["tue_start"], tue_end=spot["tue_end"],
                        wed_start=spot["wed_start"], wed_end=spot["wed_end"],
                        thu_start=spot["thu_start"], thu_end=spot["thu_end"],
                        fri_start=spot["fri_start"], fri_end=spot["fri_end"],
                        sat_start=spot["sat_start"], sat_end=spot["sat_end"],
                        sun_start=spot["sun_start"], sun_end=spot["sun_end"],
                    ),
                    created_at=spot["created_at"],
                    updated_at=spot["updated_at"],
                )
            )
            links.append({
                "self": f"/studyspots/{spot['id']}",
            })

        response_data = [{
            "data": item,
            "links": [
                {
                    "href": "self",
                    "rel": link["self"],
                    "type" : "GET"
                }, 
                {
                    "href": "first",
                    "rel": build_url(1, page_size, request), 
                    "type" : "GET"
                }, 
                {
                    "href": "prev",
                    "rel": build_url(page - 1, page_size, request) if page > 1 else None,
                    "type" : "GET"
                }, 
                {
                    "href": "next",
                    "rel": build_url(page + 1, page_size, request) if page < total_pages else None, 
                    "type" : "GET"
                }, 
                {
                    "href": "last",
                    "rel": build_url(total_pages, page_size, request), 
                    "type" : "GET"
                }
            ]
        } for item, link in zip(items, links)]
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/studyspots/{studyspot_id}", response_model=StudySpotResponse, status_code=200)
def get_studyspot(studyspot_id: UUID, response: Response, if_none_match: Optional[str]=Header(None)):
    try:
        queries = [
            (
                """
                SELECT *
                FROM studyspots s
                JOIN hours h ON s.id = h.studyspot_id
                WHERE s.id = :id
                """, 
                {"id": str(studyspot_id)}
            ),
        ]

        spot = execute_query(queries, fetchone=True)
        if not spot:
            raise HTTPException(status_code=404, detail=f"Study spot {studyspot_id} not found.")
        
        etag_source = f"{spot['id']}-{spot.get('updated_at') or ''}"
        etag = generate_etag(etag_source)

        if if_none_match==etag:
            return Response(status_code=304, headers={'Etag': etag})
        
        response.headers["ETag"] = etag

        result = StudySpotRead(
            id=spot["id"],
            name=spot["name"],
            address=AddressRead(
                street=spot["street"],
                city=spot["city"],
                state=spot.get("state", "NY"),
                postal_code=spot.get("postal_code", "00000"),
                latitude=spot.get("latitude"),
                longitude=spot.get("longitude"),
                neighborhood= spot.get("neighborhood"),
            ),
            amenity=AmenitiesRead(
                wifi_available=bool(spot["wifi_available"]),
                wifi_network=spot.get("wifi_network"),
                outlets=bool(spot["outlets"]),
                seating=spot["seating"],
                refreshments=spot["refreshments"],
                environment = [Environment(env) for env in spot.get("environment")],
            ),
            hour=HoursBase(
                mon_start=spot["mon_start"], mon_end=spot["mon_end"],
                tue_start=spot["tue_start"], tue_end=spot["tue_end"],
                wed_start=spot["wed_start"], wed_end=spot["wed_end"],
                thu_start=spot["thu_start"], thu_end=spot["thu_end"],
                fri_start=spot["fri_start"], fri_end=spot["fri_end"],
                sat_start=spot["sat_start"], sat_end=spot["sat_end"],
                sun_start=spot["sun_start"], sun_end=spot["sun_end"],
            ),
            created_at=spot["created_at"],
            updated_at=spot["updated_at"],
        )

        return {
            "data": result, 
            "links": [
                {
                    "href": "self",
                    "rel": f"/studyspots/{studyspot_id}",
                    "type" : "GET"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/studyspots/{studyspot_id}", response_model=StudySpotResponse, status_code=200)
async def update_studyspot(
    request: Request,
    studyspot_id: UUID, 
    name: Optional[str] = Query(None),
    street: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    neighborhood: Optional[Neighborhood] = Query(None),
    wifi_available: Optional[bool] = Query(None),
    wifi_network: Optional[str] = Query(None),
    outlets: Optional[bool] = Query(None),
    seating: Optional[Seating] = Query(None),
    refreshments: Optional[str] = Query(None),
    environment: Optional[List[Environment]] = Query(None),
    mon_start: Optional[time] = Query(None),
    mon_end: Optional[time] = Query(None),
    tue_start: Optional[time] = Query(None),
    tue_end: Optional[time] = Query(None),
    wed_start: Optional[time] = Query(None),
    wed_end: Optional[time] = Query(None),
    thu_start: Optional[time] = Query(None),
    thu_end: Optional[time] = Query(None),
    fri_start: Optional[time] = Query(None),
    fri_end: Optional[time] = Query(None),
    sat_start: Optional[time] = Query(None),
    sat_end: Optional[time] = Query(None),
    sun_start: Optional[time] = Query(None),
    sun_end: Optional[time] = Query(None),
):
    try:
        fields_studyspots = []
        fields_hours = []
        queries = []
        params = {"id": str(studyspot_id)}

        # --- Basic info ---
        if name is not None:
            fields_studyspots.append("name = :name")
            params["name"] = name

        # --- Address (partial) ---
        if street is not None:
            fields_studyspots.append("street = :street")
            params["street"] = street

            latitude, longitude, postal_code = get_geocode(street=street)
            fields_studyspots.append("latitude = :latitude")
            params["latitude"] = latitude
            fields_studyspots.append("longitude = :longitude")
            params["longitude"] = longitude
            fields_studyspots.append("postal_code = :postal_code")
            params["postal_code"] = postal_code
            
        if city is not None:
            fields_studyspots.append("city = :city")
            params["city"] = city
        if neighborhood is not None:
            fields_studyspots.append("neighborhood = :neighborhood")
            params["neighborhood"] = neighborhood.value if hasattr(neighborhood, "value") else neighborhood

        # --- Amenity (partial, optional fields) ---
        if wifi_available is not None:
            fields_studyspots.append("wifi_available = :wifi_available")
            params["wifi_available"] = wifi_available
        if wifi_network is not None:
            fields_studyspots.append("wifi_network = :wifi_network")
            params["wifi_network"] = wifi_network
        if outlets is not None:
            fields_studyspots.append("outlets = :outlets")
            params["outlets"] = outlets
        if seating is not None:
            fields_studyspots.append("seating = :seating")
            params["seating"] = seating.value if hasattr(seating, "value") else seating
        if refreshments is not None:
            fields_studyspots.append("refreshments = :refreshments")
            params["refreshments"] = refreshments
        if environment is not None:
            fields_studyspots.append("environment = :environment")
            params["environment"] = Json([
                env.value if isinstance(env, Enum) else env
                for env in (environment or [])
            ])

        # --- Hour (partial, optional fields) ---
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            start = locals()[f"{day}_start"]
            end = locals()[f"{day}_end"]
            if start is not None:
                fields_hours.append(f"{day}_start = :{day}_start")
                params[f"{day}_start"] = start
            if end is not None:
                fields_hours.append(f"{day}_end = :{day}_end")
                params[f"{day}_end"] = end

        # --- Error if no update fields ---
        if not fields_hours and not fields_studyspots:
            raise HTTPException(status_code=400, detail="No fields to update")

        # --- Construct and execute ---
        clause_studyspots = ", ".join(fields_studyspots)
        clause_hours = ", ".join(fields_hours)       


        if clause_studyspots:
            queries.append((
                f"""
                UPDATE studyspots
                SET {clause_studyspots}, updated_at = NOW()
                WHERE id = :id;
                """,
                params
            ))

        if clause_hours:
            queries.append((
                f"""
                UPDATE hours
                SET {clause_hours}
                WHERE studyspot_id = :id;
                """,
                params
            ))
            queries.append((
                f"""
                UPDATE studyspots
                SET updated_at = NOW()
                WHERE id = :id;
                """,
                params
            ))

        queries.append((
            """
            SELECT *
            FROM studyspots s
            JOIN hours h ON s.id = h.studyspot_id
            WHERE s.id = :id;
            """,
            params
        ))

        spot = execute_query(queries, fetchone=True)

        result = StudySpotRead(
            id=spot["id"],
            name=spot["name"],
            address=AddressRead(
                street=spot["street"],
                city=spot["city"],
                state=spot.get("state", "NY"),
                postal_code=spot.get("postal_code", "00000"),
                latitude=spot.get("latitude"),
                longitude=spot.get("longitude"),
                neighborhood=spot.get("neighborhood"),
            ),
            amenity=AmenitiesRead(
                wifi_available=bool(spot["wifi_available"]),
                wifi_network=spot.get("wifi_network"),
                outlets=bool(spot["outlets"]),
                seating=spot["seating"],
                refreshments=spot["refreshments"],
                environment=[Environment(env) for env in spot["environment"]],
            ),
            hour=HoursBase(
                mon_start=spot["mon_start"], mon_end=spot["mon_end"],
                tue_start=spot["tue_start"], tue_end=spot["tue_end"],
                wed_start=spot["wed_start"], wed_end=spot["wed_end"],
                thu_start=spot["thu_start"], thu_end=spot["thu_end"],
                fri_start=spot["fri_start"], fri_end=spot["fri_end"],
                sat_start=spot["sat_start"], sat_end=spot["sat_end"],
                sun_start=spot["sun_start"], sun_end=spot["sun_end"],
            ),
            created_at=spot["created_at"],
            updated_at=spot["updated_at"],
        )
        return {
            "data": result, 
            "links": [
                {
                    "href": "self",
                    "rel": f"/studyspots/{studyspot_id}",
                    "type" : "GET"
                }
            ]
        }
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/studyspots/{studyspot_id}", status_code=204)
def delete_studyspot(studyspot_id: UUID):
    try:
        queries = [
            ("DELETE FROM hours WHERE studyspot_id = :id;", {"id": str(studyspot_id)}),
            ("DELETE FROM studyspots WHERE id = :id;", {"id": str(studyspot_id)})
        ]
        spot = execute_query(queries)
        if spot == 0:
            raise HTTPException(status_code=404, detail=f"Study spot {str(studyspot_id)} not found.")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Async Geocoding
# -----------------------------------------------------------------------------
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
jobs = {}
def get_geocode(street, city="New York", state="NY"):    
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    address = f"{street}, {city}, {state}"
    data = gmaps.geocode(address)
    if not data:
        raise Exception(f"Geocoding failed: no results for address '{address}'")
    print("hello")
    
    location = data[0]["geometry"]["location"]
    latitude = location["lat"]
    longitude = location["lng"]

    for comp in data[0]["address_components"]:
        if "postal_code" in comp["types"]:
            postal_code = comp["long_name"]
            break
    return latitude, longitude, postal_code


def run_geocode_job(job_id: str, studyspot_id: UUID):
    jobs[job_id]["status"] = "running"
    try: 
        queries = [(
            """
            SELECT street, city, state FROM studyspots WHERE id = :id
            """, 
            {"id": str(studyspot_id)}
        )]

        spot = execute_query(queries, fetchone=True)
        if not spot:
            raise HTTPException(status_code=404, detail=f"Study spot {studyspot_id} not found.")

        latitude, longitude, postal_code = get_geocode(spot["street"], spot["city"], spot["state"])
        
        query = """
            UPDATE studyspots
            SET latitude = :lat, longitude = :lng, updated_at = NOW()
        """
        
        params = {
                "lat": latitude, 
                "lng": longitude, 
                "id": str(studyspot_id)
            }

        if postal_code is not None:
            query += ", postal_code = :postal_code"
            params["postal_code"] = postal_code
        query += " WHERE id = :id"

        execute_query([(query, params)])

        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result"] = {
            "latitude": latitude, 
            "longitude": longitude, 
            "postal_code": postal_code, 
            "message": "Geocode successful"
        }

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": str(e)}
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/studyspots/{studyspot_id}/geocode", status_code=202)
def post_studyspot_geocode(studyspot_id: UUID, background_tasks: BackgroundTasks, response: Response):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "pending", "result": None}

    background_tasks.add_task(run_geocode_job, job_id, studyspot_id)

    response.headers["Location"] = f"/jobs/{job_id}"
    return {"message": "Geocoding started.", "job_id": job_id}
    
    
@app.get("/jobs/{job_id}", status_code=200)
def get_job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job["result"]
    }

@app.get("/")
def root():
    return {"message": "Welcome to the Study Spot API. See /docs for OpenAPI UI."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)   
