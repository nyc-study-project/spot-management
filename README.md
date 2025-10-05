# Spot Management
This microservice manages study spots in NYC. It provides the spot name, address, amenities, and hours. 

# Models 
**studyspot.py** - Represents NYC study spots registered by user. 
- stores name, address, amenities, and hours.
- has uuid which acts as the primary key.
- has created_at and updated_at timestamps.

**address.py** - Address of each study spot. One address per spot. 
- stores street, city, state, zip, longitude, latitude, and neighborhood.

**amenities.py** - Amenities provided at each study spot. One amenity per spot. 
- stores wifi availability, wifi name, outlet availability, amount of seating, type of refreshments, type of environment.

**hours.py** - Hours of spot for every day of the week. One hours model per spot. 
- stores day, start time, and end time. 
- not implemented yet.

# Endpoints 
**Study Spots**
- POST /study-spots    Create a new study spot
- GET /study-spots    Retrieve all study spots
- GET /study-spots/{id}    Retrieve study spot with specific id
- PATCH /study-spots/{id}    Update part of a specific study spot
- DELETE  /study-spots/{id}    Remove study spot 

# Sprint 1
All models except hours is made. All Endpoints are created. 
<img width="585" height="560" alt="Screenshot 2025-10-04 at 10 11 55 PM" src="https://github.com/user-attachments/assets/b4f5d4ad-2f9a-4dd1-91f6-eded626a9306" />
