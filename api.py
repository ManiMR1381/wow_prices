import re
import logging
import os
from flask import Flask, jsonify
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from contextlib import contextmanager
import chromedriver_autoinstaller
import sys

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Install ChromeDriver that matches Chrome version
try:
    chromedriver_autoinstaller.install()
    logger.info("ChromeDriver installed successfully")
except Exception as e:
    logger.error(f"Error installing ChromeDriver: {e}")

@contextmanager
def get_driver():
    """Context manager for browser handling"""
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        logger.info("Creating Chrome driver with options")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        yield driver
    except Exception as e:
        logger.error(f"Error creating Chrome driver: {e}")
        raise
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Chrome driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

def get_usdt_price():
    """Fetch the USDT price from Nobitex API."""
    try:
        url = "https://api.nobitex.ir/v2/orderbook/USDTIRT"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'lastTradePrice' in data:
            price = float(data['lastTradePrice'])
            logger.info(f"USDT price fetched: {price}")
            return price
        logger.warning("No lastTradePrice in Nobitex response")
        return None
    except Exception as e:
        logger.error(f"Error fetching USDT price: {e}")
        return None

def get_best_offer_Tarren():
    """Fetch the best offer from G2G."""
    with get_driver() as driver:
        try:
            url = "https://www.g2g.com/offer/Tarren-Mill--EU----Horde?service_id=lgc_service_1&brand_id=lgc_game_2299&region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_2299_dropdown_17%3Algc_2299_dropdown_17_42127&sort=lowest_price&include_offline=1"
            logger.info(f"Fetching Tarren Mill price from: {url}")
            driver.get(url)
            
            logger.info("Waiting for price element")
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".precheckout__price-card"))
            )
            price_text = price_element.text
            logger.info(f"Price text found: {price_text}")
            
            price_match = re.search(r'\d+\.\d+', price_text)
            if price_match:
                price = float(price_match.group())
                logger.info(f"Tarren Mill price extracted: {price}")
                return price
            logger.warning("No price found in text")
            return None
        except Exception as e:
            logger.error(f"Error fetching Tarren price: {e}")
            return None

def get_best_offer_Kazzak():
    """Fetch the best offer from G2G."""
    with get_driver() as driver:
        try:
            url = "https://www.g2g.com/offer/Kazzak--EU----Horde?service_id=lgc_service_1&brand_id=lgc_game_2299&region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_2299_dropdown_17%3Algc_2299_dropdown_17_41959&sort=lowest_price&include_offline=1"
            logger.info(f"Fetching Kazzak price from: {url}")
            driver.get(url)
            
            logger.info("Waiting for price element")
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".precheckout__price-card"))
            )
            price_text = price_element.text
            logger.info(f"Price text found: {price_text}")
            
            price_match = re.search(r'\d+\.\d+', price_text)
            if price_match:
                price = float(price_match.group())
                logger.info(f"Kazzak price extracted: {price}")
                return price
            logger.warning("No price found in text")
            return None
        except Exception as e:
            logger.error(f"Error fetching Kazzak price: {e}")
            return None

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/health')
def health_check():
    try:
        # Only check API connectivity for health check
        logger.info("Starting health check")
        response = requests.get("https://api.nobitex.ir/v2/status", timeout=5)
        response.raise_for_status()
        logger.info("Health check successful")
        return jsonify({
            "status": "healthy",
            "message": "Service is running"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503

@app.route('/Tarren-Mill', methods=['GET'])
def Tarren():
    try:
        logger.info("Processing Tarren-Mill request...")
        usdt_price = get_usdt_price()
        if usdt_price is None:
            return jsonify({"error": "Failed to fetch USDT price"}), 500
        
        best_offer = get_best_offer_Tarren()
        if best_offer is None:
            return jsonify({"error": "Failed to fetch Tarren-Mill price"}), 500
        
        result = int(best_offer * usdt_price * 0.75 / 10)
        logger.info(f"Tarren-Mill result calculated: {result}")
        return jsonify({"price": result})
    except Exception as e:
        logger.error(f"Error processing Tarren request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/Kazzak', methods=['GET'])
def Kazzak():
    try:
        logger.info("Processing Kazzak request...")
        usdt_price = get_usdt_price()
        if usdt_price is None:
            return jsonify({"error": "Failed to fetch USDT price"}), 500
        
        best_offer = get_best_offer_Kazzak()
        if best_offer is None:
            return jsonify({"error": "Failed to fetch Kazzak price"}), 500
        
        result = int(best_offer * usdt_price * 0.75 / 10)
        logger.info(f"Kazzak result calculated: {result}")
        return jsonify({"price": result})
    except Exception as e:
        logger.error(f"Error processing Kazzak request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
