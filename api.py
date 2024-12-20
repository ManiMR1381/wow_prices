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
import sys
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def verify_chrome_setup():
    """Verify Chrome and ChromeDriver are properly set up"""
    chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    
    logger.info(f"Chrome binary location: {chrome_bin}")
    logger.info(f"ChromeDriver path: {chromedriver_path}")
    logger.info(f"DISPLAY environment: {os.environ.get('DISPLAY', 'not set')}")
    
    if not os.path.exists(chrome_bin):
        logger.error(f"Chrome binary not found at {chrome_bin}")
        return False
        
    if not os.path.exists(chromedriver_path):
        logger.error(f"ChromeDriver not found at {chromedriver_path}")
        return False
    
    return True

@contextmanager
def get_driver():
    """Context manager for browser handling"""
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--window-size=1280,1024')
        chrome_options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
        
        service = Service(executable_path=os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver'))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        yield driver
    except Exception as e:
        logger.error(f"Error creating Chrome driver: {e}")
        raise
    finally:
        if driver:
            try:
                driver.quit()
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
    """Health check that verifies Chrome setup"""
    try:
        if not verify_chrome_setup():
            logger.error("Chrome setup verification failed")
            return jsonify({
                "status": "unhealthy",
                "message": "Chrome setup verification failed"
            }), 500
            
        # Try to create a test driver
        with get_driver() as driver:
            # Test navigation to a simple page
            driver.get("about:blank")
            logger.info("Successfully created test Chrome driver")
            return jsonify({
                "status": "healthy",
                "message": "Service is running with Chrome properly configured"
            }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "message": str(e)
        }), 500

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

# Startup verification
logger.info("Starting Beauty World Price Scraper API")
if not verify_chrome_setup():
    logger.error("Failed to verify Chrome setup at startup")
    sys.exit(1)
logger.info("Chrome setup verified successfully")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
