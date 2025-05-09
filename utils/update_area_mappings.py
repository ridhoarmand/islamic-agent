import aiohttp
import asyncio
import json
import os

# Path to area mappings file
AREA_MAPPINGS_PATH = "data/area_mappings.json"

async def fetch_all_cities():
    """
    Fetch all cities from MyQuran API
    
    Returns:
        List of dictionaries containing city ID and name
    """
    api_url = "https://api.myquran.com/v2/sholat/kota/semua"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] and data["data"]:
                        return data["data"]
                    else:
                        print("Error: API returned no data")
                        return []
                else:
                    print(f"Error: HTTP status {response.status}")
                    return []
    except Exception as e:
        print(f"Error fetching cities: {str(e)}")
        return []

async def fetch_city_id(city_name):
    """
    Fetch city ID from MyQuran API
    
    Args:
        city_name: Name of the city to search for
        
    Returns:
        Dictionary with city ID and name if found, None otherwise
    """
    api_url = "https://api.myquran.com/v2/sholat/kota/cari/"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_url}{city_name}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] and data["data"]:
                        # Return the first matching city
                        return {
                            "id": data["data"][0]["id"],
                            "name": data["data"][0]["lokasi"]
                        }
    except Exception as e:
        print(f"Error fetching city ID for {city_name}: {str(e)}")
    
    return None

async def update_area_mappings():
    """
    Update area mappings with MyQuran API city IDs
    """
    # Check if file exists, if not create an empty template
    if not os.path.exists(AREA_MAPPINGS_PATH):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(AREA_MAPPINGS_PATH), exist_ok=True)
        # Create default mapping structure
        mappings = {"mappings": {}, "regions": {}}
    else:
        # Load existing mappings
        with open(AREA_MAPPINGS_PATH, "r", encoding="utf-8") as f:
            mappings = json.load(f)
            if "mappings" not in mappings:
                mappings["mappings"] = {}
            if "regions" not in mappings:
                mappings["regions"] = {}
    
    print("Fetching all cities from MyQuran API...")
    all_cities = await fetch_all_cities()
    
    if not all_cities:
        print("Failed to fetch cities from API. No updates made.")
        return
    
    print(f"Successfully fetched {len(all_cities)} cities")
    
    # Update mappings
    added_count = 0
    updated_count = 0
    
    for city in all_cities:
        city_id = city["id"]
        city_name = city["lokasi"]
        
        # Use the city name as the key (lowercase for case-insensitive matching)
        city_key = city_name.lower()
        
        # Add or update the city in mappings
        if city_key in mappings["mappings"]:
            if mappings["mappings"][city_key]["id"] != city_id:
                mappings["mappings"][city_key]["id"] = city_id
                mappings["mappings"][city_key]["name"] = city_name
                updated_count += 1
                print(f"Updated {city_name} to ID {city_id}")
        else:
            mappings["mappings"][city_key] = {
                "id": city_id,
                "name": city_name
            }
            added_count += 1
    
    # Also update traditional cities list for backwards compatibility
    traditional_cities = [
        "Jakarta", "Bandung", "Surabaya", "Semarang", "Medan", 
        "Makassar", "Depok", "Bogor", "Tangerang", "Bekasi", 
        "Yogyakarta", "Purwokerto", "Banyumas"
    ]
    
    for city in traditional_cities:
        print(f"Ensuring {city} is properly mapped...")
        city_data = await fetch_city_id(city)
        if city_data:
            city_key = city.lower()
            if city_key in mappings["mappings"]:
                if mappings["mappings"][city_key]["id"] != city_data["id"]:
                    mappings["mappings"][city_key]["id"] = city_data["id"]
                    mappings["mappings"][city_key]["name"] = city_data["name"]
                    updated_count += 1
                    print(f"Updated {city} to ID {city_data['id']} ({city_data['name']})")
            else:
                mappings["mappings"][city_key] = {
                    "id": city_data["id"],
                    "name": city_data["name"]
                }
                added_count += 1
                print(f"Added {city} with ID {city_data['id']} ({city_data['name']})")
    
    # Save updated mappings
    with open(AREA_MAPPINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)
    
    print(f"Finished updating area mappings:")
    print(f"- Added {added_count} new cities")
    print(f"- Updated {updated_count} existing cities")
    print(f"- Total mappings: {len(mappings['mappings'])}")
    print(f"File saved to {AREA_MAPPINGS_PATH}")

if __name__ == "__main__":
    asyncio.run(update_area_mappings())
