import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
import json


def save_result_to_excel(row, filename="airbnb_all_guests_results.xlsx"):
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        updated_df = pd.concat([existing_df, pd.DataFrame([row])], ignore_index=True)
    else:
        updated_df = pd.DataFrame([row])
    updated_df.to_excel(filename, index=False)
    print(f"✅ Result for {row['guest']} guests in {row.get('city', 'Unknown')} added to {filename}")


def build_airbnb_aria_label(date_obj, role):
    day = date_obj.day
    weekday = date_obj.strftime("%A")
    month = date_obj.strftime("%B")
    year = date_obj.year
    return f"{day}, {weekday}, {month} {year}. Available. Select as {role} date."


# === MANUAL DATE SETTINGS ===
# For One night stays, set the check-in and check-out dates manually
friday = datetime(2025, 8, 1)  # Set your desired check-in date
saturday = datetime(2025, 8, 3)  # Set your desired check-out date

# List of weekends or custom date pairs for batch search
# Format: [("Label", datetime(checkin), datetime(checkout)), ...]
weekends = [
    ("This weekend", datetime(2025, 8, 1), datetime(2025, 8, 3)),
    ("1 Week Out", datetime(2025, 8, 8), datetime(2025, 8, 10)),
    ("2 Week Out", datetime(2025, 8, 22), datetime(2025, 8, 24)),
    ("1 Month Out", datetime(2025, 8, 29), datetime(2025, 8, 31)),
    ("2 Months (15–16)", datetime(2025, 9, 15), datetime(2025, 9, 16)),
    ("3 Months (15–16)", datetime(2025, 10, 15), datetime(2025, 10, 16)),
    ("4 Months (15–16)", datetime(2025, 11, 15), datetime(2025, 11, 16)),
    ("5 Months (15–16)", datetime(2025, 12, 15), datetime(2025, 12, 16)),
    ("6 Months (15–16)", datetime(2026, 1, 15), datetime(2026, 1, 16)),
    ("7 Months (15–16)", datetime(2026, 2, 15), datetime(2026, 2, 16)),
    ("8 Months (15–16)", datetime(2026, 3, 15), datetime(2026, 3, 16)),
    ("9 Months (15–16)", datetime(2026, 4, 15), datetime(2026, 4, 16)),
    ("10 Months (15–16)", datetime(2026, 5, 15), datetime(2026, 5, 16)),
    ("11 Months (15–16)", datetime(2026, 6, 15), datetime(2026, 6, 16)),
    ("12 Months (15–16)", datetime(2026, 7, 15), datetime(2026, 7, 16)),
]


def search_airbnb_for_guests(driver, guest_count, city_name):
    print(f"\n--- Searching Airbnb for {guest_count} guests ---")
    try:
        driver.get("https://www.airbnb.com/")
        time.sleep(20)
        try:
            got_it_button = driver.find_element(By.XPATH, "//button[normalize-space()='Got it']")
            got_it_button.click()
            print("✅ 'Got it' button clicked.")
        except:
            pass
        time.sleep(2)

        search_input = driver.find_element(By.XPATH, "//input[@placeholder='Search destinations']")
        # search_input.send_keys("Santa Fe")
        search_input.send_keys(city_name)
        time.sleep(1)
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)

        guest_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Add guests')]")
        guest_btn.click()
        time.sleep(2)

        try:
            increase_btn = driver.find_element(By.XPATH, "//button[@data-testid='stepper-adults-increase-button']")
            for _ in range(guest_count):
                increase_btn.click()
                time.sleep(0.3)
            print(f"✅ Adults now set to {guest_count}")
        except Exception as e:
            print("❌ Failed to set adults:", e)

        try:
            done_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Done')]")
            done_btn.click()
        except:
            guest_btn.click()
        time.sleep(3)

        search_btn = driver.find_element(By.XPATH, "//button[@data-testid='structured-search-input-search-button']")
        search_btn.click()
        time.sleep(2)

        try:
            import re
            heading_element = driver.find_element(By.XPATH, "//section[@aria-live='polite']//h1//span[1]")
            heading_text = heading_element.text
            match = re.search(r"Over\s([\d,]+)|([\d,]+)\+?", heading_text)
            if match:
                number_str = match.group(1) or match.group(2)
                number = int(number_str.replace(",", ""))
                print("🏘️ Number of places found:", number)
            else:
                print("❌ Number not found in text:", heading_text)
        except Exception as e:
            print("❌ Error extracting number of places:", e)

        # === DATE SELECTION ===
        # Use manually set friday and saturday
        friday_label = build_airbnb_aria_label(friday, "check-in")
        saturday_label = build_airbnb_aria_label(saturday, "checkout")

        try:
            checkin_button = driver.find_element(By.XPATH, "//button[@data-testid='little-search-date']")
            checkin_button.click()
            time.sleep(2)
        except Exception as e:
            print("❌ Failed to click 'Check in / Check out' button:", e)

        # Define a helper to move calendar forward if needed
        def click_until_date_visible(label):
            for _ in range(12):  # Try up to 12 months ahead
                try:
                    driver.find_element(By.XPATH, f"//button[@aria-label=\"{label}\"]").click()
                    time.sleep(2)
                    return True
                except:
                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR,
                                                       'button[aria-label="Move forward to switch to the next month."]')
                        next_btn.click()
                        time.sleep(2)
                    except:
                        break
            return False

        # Try selecting the check-in (Friday)
        if not click_until_date_visible(friday_label):
            print(f"❌ Could not find Friday: {friday_label}")

        # Try selecting the check-out (Saturday)
        if not click_until_date_visible(saturday_label):
            print(f"❌ Could not find Saturday: {saturday_label}")

        search_btn = driver.find_element(By.XPATH, "//button[@data-testid='structured-search-input-search-button']")
        search_btn.click()
        time.sleep(2)

        try:
            heading_element = driver.find_element(By.XPATH, "//section[@aria-live='polite']//h1//span[1]")
            heading_text = heading_element.text
            print(f"Number of places found text: {heading_text}")
        except Exception as e:
            print("Failed to get number of places:", e)

        try:
            filter_btn = driver.find_element(By.XPATH, "//button[@data-testid='category-bar-filter-button']")
            filter_btn.click()
            time.sleep(2)
        except Exception as e:
            print("Failed to open filters:", e)

        time.sleep(2)

        try:
            entire_home_option = driver.find_element(By.XPATH,
                                                     "//div[@role='radio' and @aria-describedby='room-filter-description-Entire home']")
            entire_home_option.click()
            time.sleep(2)
        except Exception as e:
            print("Failed to select 'Entire home' filter:", e)

        api_result = get_network_requests(driver)
        if api_result:
            histogram = \
                api_result['data']['presentation']['staysSearch']['dynamicFilters']['sectionReplacementsByID'][0][
                    'sectionData']['discreteFilterItems'][0]['priceHistogram']
            index = 0
            for i, v in enumerate(histogram):
                if v != 0:
                    index = i + 1
                    break
            print(f"📊 API Response with priceHistogram captured successfully for {guest_count} guests")
        else:
            print(f"⚠️ No API response with priceHistogram captured for {guest_count} guests")

        try:
            max_input = driver.find_element(By.ID, 'price_filter_max').get_attribute('value')
            slider = driver.find_elements(By.XPATH, "//input[@type='range']")[0]
            # Create action chain
            actions = ActionChains(driver)

            # Move the slider by offset
            move = index * 10
            move = 255 - move
            move = move * -1
            actions.click_and_hold(slider).move_by_offset(move, 0).release().perform()
            time.sleep(2)
            min_input = driver.find_element(By.ID, 'price_filter_min').get_attribute('value')

            min_val = int(min_input)
            max_val = int(max_input.replace('+', '')) if '+' in max_input else int(max_input)
            median = (min_val + max_val) // 2

            print(f"Prices -> Min: ${min_val}, Max: ${max_val}, Median: ${median}")
        except Exception as e:
            print("Failed to get prices:", e)

        try:
            driver.find_element(By.XPATH, "//button[@aria-label='Close']").click()
        except:
            pass

        # Use manually set weekends list
        weekend_counts = {}

        for label, checkin_date, checkout_date in weekends:
            print(f"\n🔁 {label}: {checkin_date.date()} → {checkout_date.date()}")

            try:
                # Open calendar
                driver.find_element(By.XPATH, "//button[@data-testid='little-search-date']").click()
                time.sleep(2)

                try:
                    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Clear Input"]').click()
                except:
                    pass

                # Build aria-labels for the current weekend
                checkin_label = build_airbnb_aria_label(checkin_date, "check-in")
                checkout_label = build_airbnb_aria_label(checkout_date, "checkout")

                # Select check-in date
                if not click_until_date_visible(checkin_label):
                    print(f"❌ Could not find check-in: {checkin_label}")

                # Select check-out date
                if not click_until_date_visible(checkout_label):
                    print(f"❌ Could not find check-out: {checkout_label}")

                # Click search
                driver.find_element(By.XPATH, "//button[@data-testid='structured-search-input-search-button']").click()
                print("🔍 Searching...")
                time.sleep(5)

                # Grab listing count
                heading = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="stays-page-heading"]')
                heading_text = heading.text

                import re
                match = re.search(r"Over\s([\d,]+)|([\d,]+)\+?", heading_text)
                if match:
                    number_str = match.group(1) or match.group(2)
                    count = int(number_str.replace(",", ""))
                    weekend_counts[label] = count
                    print(f"✅ {label}: {count} listings")
                else:
                    print(f"❌ Could not extract count for {label}: {heading_text}")
                    weekend_counts[label] = 0

            except Exception as e:
                print(f"❌ Error on {label}: {e}")
                weekend_counts[label] = 0

        # === SAVE RESULTS TO EXCEL ===
        row = {
            "city": city_name,
            "guest": guest_count,
            "total available accommodations": number,
            "low end": min_val,
            "median": median,
            "high end": max_val,
            "1 Month Out": weekend_counts.get("1 Month Out", 0),
            "2 Week Out": weekend_counts.get("2 Week Out", 0),
            "1 Week Out": weekend_counts.get("1 Week Out", 0),
            "This weekend": weekend_counts.get("This weekend", 0),
            "2 Months (15–16)": weekend_counts.get("2 Months (15–16)", 0),
            "3 Months (15–16)": weekend_counts.get("3 Months (15–16)", 0),
            "4 Months (15–16)": weekend_counts.get("4 Months (15–16)", 0),
            "5 Months (15–16)": weekend_counts.get("5 Months (15–16)", 0),
            "6 Months (15–16)": weekend_counts.get("6 Months (15–16)", 0),
            "7 Months (15–16)": weekend_counts.get("7 Months (15–16)", 0),
            "8 Months (15–16)": weekend_counts.get("8 Months (15–16)", 0),
            "9 Months (15–16)": weekend_counts.get("9 Months (15–16)", 0),
            "10 Months (15–16)": weekend_counts.get("10 Months (15–16)", 0),
            "11 Months (15–16)": weekend_counts.get("11 Months (15–16)", 0),
            "12 Months (15–16)": weekend_counts.get("12 Months (15–16)", 0),
        }

        save_result_to_excel(row)

    except Exception as e:
        print("Error during search:", e)


def get_network_requests(driver):
    """
    Capture the latest API response that contains priceHistogram data.
    Returns the API response data or None if not found.
    """
    try:
        print("🔍 Capturing API response with priceHistogram data...")

        # Get performance logs
        logs = driver.get_log('performance')
        print(f"📊 Found {len(logs)} performance log entries")

        # Look for requests with priceHistogram in their response
        price_histogram_requests = []

        for log in logs:
            try:
                message = json.loads(log['message'])
                if 'message' in message and message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url = response.get('url', '')
                    request_id = message['message']['params']['requestId']

                    # Get the response body to check for priceHistogram
                    try:
                        response_body = driver.execute_cdp_cmd('Network.getResponseBody', {
                            'requestId': request_id
                        })

                        if response_body and 'body' in response_body:
                            response_text = response_body['body']
                            if 'priceHistogram' in response_text:
                                price_histogram_requests.append({
                                    'requestId': request_id,
                                    'url': url,
                                    'timestamp': log['timestamp'],
                                    'responseBody': response_text
                                })
                                print(f"🔗 Found request with priceHistogram: {url}")
                    except Exception as e:
                        # Skip if we can't get response body
                        continue

            except (json.JSONDecodeError, KeyError) as e:
                continue

        if not price_histogram_requests:
            print("❌ No requests with priceHistogram data found in performance logs")
            # Print some sample URLs to help debug
            sample_urls = []
            for log in logs[-10:]:  # Last 10 logs
                try:
                    message = json.loads(log['message'])
                    if 'message' in message and message['message']['method'] == 'Network.responseReceived':
                        url = message['message']['params']['response'].get('url', '')
                        if url:
                            sample_urls.append(url)
                except:
                    continue
            if sample_urls:
                print("📋 Sample recent URLs:", sample_urls[:5])
            return None

        # Get the latest request (highest timestamp)
        latest_request = max(price_histogram_requests, key=lambda x: x['timestamp'])
        print(f"🎯 Using latest request with priceHistogram: {latest_request['url']}")

        # Parse the response body
        try:
            api_data = json.loads(latest_request['responseBody'])
            print(f"✅ Successfully captured and parsed API response with priceHistogram")
            print(f"📄 Response keys: {list(api_data.keys()) if isinstance(api_data, dict) else 'Not a dict'}")

            # Verify priceHistogram is present
            if isinstance(api_data, dict) and 'priceHistogram' in str(api_data):
                print("✅ Confirmed priceHistogram data is present in response")
            else:
                print("⚠️ priceHistogram not found in parsed response, but was in raw text")

            return api_data
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse API response as JSON: {e}")
            print(f"📄 Raw response preview: {latest_request['responseBody'][:200]}...")
            return latest_request['responseBody']

    except Exception as e:
        print(f"❌ Error capturing network requests: {e}")
        import traceback
        traceback.print_exc()
        return None
