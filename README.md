# Spot Management
This microservice manages study spots in NYC. It provides the spot name, address, amenities, and hours. 

# Models 
**studyspot.py** - Represents NYC study spots registered by user. 
- stores name, address, amenities, hours, and created_at and updated_at timestamps.
- stored in the studyspot db. 
- has a uuid which acts as the primary key.

**address.py** - Address of each study spot. One address per spot. 
- stores street, city, state, zip, longitude, latitude, and neighborhood.
- stored in the studyspot db.

**amenities.py** - Amenities provided at each study spot. One amenity per spot. 
- stores wifi availability, wifi name, outlet availability, amount of seating, type of refreshments, type of environment.
- stored in the studyspot db.

**hours.py** - Hours of spot for every day of the week. One hours per spot. 
- stores start time and end time for each day of teh week.
- stored in the hours db. 
- has studyspot.py PK as FK.

# Endpoints 
**Study Spots**
- POST /studyspots    
    - Creates a new study spot.
    - Assigns a unique id. 
- GET /studyspots
    - Retrieves all study spots
    - Includes pagination and filters by name, street, city, amenity, open now, and open date.
- GET /studyspots/{id}
    - Retrieves study spot with specific id
- PATCH /studyspots/{id}
    - Updates part of a specific study spot
- DELETE  /studyspots/{id}
    - Removes study spot with specific id

# Sprint 1
All models are made. All Endpoints are locally created. 
<img width="1412" height="546" alt="Screenshot 2025-10-04 at 10 13 02 PM" src="https://github.com/user-attachments/assets/30381cc5-b55a-4bf3-9a29-02b6509f36f8" />

# Sprint 2 - IN PROGRESS
The main.py application is deployed on Cloud Run and successfully connected to a Cloud SQL PostgreSQL instance hosting the spot-management database, which includes the studyspots and hours tables.

### Implemented Features
1. Containerization and Deployment
    - Application is containerized with a Dockerfile and deployed to Cloud Run.
2. FastAPI Endpoints
    - Implemented RESTful endpoints using FastAPI and SQLAlchemy connected to a Cloud SQL PostgreSQL database with studyspots and hours tables.
3. ETag Support
    - GET /studyspots/{id} supports ETag headers for caching and conditional requests (returns 304 Not Modified when appropriate).
    <img width="1403" height="773" alt="Screenshot 2025-11-09 at 10 48 47 PM" src="https://github.com/user-attachments/assets/dc95dbc4-9ed6-490a-b4d4-6607a471a4d8" />
    <img width="1400" height="633" alt="Screenshot 2025-11-09 at 10 49 07 PM" src="https://github.com/user-attachments/assets/954d93d3-4146-42ad-8deb-5eebc903fbb0" />

4. Query Parameters & Filters
    - Bulk collection endpoint (GET /studyspots) supports filtering by name, neighborhood, amenities (wifi, outlets, seating, refreshments), environment (JSONB array), day open and open now.
    <img width="723" height="685" alt="Screenshot 2025-11-09 at 10 53 20 PM" src="https://github.com/user-attachments/assets/f1a65c6b-60fe-46ef-a19f-88dd24950370" />
5. Pagination
    - Bulk collection endpoint (GET /studyspots) supports page and page_size query parameters.
    - Responses include data and navigation links (self, study spot review, first page, prev page, next page, last page).
      <img width="719" height="434" alt="Screenshot 2025-11-09 at 10 53 56 PM" src="https://github.com/user-attachments/assets/93b77520-8dcb-48e8-bc6b-71350d8b0f2e" />

6. POST Requests
    - POST /studyspots returns 201 Created and a location header pointing to the newly created resource.
      <img width="962" height="441" alt="Screenshot 2025-11-09 at 10 57 52 PM" src="https://github.com/user-attachments/assets/341253c6-e357-4720-80fa-6f3214bb6864" />

7. Linked Data
    - All responses (execept Delete call) include linked data with relative paths:
        - links.self → resource itself
        - links.reviews → related reviews endpoint

8. Asynchronous Geocoding
    - Implemented a asynchronous operation (POST /studyspots/{id}/geocode) that triggers Google Geocoding API to update the study spot’s coordinates.
    - The response returns 202 Accepted with a Location header pointing to the job resource (/jobs/{job_id}).
    - A polling endpoint (GET /jobs/{job_id}) provides job status updates:
        - {"status": "pending|running|complete|failed", "result": {...}}

# TODO
- Deploy on team's Cloud Run
- Add pictures of demo data visible in Cloud SQL (Postgres) to README
- Async Geocoding 
    - Test connection to Google Geocode API
    - Add pictures of OpenAPI doc showing 201 + 202 async examples to README
    - Create code to automatically get geocode after creating a new studyspot or updating the street/city of an existing spot