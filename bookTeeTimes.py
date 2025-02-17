import sys
import subprocess
import pickle
import time
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from html import unescape

def wait_until_precise_7am():
    """Wait until exactly 7:00:00.000 AM with millisecond precision."""
    now = datetime.now()
    target_time = now.replace(hour=22, minute=5, second=0, microsecond=0)
    
    # If it's past 7 AM, wait for the next day's 7 AM
    if now >= target_time:
        target_time = target_time.replace(day=now.day + 1)

    seconds_until_target = (target_time - now).total_seconds()

    print(f"Waiting {seconds_until_target:.6f} seconds until 7:00:00 AM...")

    # Sleep until ~0.1s before target, then do a precise busy-wait
    time.sleep(max(0, seconds_until_target - 0.1))  

    # Busy-wait the last 100ms for max precision
    while datetime.now() < target_time:
        pass  

def click_add_to_cart(session, add_to_cart_url, cookies):
    """Simulate clicking the 'Add to Cart' button using the cookies from Selenium."""
    # Add cookies to the Requests session before making the request
    print("this should match", cookies)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    
    response = session.get(add_to_cart_url)
    
    if response.ok:
        print(f"Successfully added to cart from {add_to_cart_url}")
        soup = BeautifulSoup(response.content, 'html.parser')
        print("HTML content:", soup)
    else:
        print(f"Failed to add to cart from {add_to_cart_url}")


def remove_cron_job(course, day, min_time, max_time, players):
    # Recreate the cron command from the input parameters
    cron_command = f"python3 /home/teetimesuser/bookTeeTimes/bookTeeTimes.py '{course}' '{day}' '{min_time}' '{max_time}' '{players}'"

    # Build the cron timing part (the part that specifies when the cron job should run)
    # This should match the cron job timing used when adding the job.
    cron_hour = 7  # Fixed to 7:00 AM
    cron_minute = 0  # Fixed to 0 minute
    cron_day = int(day.split('-')[2])  # Extract the day from the date (YYYY-MM-DD)
    cron_month = int(day.split('-')[1])  # Extract the month from the date (YYYY-MM-DD)

    # Full cron timing
    cron_timing = f"{cron_minute} {cron_hour} {cron_day} {cron_month} *"
    
    # Full cron job entry to search for (timing + command)
    cron_job = f"{cron_timing} {cron_command}"

    # Get the current crontab
    try:
        result = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        current_cron = result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print("Error reading crontab.")
        return

    # Check if the specific cron job exists
    if cron_job in current_cron:
        # Remove the matching cron job
        new_cron = "\n".join([line for line in current_cron.splitlines() if cron_job not in line])
        
        # Update the crontab
        try:
            subprocess.run(
                f"echo \"{new_cron}\" | crontab -",
                shell=True,
                check=True
            )
            print(f"Cron job removed successfully:\n{cron_job}")
        except subprocess.CalledProcessError as e:
            print(f"Error removing cron job: {e}")
    else:
        print("Cron job not found!")

def use_selenium_with_cookies(min_time, max_time, players, day, numTeeTimes):
    """Make requests using the cookies from Selenium."""
    
    # Set up WebDriver options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Opening the login page...")
        driver.get("https://sccharlestonweb.myvscloud.com/webtrac/web/splash.html?InterfaceParameter=WebTrac_Golf")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Find and click the login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'login.html')]"))
        )
        login_button.click()
        print("✅ Login button clicked!")

        # Enter username and password
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'weblogin_username')))
        driver.find_element(By.ID, 'weblogin_username').send_keys('priedejm')
        driver.find_element(By.ID, 'weblogin_password').send_keys('123Qweasdhuyter4!')

        # Click login button
        driver.find_element(By.ID, 'weblogin_buttonlogin').click()
        print("✅ Logged in successfully!")

        # Wait for Tee Times page and click the second button
        tee_time_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//a[contains(@href, 'search.html') and contains(@class, 'tile')])[2]"))
        )
        tee_time_button.click()
        print("✅ Tee Times button clicked!")

        # Modify URL
        current_url = driver.current_url
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        formatted_day = datetime.strptime(day, "%Y-%m-%d").strftime("%m/%d/%Y")
        formatted_time = datetime.strptime(min_time, "%I:%M%p").strftime("%-I:%M%p").upper()

        query_params.update({
            "Action": ["Start"],
            "numberofplayers": [players],
            "begindate": [formatted_day],
            "begintime": [formatted_time],
            "numberofholes": ["18"],
            "display": ["Detail"],
            "grwebsearch_buttonsearch": ["yes"]
        })

        new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, urlencode(query_params, doseq=True), parsed_url.fragment))
        wait_until_precise_7am()
        driver.get(new_url)
        print("✅ Navigated to modified search page!")

        # Click Search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "grwebsearch_buttonsearch"))
        )
        search_button.click()
        print("✅ Search button clicked!")

        # Parse available tee times
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.select("tbody tr")
        print(f"Total tee times found: {len(rows)}")
        print("Found: ", rows)

        min_time = datetime.strptime(f"{day} {min_time.strip().upper()}", "%Y-%m-%d %I:%M%p")
        max_time = datetime.strptime(f"{day} {max_time.strip().upper()}", "%Y-%m-%d %I:%M%p")

        tee_times = []

        for row in rows:
            cells = row.find_all('td', class_='label-cell')
            if len(cells) < 5:
                continue

            time_str = cells[0].get_text(strip=True).strip().upper().replace(" ", "")
            try:
                tee_time = datetime.strptime(f"{day} {time_str}", "%Y-%m-%d %I:%M%p")
            except ValueError:
                continue  # Skip invalid time formats

            open_slots = cells[4].get_text(strip=True)
            try:
                open_slots_int = int(open_slots)
            except ValueError:
                continue  # Skip invalid slots

            if min_time <= tee_time <= max_time and open_slots_int <= int(players):
                cart_button = row.find('a', class_='cart-button')
                add_to_cart_url = cart_button['href'] if cart_button else 'N/A'

                tee_times.append({
                    'Time': time_str,
                    'Open Slots': open_slots,
                    'Add to Cart URL': add_to_cart_url
                })

        if not tee_times:
            print("❌ No matching tee times found within the specified range.")
            return

        print("✅ Found matching tee times!")

        # Add first tee time to cart
        driver.get(tee_times[0]['Add to Cart URL'])
        print(f"✅ Added to cart: {tee_times[0]['Time']}")

        # Click "Continue" on player selection
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "golfmemberselection_buttoncontinue"))
        )
        continue_button.click()
        print("✅ Clicked continue on player selection page!")

        # Click "Continue" on payment page
        payment_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "processingprompts_buttononeclicktofinish"))
        )
        payment_button.click()
        print("✅ Clicked continue on payment page!")

        # Logout
        logout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "webconfirmation_buttonlogout"))
        )
        logout_button.click()
        print("✅ Logged out successfully!")

    except Exception as e:
        print("❌ Unexpected error:", e)

    finally:
        driver.quit()


def main(): 
    """Main function to handle login, data fetching, and cron job removal."""
    if len(sys.argv) != 7:
        print("Usage: python3 bookTeeTimes.py <course> <day> <minTime> <maxTime> <players> <numTeeTimes>")
        sys.exit(1)

    course, day, min_time, max_time, players, numTeeTimes = sys.argv[1:7]

    print(f"Course: {course}")
    print(f"Day: {day}")
    print(f"Min Time: {min_time}")
    print(f"Max Time: {max_time}")
    print(f"Players: {players}")

    if course == "Charleston Municipal":
        print("Start scraping...")
        # Use the Selenium session for login and scraping
        use_selenium_with_cookies(min_time, max_time, players, day, numTeeTimes)

    remove_cron_job(course, day, min_time, max_time, players)

if __name__ == "__main__":
    main()
