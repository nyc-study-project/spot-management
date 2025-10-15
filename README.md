# Spot Management
This microservice manages study spots in NYC. It provides the spot name, address, amenities, and hours. 

# Models 
**studyspot.py** - Represents NYC study spots registered by user. 
- stores name, address, amenities, and hours.
- has uuid which acts as the primary key.
- has created_at and updated_at timestamps.

**address.py** - Address of each study spot. One address per spot. 
- stores street, city, state, zip, longitude, latitude, and neighborhood.
- has studyspot.py PK as FK

**amenities.py** - Amenities provided at each study spot. One amenity per spot. 
- stores wifi availability, wifi name, outlet availability, amount of seating, type of refreshments, type of environment.
- has studyspot.py PK as FK

**hours.py** - Hours of spot for every day of the week. One hours per spot. 
- stores day, start time, and end time. 
- has studyspot.py PK as FK

# Endpoints 
**Study Spots**
- POST /study-spots    Create a new study spot
- GET /study-spots    Retrieve all study spots
- GET /study-spots/{id}    Retrieve study spot with specific id
- PATCH /study-spots/{id}    Update part of a specific study spot
- DELETE  /study-spots/{id}    Remove study spot 

# Sprint 1
All models are made. All Endpoints are locally created. 
<img width="1412" height="546" alt="Screenshot 2025-10-04 at 10 13 02 PM" src="https://github.com/user-attachments/assets/30381cc5-b55a-4bf3-9a29-02b6509f36f8" />

# Sprint 2 - IN PROGRESS
Connected main.py to Cloud Run. Cloud Run is connected to Cloud SQL instance with spot-management database. 

Things to todo: 
- create table in GCP database 
- import test data into database
- implement FastAPI endpoints that connect to database

# TODO
- connect address.py, amenities.py, and hours.py FK to studyspot.py PK.
- implement endpoints that connect to DB.