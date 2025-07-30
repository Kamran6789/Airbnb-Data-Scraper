import pandas as pd
import time
from selenium import webdriver
from guests_data import search_airbnb_for_guests


def read_cities_from_csv(csv_file="cities.csv"):
    """Read cities from CSV file and return a list of city names"""
    try:
        df = pd.read_csv(csv_file)
        # Extract city names from the 'City' column
        cities = df['city'].dropna().tolist()
        print(f"📋 Loaded {len(cities)} cities from {csv_file}")
        return cities
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        # Fallback to a few default cities
        return ["London", "New York", "Paris"]


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# Enable performance logging to capture network requests
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Read cities from CSV
cities = read_cities_from_csv()

total_cities = len(cities)
# Iterate over each city
for city_index, city in enumerate(cities[11:], 1):
    print(f"\n🌍 Processing city {city_index}/{total_cities}: {city}")
    print("=" * 50)
    driver = webdriver.Chrome(options=options)
    try:
        # For each city, process all guest counts
        for guests in range(2, 17):
            try:
                print(f"👥 Processing {guests} guests for {city}...")
                search_airbnb_for_guests(driver, guests, city)
                print(f"✅ Completed {guests} guests for {city}")
            except Exception as e:
                print(f"❌ Error processing {guests} guests for {city}: {e}")
                # Continue with next guest count instead of stopping
                continue
        print(f"✅ Completed all guest counts for {city}")
        print("-" * 50)
    finally:
        driver.quit()
        print(f"🛑 Closed browser for {city}")
    # Add a small delay between cities to be respectful to the server
    if city_index < total_cities:  # Don't delay after the last city
        print("⏳ Waiting 5 seconds before next city...")
        time.sleep(5)
print("🏁 All cities processed. Check airbnb_all_guests_results.xlsx for results.")
