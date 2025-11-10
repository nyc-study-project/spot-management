from __future__ import annotations

import os
import socket
import json
import hashlib
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from psycopg2.extras import Json

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import PositiveInt

from models.hours import HoursBase
from models.studyspot import StudySpotCreate, StudySpotRead, StudySpotUpdate, StudySpotResponse
from models.address import AddressRead, Neighborhood
from models.amenities import AmenitiesRead, Seating, Environment
from models.health import Health


from fastapi import Request, Response, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback

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

# -----------------------------------------------------------------------------
# StudySpots
# -----------------------------------------------------------------------------
@app.post("/studyspots", response_model=StudySpotResponse, status_code=201)
def create_studyspot(studyspot: StudySpotCreate, response: Response):
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
            "links": {
                "link_studyspot": f"/studyspots/{spot_id}",
                "link_reviews": f"/studyspots/{spot_id}/reviews"
            }
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
        base_query = """
            SELECT * FROM studyspots s
            JOIN hours h ON s.id = h.studyspot_id
            WHERE 1=1
        """
        params = {"page_size": page_size, "offset": (page-1)*page_size}

        if name:
            base_query += " AND name LIKE :name"
            params["name"]=f"%{name}%"
        if neighborhood: 
            base_query += " AND neighborhood = :neighborhood"
            params["neighborhood"] = neighborhood.value if isinstance(neighborhood, Enum) else neighborhood
        if wifi is not None:
            base_query += " AND wifi_available = :wifi_available"
            params["wifi_available"]=wifi
        if outlets is not None:
            base_query += " AND outlets = :outlets"
            params["outlets"]=outlets
        if seating:
            base_query += " AND seating = :seating"
            params["seating"] = seating.value if isinstance(seating, Enum) else seating
        if refreshments:
            base_query += " AND refreshments LIKE :refreshments"
            params["refreshments"]=f"%{refreshments}%"
        if environment:
            base_query += " AND s.environment @> :environment"
            params["environment"] = environment.value if isinstance(environment, Enum) else environment
        if open_day: 
            base_query += f" AND h.{open_day.value}_start IS NOT NULL"
        if open_now: 
            base_query += f" AND h.{current_day}_start <= :current_time AND h.{current_day}_end >= :current_time"
            params["current_time"] = current_time

        base_query += " LIMIT :page_size OFFSET :offset"

        results = execute_query([(base_query, params)]) or []

        def build_url(page_number):
            query_params = dict(request.query_params)
            query_params["page"] = page_number
            query_params["page_size"] = page_size
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            return f"{request.url.path}?{query_string}"

        items = []
        for r in results:
            items.append({
                "data": StudySpotRead(
                    id=r["id"],
                    name=r["name"],
                    address=AddressRead(
                        street=r.get("street"),
                        city=r.get("city"),
                        state=r.get("state"),
                        postal_code=r.get("postal_code"),
                        latitude=r.get("latitude"),
                        longitude=r.get("longitude"),
                        neighborhood=r.get("neighborhood"),
                    ),
                    amenity=AmenitiesRead(
                        wifi_available=bool(r["wifi_available"]),
                        wifi_network=r.get("wifi_network"),
                        outlets=bool(r["outlets"]),
                        seating=r.get("seating"),
                        refreshments=r.get("refreshments"),
                        environment=json.loads(r.get("environment") or "[]"),
                    ),
                    hour=HoursBase(),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at") or datetime.utcnow(),
                ),
                "links": {
                    "self": f"/studyspots/{r['id']}",
                    "reviews": f"/studyspots/{r['id']}/reviews"
                }
            })

        total_items = len(results)
        response_data = {
            "data": items,
            "links": {
                "first": build_url(1),
                "prev": build_url(page - 1) if page > 1 else None,
                "next": build_url(page + 1) if total_items == page_size else None,
                "last": build_url(1000)
            }
        }
        print("hello2")
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
            "links": {
                "link_self": f"/studyspots/{studyspot_id}", 
                "link_reviews": f"/studyspots/{studyspot_id}/reviews"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.patch("/studyspots/{studyspot_id}", response_model=StudySpotResponse, status_code=200)
def update_studyspot(
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
        if city is not None:
            fields_studyspots.append("city = :city")
            params["city"] = city
        if neighborhood is not None:
            fields_studyspots.append("neighborhood = :neighborhood")
            params["neighborhood"] = neighborhood.value if hasattr(neighborhood, "value") else neighborhood
        # automatically change the rest of address based on street/city change

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
        print("hello1")
        spot = execute_query(queries, fetchone=True)
        print("hello2")
        print(spot)

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
            "links": {
                "link_self": f"/studyspots/{studyspot_id}", 
                "link_reviews": f"/studyspots/{studyspot_id}/reviews"
            }
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


@app.get("/")
def root():
    return {"message": "Welcome to the Study Spot API. See /docs for OpenAPI UI."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)   
