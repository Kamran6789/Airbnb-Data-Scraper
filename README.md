# Airbnb-Data-Scraper
This project automates the process of collecting Airbnb listing data across multiple cities and varying guest counts using Selenium WebDriver. It scrapes availability, pricing, and listing volumes for different weekends and guest configurations to analyze trends in Airbnb accommodation data.

🔍 Key Features:
✅ City-Based Search: Reads city names from a CSV file and searches Airbnb for each city.

✅ Guest Variations: Scrapes data for different guest counts (from 2 to 16 guests).

✅ Date Flexibility: Selects specific weekends and custom date ranges for consistent comparison.

✅ Price Extraction: Uses Airbnb’s price histogram API data and slider manipulation to fetch minimum, maximum, and median prices.

✅ Network Sniffing: Captures internal API calls from Airbnb to extract accurate price distribution data.

✅ Excel Reporting: Saves the final results to an Excel file (airbnb_all_guests_results.xlsx) with columns including city, guest count, price range, and availability across future weekends.

📂 Output:
Each row in the Excel file contains:

city: City name searched.

guest: Number of guests used in the search.

total available accommodations: Total listings found.

low end, median, high end: Price statistics.

Listing counts for multiple weekends, such as:

This weekend

1 Week Out

2 Week Out

1 Month Out

And up to 12 Months Out

🧠 Technologies Used:
Python

Selenium

Pandas

Chrome DevTools Protocol (CDP) for capturing internal Airbnb API responses

📈 Use Cases:
Market research for short-term rental pricing.

Demand trend analysis for different seasons and guest sizes.

Identifying cities with high availability or price drops.

Real estate or travel planning insights.


