import time
import random
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CSV_FILENAME = "sp500_transcripts_history_part_2.csv"
TARGET_YEARS = ["2025", "2024", "2023"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]

MODE = "MARATHON" 

SPEED_PROFILES = {
    "FAST": {
        "google_search": (2, 3),
        "page_load": (3, 5),
        "inter_request": (5, 8)
    },
    "MARATHON": {
        "google_search": (4, 7),
        "page_load": (5, 10),
        "inter_request": (15, 35)
    }
}

DELAYS = SPEED_PROFILES[MODE]

COMPANIES = [
    "RTX (RTX)",
    "Northrop Grumman (NOC)",
    "General Dynamics (GD)",
    "L3Harris (LHX)",
    "TransDigm (TDG)",
    "Howmet Aerospace (HWM)",
    "Textron (TXT)",
    "Huntington Ingalls (HII)",
    "Axon Enterprise (AXON)",
    "UPS (UPS)",
    "FedEx (FDX)",
    "Union Pacific (UNP)",
    "CSX (CSX)",
    "Norfolk Southern (NSC)",
    "Old Dominion Freight (ODFL)",
    "J.B. Hunt (JBHT)",
    "C.H. Robinson (CHRW)",
    "Expeditors (EXPD)",
    "Delta Air Lines (DAL)",
    "United Airlines (UAL)",
    "Southwest Airlines (LUV)",
    "Deere (DE)",
    "Cummins (CMI)",
    "PACCAR (PCAR)",
    "Wabtec (WAB)",
    "Parker-Hannifin (PH)",
    "Otis (OTIS)",
    "Carrier Global (CARR)",
    "Johnson Controls (JCI)",
    "Trane Technologies (TT)",
    "Rockwell Automation (ROK)",
    "Dover (DOV)",
    "Ingersoll Rand (IR)",
    "Xylem (XYL)",
    "Fortive (FTV)",
    "Stanley Black & Decker (SWK)",
    "Snap-on (SNA)",
    "Nordson (NDSN)",
    "Vulcan Materials (VMC)",
    "Martin Marietta (MLM)",
    "Quanta Services (PWR)",
    "Jacobs Solutions (J)",
    "United Rentals (URI)",
    "Builders FirstSource (BLDR)",
    "3M (MMM)",
    "Eaton (ETN)",
    "Emerson Electric (EMR)",
    "Waste Management (WM)",
    "Republic Services (RSG)",
    "Cintas (CTAS)",
    "Fastenal (FAST)",
    "W.W. Grainger (GWW)",
    "Verisk Analytics (VRSK)"
]

def setup_driver():
    """
    Configures and initializes the Chrome WebDriver.
    Implements stealth options (disabling automation flags, masking user-agent) to bypass basic bot detection.
    Returns the configured WebDriver instance.
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    current_folder = os.getcwd()
    if os.name == 'nt': 
        driver_filename = "chromedriver.exe"
    else: 
        driver_filename = "chromedriver"
    driver_path = os.path.join(current_folder, driver_filename)
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"Driver manquant : {driver_path}")
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)

def human_scroll(driver):
    """
    Simulates human-like scrolling behavior on the webpage.
    Scrolls down dynamically in increments and slightly back up to prevent the script from being flagged as a bot.
    """
    print("[SCROLL] Défilement...")
    try:
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        for i in range(1, 4):
            driver.execute_script(f"window.scrollTo(0, {total_height * i / 4});")
            time.sleep(random.uniform(0.5, 1.2))
        driver.execute_script("window.scrollBy(0, -300);")
        time.sleep(1)
    except: 
        pass

def close_marketing_popup(driver):
    """
    Detects and attempts to automatically dismiss intrusive marketing pop-ups or cookie consent banners.
    Iterates through a list of common CSS selectors for close buttons.
    Returns True if a popup was closed, False otherwise.
    """
    try:
        time.sleep(1.5)
        selectors = [
            "button[aria-label='Close']", "button[class*='close']", 
            "div[class*='modal'] button", "svg[data-icon='times']", 
            ".inf-close-icon", "button#onetrust-close-btn-handler"
        ]
        for selector in selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.5)
                    return True
            except: 
                continue
    except: 
        pass
    return False

def check_for_captcha(driver):
    """
    Identifies Google (Unusual Traffic) or Cloudflare CAPTCHA challenges.
    Pauses the execution loop to allow manual resolution by the user if a block is detected.
    Returns True if a CAPTCHA was found, False otherwise.
    """
    try:
        page_source = driver.page_source.lower()
        page_title = driver.title.lower()
        google_triggers = ["trafic exceptionnel", "unusual traffic", "nos systèmes ont détecté", "id=\"captcha-form\"", "g-recaptcha"]
        if "google" in driver.current_url and any(trigger in page_source for trigger in google_triggers):
             if "id=\"search\"" not in page_source and "class=\"g\"" not in page_source:
                print("\n" + "!"*60 + "\n[ALERTE] BLOCAGE GOOGLE DÉTECTÉ (Trafic Exceptionnel)\n" + "!"*60)
                print('\a') 
                input(">>> Résolvez le CAPTCHA, attendez les résultats, puis appuyez sur ENTREE <<<")
                time.sleep(5)
                return True
        cloudflare_triggers = ["just a moment", "attention required", "security check", "access denied", "verify you are human"]
        if any(x in page_title for x in cloudflare_triggers):
            print("\n[ALERTE] Captcha Site Web détecté.")
            input(">>> Résolvez le CAPTCHA puis appuyez sur ENTREE <<<")
            time.sleep(2)
            return True
        h1s = [h.text.lower() for h in driver.find_elements(By.TAG_NAME, "h1")]
        if any("challenge" in h or "turnstile" in h for h in h1s):
            print("\n[ALERTE] Captcha détecté (H1)")
            input(">>> Résolvez le CAPTCHA puis appuyez sur ENTREE <<<")
            return True
    except Exception: 
        pass
    return False

def extract_ticker(company_string):
    """
    Parses the provided company string and extracts the exact stock ticker symbol.
    Example: 'Apple Inc. (AAPL)' becomes 'AAPL'.
    """
    try:
        return company_string.split('(')[1].replace(')', '').strip()
    except IndexError:
        return company_string.strip()

def load_existing_data():
    """
    Loads previously scraped data from the output CSV file.
    Generates unique identifier keys (Ticker_Year_Quarter) to prevent duplicate processing.
    Returns the existing records and a set of completed task keys.
    """
    if os.path.exists(CSV_FILENAME):
        try:
            df = pd.read_csv(CSV_FILENAME)
            if df.empty: 
                return [], set()
            records = df.to_dict('records')
            done_set = set()
            for row in records:
                ticker_in_csv = extract_ticker(row['company'])
                key = f"{ticker_in_csv}_{row['year']}_{row['quarter']}"
                done_set.add(key)
            print(f"[INFO] Historique chargé : {len(records)} entrées (Basé sur Tickers).")
            return records, done_set
        except Exception as e:
            print(f"[WARN] Erreur chargement CSV: {e}")
            return [], set()
    return [], set()

def save_data_safely(data):
    """
    Writes the newly scraped data to the dataset via a temporary file.
    Ensures data integrity and prevents file corruption if the script crashes during the save process.
    """
    temp = CSV_FILENAME + ".tmp"
    try:
        df = pd.DataFrame(data)
        df.to_csv(temp, index=False)
        os.replace(temp, CSV_FILENAME)
    except Exception as e:
        print(f"[ERREUR SAVE] {e}")

def google_search_quarter_fool(driver, company_full_name, quarter, year):
    """
    Executes a targeted Google search to find the Motley Fool earnings call transcript URL.
    Uses exact search operators and filters results based on the company name, ticker, quarter, and year.
    Returns a list containing the best matching result dict.
    """
    search_name = company_full_name.split('(')[0].strip()
    search_name = search_name.replace(".com", "").replace(" Group", "").strip()
    ticker = extract_ticker(company_full_name)
    query = f'site:fool.com {search_name} {quarter} {year} "Earnings Call Transcript"'
    print(f"[RECHERCHE] {search_name} ({ticker}) {quarter} {year}...")
    try:
        driver.get("https://www.google.com")
        time.sleep(random.uniform(*DELAYS['google_search']))
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if "tout accepter" in btn.text.lower() or "accept all" in btn.text.lower():
                    driver.execute_script("arguments[0].click();", btn)
                    break
        except: 
            pass
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(*DELAYS['google_search']))
        if check_for_captcha(driver):
            print("[INFO] Reprise après résolution Captcha...")
            time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links_found = []
        for h3 in soup.find_all('h3'):
            link_tag = h3.find_parent('a')
            if link_tag and 'href' in link_tag.attrs:
                url = link_tag['href']
                title = h3.get_text()
                if "fool.com" not in url: 
                    continue
                if "transcript" not in title.lower(): 
                    continue
                if quarter.lower() not in title.lower(): 
                    continue
                if str(year) not in title: 
                    continue
                if ticker.lower() not in title.lower() and search_name.lower() not in title.lower():
                    continue
                links_found.append({
                    "company": company_full_name,
                    "quarter": quarter,
                    "year": year,
                    "title": title,
                    "url": url
                })
        return links_found[:1]
    except Exception as e:
        print(f"[ERREUR GOOGLE] {e}")
        return []

def extract_content_fool(driver, url):
    """
    Navigates to the targeted transcript URL and extracts the main text content.
    Strips away embedded videos, styling, tracking scripts, and generic disclaimer text to ensure clean data.
    Returns the cleaned transcript string, or None if extraction fails.
    """
    try:
        driver.get(url)
        time.sleep(random.uniform(*DELAYS['page_load']))
        try:
            driver.execute_script("""
                var videos = document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"], .video-player');
                videos.forEach(function(v) { v.remove(); });
            """)
        except: 
            pass
        human_scroll(driver)
        check_for_captcha(driver)
        try: 
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except: 
            pass
        close_marketing_popup(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content = soup.find('div', id='article-body-transcript')
        if not content: 
            content = soup.find('div', class_='article-body')
        if content:
            for el in content.find_all(string=lambda t: t and "Image source:" in t): 
                el.extract()
            for tag in content.select(".ticker-widget, .promo, script, style, .video-container"):
                tag.decompose()
            full_text = content.get_text(separator="\n", strip=True)
            if "Should you invest" in full_text: 
                full_text = full_text.split("Should you invest")[0]
            return full_text
    except Exception as e:
        print(f"[EXTRACT ERROR] {e}")
    return None

def main():
    """
    The primary execution loop.
    Iterates through defined years, companies, and quarters, orchestrates the scraping process, checks for existing data, and saves results iteratively while managing random delays to avoid IP bans.
    """
    print(f"--- Scraping S&P 500 (Mode: {MODE} - ID: Ticker) ---")
    all_data, done_set = load_existing_data()
    driver = setup_driver()
    try:
        for year in TARGET_YEARS:
            print(f"\n>>> TRAITEMENT ANNÉE : {year} <<<\n")
            for company in COMPANIES:
                current_ticker = extract_ticker(company)
                for quarter in QUARTERS:
                    task_key = f"{current_ticker}_{year}_{quarter}"
                    if task_key in done_set: 
                        continue 
                    results = google_search_quarter_fool(driver, company, quarter, year)
                    if not results:
                        print(f"[SKIP] Introuvable : {company} {quarter} {year}")
                        time.sleep(1)
                        continue
                    item = results[0]
                    text = extract_content_fool(driver, item['url'])
                    if text and len(text) > 2000:
                        item['content'] = text
                        all_data.append(item)
                        done_set.add(task_key)
                        save_data_safely(all_data)
                        print(f"[OK] {company} {quarter} {year} ({len(text)} cars).")
                    else:
                        print(f"[WARN] Contenu vide/court : {item['title']}")
                    delay_min, delay_max = DELAYS['inter_request']
                    sleep_time = random.uniform(delay_min, delay_max)
                    print(f"   ... Pause de sécurité de {int(sleep_time)}s ...")
                    time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n[STOP] Arrêt manuel. Données sauvegardées.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()