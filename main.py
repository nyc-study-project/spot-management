from __future__ import annotations

import os
import socket
import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import PositiveInt

from models.hours import HoursBase
from models.studyspot import StudySpotCreate, StudySpotRead, StudySpotUpdate
from models.address import AddressRead
from models.amenities import AmenitiesRead
from models.health import Health


from fastapi import Request
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

            connection_str = (
                f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
            )
        else:
            # Production — connects via Cloud SQL Unix socket
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


# # -----------------------------------------------------------------------------
# # Database Connection
# # -----------------------------------------------------------------------------
def execute_query(Session, query: str, params: dict | tuple | None=None, fetchone=False):
    try: 
        with Session() as session:
            result = session.execute(text(query), params or {})

            if query.strip().upper().startswith("SELECT"):
                rows = result.mappings().fetchone() if fetchone else result.mappings().all()
                return rows
            else: 
                session.commit()
                return result.rowcount

    except Exception as e:
        session.rollback()
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
# StudySpots
# -----------------------------------------------------------------------------
@app.post("/studyspots", response_model=StudySpotRead, status_code=201)
def create_studyspot(studyspot: StudySpotCreate):
    try:
        spot_id = str(uuid4())
        # 1️⃣ Insert study spot
        queries = [
            (
                """
                INSERT INTO studyspots (
                    id, name, street, city, state, postal_code, latitude, longitude, neighborhood,
                    wifi_available, wifi_network, outlets, seating, refreshments, environment, created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP()
                );
                """,
                (
                    spot_id,
                    studyspot.name,
                    getattr(studyspot.address, "street", None),
                    getattr(studyspot.address, "city", None),
                    getattr(studyspot.address, "state", None),
                    getattr(studyspot.address, "postal_code", None),
                    getattr(studyspot.address, "latitude", None),
                    getattr(studyspot.address, "longitude", None),
                    getattr(studyspot.address, "neighborhood", None),
                    studyspot.amenity.wifi_available,
                    getattr(studyspot.amenity, "wifi_network", None),
                    studyspot.amenity.outlets,
                    studyspot.amenity.seating.value if hasattr(studyspot.amenity.seating, "value") else studyspot.amenity.seating,
                    studyspot.amenity.refreshments,
                    # ✅ FIX: tolerate string or Enum values
                    json.dumps([
                        env.value if hasattr(env, "value") else env
                        for env in (studyspot.amenity.environment or [])
                    ]),
                ),
            )
        ]

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            start = getattr(studyspot.hour, f"{day}_start", None)
            end = getattr(studyspot.hour, f"{day}_end", None)
            if start or end:
                queries.append((
                    """
                    INSERT INTO hours (id, studyspot_id, day_of_week, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (str(uuid4()), spot_id, day, start, end)
                ))

        # 3️⃣ Retrieve the newly created record
        queries.append(("SELECT * FROM studyspots WHERE id = %s;", (spot_id,)))

        new_spot = execute_query(queries, only_one=True)
        if not new_spot:
            raise HTTPException(status_code=500, detail="Failed to create new study spot.")

        response = StudySpotRead(
            id=new_spot["id"],
            name=new_spot["name"],
            address=AddressRead(
                street=new_spot["street"],
                city=new_spot["city"],
                state=new_spot.get("state", "NY"),
                postal_code=new_spot.get("postal_code", "00000"),
                latitude=new_spot.get("latitude"),
                longitude=new_spot.get("longitude"),
                neighborhood=new_spot.get("neighborhood"),
            ),
            amenity=AmenitiesRead(
                wifi_available=bool(new_spot["wifi_available"]),
                wifi_network=new_spot.get("wifi_network"),
                outlets=bool(new_spot["outlets"]),
                seating=new_spot["seating"],
                refreshments=new_spot["refreshments"],
                environment=json.loads(new_spot.get("environment") or "[]"),
            ),
            hour=HoursBase(),
            created_at=new_spot["created_at"],
            updated_at=new_spot.get("updated_at") or datetime.utcnow(),
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# Other routes unchanged
# -----------------------------------------------------------------------------
@app.get("/studyspots", response_model=List[StudySpotRead])
def list_studyspots(
    name: Optional[str] = Query(None),
    wifi: Optional[bool] = Query(None),
    outlets: Optional[bool] = Query(None),
    seating: Optional[PositiveInt] = Query(None),
    refreshments: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
):
    try:
        base_query = "SELECT * FROM studyspots WHERE 1=1"
        params = []
        if name:
            base_query += " AND name = %s"
            params.append(name)
        if wifi is not None:
            base_query += " AND wifi_available = %s"
            params.append(wifi)
        if outlets is not None:
            base_query += " AND outlets = %s"
            params.append(outlets)
        if seating is not None:
            base_query += " AND seating >= %s"
            params.append(seating)
        if refreshments:
            base_query += " AND refreshments LIKE %s"
            params.append(f"%{refreshments}%")
        if city:
            base_query += " AND city = %s"
            params.append(city)

        queries = [(base_query + ";", tuple(params))]
        results = execute_query(queries) or []
        return [StudySpotRead(
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
        ) for r in results]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/studyspots/{studyspot_id}", response_model=StudySpotRead)
def get_studyspot(studyspot_id: UUID):
    try:
        queries = [("SELECT * FROM studyspots WHERE id = %s;", (str(studyspot_id),))]
        result = execute_query(queries, only_one=True)
        if not result:
            raise HTTPException(status_code=404, detail=f"Study spot {studyspot_id} not found.")

        return StudySpotRead(
            id=result["id"],
            name=result["name"],
            address=AddressRead(
                street=result.get("street"),
                city=result.get("city"),
                state=result.get("state"),
                postal_code=result.get("postal_code"),
                latitude=result.get("latitude"),
                longitude=result.get("longitude"),
                neighborhood=result.get("neighborhood"),
            ),
            amenity=AmenitiesRead(
                wifi_available=bool(result["wifi_available"]),
                wifi_network=result.get("wifi_network"),
                outlets=bool(result["outlets"]),
                seating=result.get("seating"),
                refreshments=result.get("refreshments"),
                environment=json.loads(result.get("environment") or "[]"),
            ),
            hour=HoursBase(),
            created_at=result.get("created_at"),
            updated_at=result.get("updated_at") or datetime.utcnow(),
        )
    except HTTPException:
        # Let 404 bubble up
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.patch("/studyspots/{studyspot_id}", response_model=StudySpotRead)
def update_studyspot(studyspot_id: UUID, update: StudySpotUpdate):
    try:
        fields = []
        params = []

        # --- Basic info ---
        if update.name:
            fields.append("name = %s")
            params.append(update.name)

        # --- Address (partial) ---
        if update.address:
            if update.address.street:
                fields.append("street = %s")
                params.append(update.address.street)
            if update.address.city:
                fields.append("city = %s")
                params.append(update.address.city)

        # --- Amenity (partial, optional fields) ---
        if update.amenity:
            if update.amenity.wifi_available is not None:
                fields.append("wifi_available = %s")
                params.append(update.amenity.wifi_available)
            if update.amenity.wifi_network is not None:
                fields.append("wifi_network = %s")
                params.append(update.amenity.wifi_network)
            if update.amenity.outlets is not None:
                fields.append("outlets = %s")
                params.append(update.amenity.outlets)
            if update.amenity.seating is not None:
                val = update.amenity.seating
                if hasattr(val, "value"):
                    val = val.value
                fields.append("seating = %s")
                params.append(val)

            if update.amenity.refreshments is not None:
                fields.append("refreshments = %s")
                params.append(update.amenity.refreshments)
            if update.amenity.environment is not None:
                fields.append("environment = %s")
                params.append(json.dumps(update.amenity.environment))

        # --- Error if no update fields ---
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        # --- Construct and execute ---
        set_clause = ", ".join(fields)
        params.append(str(studyspot_id))
        queries = [
            (
                f"UPDATE studyspots SET {set_clause}, updated_at = UTC_TIMESTAMP() WHERE id = %s;",
                tuple(params),
            ),
            ("SELECT * FROM studyspots WHERE id = %s;", (str(studyspot_id),)),
        ]

        updated_spot = execute_query(queries, only_one=True)
        if not updated_spot:
            raise HTTPException(status_code=404, detail=f"Study spot {studyspot_id} not found.")

        return StudySpotRead(
            id=updated_spot["id"],
            name=updated_spot["name"],
            address=AddressRead(
                street=updated_spot.get("street"),
                city=updated_spot.get("city"),
                state=updated_spot.get("state"),
                postal_code=updated_spot.get("postal_code"),
                latitude=updated_spot.get("latitude"),
                longitude=updated_spot.get("longitude"),
                neighborhood=updated_spot.get("neighborhood"),
            ),
            amenity=AmenitiesRead(
                wifi_available=bool(updated_spot["wifi_available"]),
                wifi_network=updated_spot.get("wifi_network"),
                outlets=bool(updated_spot["outlets"]),
                seating=updated_spot.get("seating"),
                refreshments=updated_spot.get("refreshments"),
                environment=json.loads(updated_spot.get("environment") or "[]"),
            ),
            hour=HoursBase(),
            created_at=updated_spot.get("created_at"),
            updated_at=updated_spot.get("updated_at") or datetime.utcnow(),
        )


    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/studyspots/{studyspot_id}", status_code=204)
def delete_studyspot(studyspot_id: UUID):
    try:
        queries = [("DELETE FROM studyspots WHERE id = %s;", (str(studyspot_id),))]
        rows_deleted = execute_query(queries)
        if rows_deleted == 0:
            raise HTTPException(status_code=404, detail=f"Study spot {studyspot_id} not found.")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Welcome to the Study Spot API. See /docs for OpenAPI UI."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
