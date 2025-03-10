from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import sys
import os

def setup_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("Initierar Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome initierad framgångsrikt")
        return driver
    except Exception as e:
        print(f"Fel vid setup av Chrome driver: {str(e)}")
        print("Kontrollera att Chrome är installerat och uppdaterat")
        sys.exit(1)

def scroll_and_load_more(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_attempts = 10
    
    while scroll_attempts < max_attempts:
        # Scrolla till botten
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Ökar väntetiden
        
        try:
            # Prova olika selektorer för att hitta knappen
            selectors = [
                "[data-testid='load-more-btn']",  # Uppdaterad korrekt selektor
                "button[data-testid='load-more-btn']",  # Alternativ med button-element
                ".hxUVHi.cjzTBv",  # CSS klasser från knappen
                "button.hxUVHi.cjzTBv"  # Kombinerad selektor med element och klasser
            ]
            
            load_more_button = None
            for selector in selectors:
                print(f"Försöker hitta knappen med selector: {selector}")
                try:
                    load_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if load_more_button:
                        print(f"Hittade knappen med selector: {selector}")
                        break
                except:
                    continue
            
            if load_more_button:
                # Scrolla knappen into view
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)
                
                # Försök klicka med JavaScript om vanlig klickning inte fungerar
                try:
                    load_more_button.click()
                except:
                    driver.execute_script("arguments[0].click();", load_more_button)
                    
                print("Klickade på 'Visa mer'")
                time.sleep(3)
            else:
                print("Kunde inte hitta 'Visa mer' knappen med någon selector")
                break
                
        except Exception as e:
            print(f"Fel vid hantering av 'Visa mer' knappen: {str(e)}")
            # Kontrollera om vi nått botten
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Nådde botten av sidan")
                break
            last_height = new_height
        
        scroll_attempts += 1
        print(f"Scroll-försök {scroll_attempts}/{max_attempts}")
        
    # Vänta lite extra efter all scrollning
    time.sleep(5)

def extract_products(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # Hitta alla produktkort med korrekt data-testid
    product_cards = soup.find_all("div", {"data-testid": "product"})
    print(f"Hittade {len(product_cards)} produktkort")
    
    for card in product_cards:
        try:
            # Extrahera produktnamn
            name_element = card.find("div", class_="iKFOfw")
            if not name_element:
                print("Hittade inget produktnamn i kortet")
                continue
            
            name = name_element.text.strip()
            
            # Extrahera varumärke/storlek
            brand_element = card.find("span", class_="jzGKY")
            brand = brand_element.text.strip() if brand_element else ""
            
            # Kombinera namn och varumärke
            full_name = f"{name} - {brand}" if brand else name
            print(f"Hittade produkt: {full_name}")
            
            # Hitta kampanjformat (t.ex. "3 för")
            campaign_element = card.find("div", class_="hqMUdY")
            campaign_text = campaign_element.text.strip() if campaign_element else ""
            
            # Hitta prisinformation
            price_container = card.find("div", {"data-testid": "product-price"})
            price = ""
            if price_container:
                # Försök hitta priset i den nya strukturen
                price_parts = price_container.find_all("span", class_=["cCZiOx", "ggAScU"])
                if price_parts:
                    # Samla alla siffror från prisdelen
                    price_digits = "".join(part.text.strip() for part in price_parts)
                    # Konvertera till float och formatera med två decimaler
                    try:
                        price_float = float(price_digits) / 100  # Dela med 100 för att få rätt decimaler
                        price = f"{price_float:.2f}".replace(".", ",")
                        print(f"Pris för {full_name}: {price}")
                    except ValueError:
                        print(f"Kunde inte konvertera pris för {full_name}")
            
            # Hitta jämförpris
            compare_price_element = card.find("div", class_="kTSKTN")
            compare_price = compare_price_element.text.strip() if compare_price_element else ""
            if compare_price:
                print(f"Jämförpris för {full_name}: {compare_price}")
            
            # Lägg till produkten i listan med separat kampanjinformation
            products.append({
                "name": full_name,
                "price": price,
                "campaign": campaign_text,
                "compare_price": compare_price
            })
            
        except Exception as e:
            print(f"Fel vid extraktion av produkt: {e}")
            continue
    
    return products

def save_to_markdown(products):
    filename = "willys.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Willys Erbjudanden {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        for product in products:
            f.write(f"## {product['name']}\n")
            if product['campaign']:
                f.write(f"- Erbjudande: {product['campaign']}\n")
            f.write(f"- Pris: {product['price']} kr\n")
            if product['compare_price']:
                f.write(f"- Jämförpris: {product['compare_price']}\n")
            f.write("\n")
    
    print(f"Sparade erbjudanden till {filename}")
    return filename

def main():
    print("Startar scraping av Willys erbjudanden...")
    
    try:
        driver = setup_driver()
        print("Chrome driver initierad framgångsrikt")
        
        # Öppna Willys erbjudandesida
        driver.get("https://www.willys.se/erbjudanden/ehandel")
        time.sleep(5)  # Vänta på att sidan ska laddas helt
        
        # Acceptera cookies om popup finns
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("Cookie popup hanterad")
        except Exception as e:
            print(f"Kunde inte hantera cookie popup: {str(e)}")
        
        print("Scrollar och laddar fler produkter...")
        scroll_and_load_more(driver)
        
        print("Extraherar produktinformation...")
        products = extract_products(driver.page_source)
        
        if not products:
            print("Varning: Inga produkter hittades. Detta kan tyda på ett problem med scrapingen.")
        else:
            print(f"Hittade {len(products)} produkter med erbjudanden")
            filename = save_to_markdown(products)
            print(f"Sparade erbjudanden till {filename}")
        
    except Exception as e:
        print(f"Ett oväntat fel uppstod: {str(e)}")
        raise
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main() 