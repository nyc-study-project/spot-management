import requests

# When running locally; later change this to your Cloud Run URL.
BASE_URL = "http://localhost:8000"

spots = [
    # 1) Financial District
    {
        "name": "Battery Park City Library",
        "address": {
            "street": "175 North End Ave",
            "city": "New York",
            "state": "NY",
            "postal_code": "10282",
            "longitude": -74.0150,
            "latitude": 40.7150,
            "neighborhood": "Financial District (FiDi)"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "10:00", "thu_end": "18:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 2) Tribeca
    {
        "name": "Laughing Man Coffee - Duane Street",
        "address": {
            "street": "184 Duane St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10013",
            "longitude": -74.0103,
            "latitude": 40.7167,
            "neighborhood": "Tribeca"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "Guest",
            "outlets": True,
            "seating": "6-10",
            "refreshments": "coffee, pastries",
            "environment": ["lively", "indoor"]
        },
        "hour": {
            "mon_start": "07:00", "mon_end": "18:00",
            "tue_start": "07:00", "tue_end": "18:00",
            "wed_start": "07:00", "wed_end": "18:00",
            "thu_start": "07:00", "thu_end": "18:00",
            "fri_start": "07:00", "fri_end": "18:00",
            "sat_start": "08:00", "sat_end": "18:00",
            "sun_start": "08:00", "sun_end": "18:00"
        }
    },

    # 3) SoHo
    {
        "name": "Housing Works Bookstore Cafe",
        "address": {
            "street": "126 Crosby St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10012",
            "longitude": -73.9971,
            "latitude": 40.7243,
            "neighborhood": "SoHo"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "Bookstore WiFi",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "coffee, pastries",
            "environment": ["lively", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "21:00",
            "tue_start": "10:00", "tue_end": "21:00",
            "wed_start": "10:00", "wed_end": "21:00",
            "thu_start": "10:00", "thu_end": "21:00",
            "fri_start": "10:00", "fri_end": "22:00",
            "sat_start": "10:00", "sat_end": "22:00",
            "sun_start": "10:00", "sun_end": "20:00"
        }
    },

    # 4) Chinatown
    {
        "name": "Chatham Square Library (NYPL)",
        "address": {
            "street": "33 E Broadway",
            "city": "New York",
            "state": "NY",
            "postal_code": "10002",
            "longitude": -73.9960,
            "latitude": 40.7130,
            "neighborhood": "Chinatown"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "11:00", "tue_end": "19:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "10:00", "thu_end": "18:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 5) Lower East Side
    {
        "name": "Seward Park Library (NYPL)",
        "address": {
            "street": "192 East Broadway",
            "city": "New York",
            "state": "NY",
            "postal_code": "10002",
            "longitude": -73.9882,
            "latitude": 40.7147,
            "neighborhood": "Lower East Side"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "20+",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "11:00", "thu_end": "19:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 6) Greenwich Village (West Village)
    {
        "name": "NYU Bobst Library",
        "address": {
            "street": "70 Washington Square S",
            "city": "New York",
            "state": "NY",
            "postal_code": "10012",
            "longitude": -73.9973,
            "latitude": 40.7295,
            "neighborhood": "West Village"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYU",
            "outlets": True,
            "seating": "20+",
            "refreshments": "cafe in building",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "08:00", "mon_end": "02:00",
            "tue_start": "08:00", "tue_end": "02:00",
            "wed_start": "08:00", "wed_end": "02:00",
            "thu_start": "08:00", "thu_end": "02:00",
            "fri_start": "08:00", "fri_end": "22:00",
            "sat_start": "10:00", "sat_end": "22:00",
            "sun_start": "10:00", "sun_end": "02:00"
        }
    },

    # 7) East Village
    {
        "name": "Tompkins Square Library (NYPL)",
        "address": {
            "street": "331 E 10th St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10009",
            "longitude": -73.9819,
            "latitude": 40.7264,
            "neighborhood": "East Village"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "11:00", "thu_end": "19:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 8) Chelsea
    {
        "name": "Cafe Grumpy Chelsea",
        "address": {
            "street": "224 W 20th St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10011",
            "longitude": -73.9993,
            "latitude": 40.7432,
            "neighborhood": "Chelsea"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "Guest",
            "outlets": True,
            "seating": "6-10",
            "refreshments": "coffee, pastries",
            "environment": ["lively", "indoor"]
        },
        "hour": {
            "mon_start": "07:00", "mon_end": "19:00",
            "tue_start": "07:00", "tue_end": "19:00",
            "wed_start": "07:00", "wed_end": "19:00",
            "thu_start": "07:00", "thu_end": "19:00",
            "fri_start": "07:00", "fri_end": "19:00",
            "sat_start": "08:00", "sat_end": "19:00",
            "sun_start": "08:00", "sun_end": "18:00"
        }
    },

    # 9) Flatiron District
    {
        "name": "Ace Hotel New York Lobby",
        "address": {
            "street": "20 W 29th St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "longitude": -73.9886,
            "latitude": 40.7450,
            "neighborhood": "Flatiron District"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "Ace Hotel",
            "outlets": True,
            "seating": "20+",
            "refreshments": "coffee, bar",
            "environment": ["lively", "indoor"]
        },
        "hour": {
            "mon_start": "07:00", "mon_end": "23:00",
            "tue_start": "07:00", "tue_end": "23:00",
            "wed_start": "07:00", "wed_end": "23:00",
            "thu_start": "07:00", "thu_end": "23:00",
            "fri_start": "07:00", "fri_end": "23:59",
            "sat_start": "08:00", "sat_end": "23:59",
            "sun_start": "08:00", "sun_end": "23:00"
        }
    },

    # 10) Midtown
    {
        "name": "Stavros Niarchos Foundation Library (Mid-Manhattan)",
        "address": {
            "street": "455 5th Ave",
            "city": "New York",
            "state": "NY",
            "postal_code": "10016",
            "longitude": -73.9800,
            "latitude": 40.7528,
            "neighborhood": "Midtown"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "20+",
            "refreshments": "cafe in building",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "20:00",
            "tue_start": "10:00", "tue_end": "20:00",
            "wed_start": "10:00", "wed_end": "20:00",
            "thu_start": "10:00", "thu_end": "20:00",
            "fri_start": "10:00", "fri_end": "18:00",
            "sat_start": "10:00", "sat_end": "18:00",
            "sun_start": "13:00", "sun_end": "17:00"
        }
    },

    # 11) Upper West Side
    {
        "name": "St. Agnes Library (NYPL)",
        "address": {
            "street": "444 Amsterdam Ave",
            "city": "New York",
            "state": "NY",
            "postal_code": "10024",
            "longitude": -73.9777,
            "latitude": 40.7833,
            "neighborhood": "Upper West Side"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "11:00", "thu_end": "19:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 12) Upper East Side
    {
        "name": "67th Street Library (NYPL)",
        "address": {
            "street": "328 E 67th St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10065",
            "longitude": -73.9587,
            "latitude": 40.7656,
            "neighborhood": "Upper East Side"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "11:00", "thu_end": "19:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 13) Harlem
    {
        "name": "Columbia University - Butler Library",
        "address": {
            "street": "535 W 114th St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10027",
            "longitude": -73.9620,
            "latitude": 40.8064,
            "neighborhood": "Harlem"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "Columbia U Secure",
            "outlets": True,
            "seating": "20+",
            "refreshments": "nearby cafes",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "08:00", "mon_end": "02:00",
            "tue_start": "08:00", "tue_end": "02:00",
            "wed_start": "08:00", "wed_end": "02:00",
            "thu_start": "08:00", "thu_end": "02:00",
            "fri_start": "08:00", "fri_end": "22:00",
            "sat_start": "10:00", "sat_end": "22:00",
            "sun_start": "10:00", "sun_end": "02:00"
        }
    },

    # 14) Washington Heights
    {
        "name": "Fort Washington Library (NYPL)",
        "address": {
            "street": "535 W 179th St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10033",
            "longitude": -73.9375,
            "latitude": 40.8486,
            "neighborhood": "Washington Heights"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "11:00", "thu_end": "19:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },

    # 15) Inwood
    {
        "name": "Inwood Library (NYPL)",
        "address": {
            "street": "4790 Broadway",
            "city": "New York",
            "state": "NY",
            "postal_code": "10034",
            "longitude": -73.9213,
            "latitude": 40.8675,
            "neighborhood": "Inwood"
        },
        "amenity": {
            "wifi_available": True,
            "wifi_network": "NYPL",
            "outlets": True,
            "seating": "11-20",
            "refreshments": "none",
            "environment": ["quiet", "indoor"]
        },
        "hour": {
            "mon_start": "10:00", "mon_end": "18:00",
            "tue_start": "10:00", "tue_end": "18:00",
            "wed_start": "11:00", "wed_end": "19:00",
            "thu_start": "11:00", "thu_end": "19:00",
            "fri_start": "10:00", "fri_end": "17:00",
            "sat_start": "10:00", "sat_end": "17:00",
            "sun_start": None,   "sun_end": None
        }
    },
]


def main():
    for spot in spots:
        resp = requests.post(f"{BASE_URL}/studyspots", json=spot)
        print(f"{spot['name']}: {resp.status_code}")
        if resp.status_code >= 400:
            print("  Error:", resp.text)


if __name__ == "__main__":
    main()
