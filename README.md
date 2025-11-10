# Spot Management
This microservice manages study spots in NYC. It provides the spot name, address, amenities, and hours. 

# Models 
**studyspot.py** - Represents NYC study spots registered by user. 
- stores name, address, amenities, hours, and created_at and updated_at timestamps.
- in the studyspot db. 
- has uuid which acts as the primary key.

**address.py** - Address of each study spot. One address per spot. 
- stores street, city, state, zip, longitude, latitude, and neighborhood.
- contained within the studyspot db.

**amenities.py** - Amenities provided at each study spot. One amenity per spot. 
- stores wifi availability, wifi name, outlet availability, amount of seating, type of refreshments, type of environment.
- contianed within the studyspot db.

**hours.py** - Hours of spot for every day of the week. One hours per spot. 
- stores start time and end time for each day.
- in the hours db. 
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
    ![alt text](image.png)
4. Query Parameters & Filters
    - Collection endpoints (e.g., GET /studyspots) support filtering by:
        - Name, city, neighborhood, amenities (wifi, outlets, seating, refreshments), environment (JSONB array), day open and open now.
5. Pagination
    - Endpoints support page and page_size query parameters.
    - Responses include data and navigation links (self, review, first, prev, next, last).
6. POST Requests
    - POST /studyspots returns 201 Created and a Location header pointing to the newly created resource.
7. Linked Data
    - All responses include linked data with relative paths:
        - links.self → resource itself
        - links.reviews → related reviews endpoint

# TODO
- Deploy on team's Cloud Run
- Implement a 202 Accepted asynchronous operation (POST /studyspots/{id}/geocode)
     - Returns 202 + Location: /jobs/{job_id}
     - Provide GET /jobs/{job_id} polling endpoint that returns {"status": "pending|running|complete", "result": {...}}
     - OpenAPI docs showing eTag, pagination, filters, 201 + 202 async examples

