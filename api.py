import re
import logging
from flask import Flask, jsonify, send_from_directory
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import os
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache results for 5 minutes
@lru_cache(maxsize=128)
def cache_key():
    now = datetime.now()
    return now.replace(second=now.second // 300 * 300, microsecond=0)

def get_with_cache(func, *args, **kwargs):
    key = cache_key()
    return func(*args, **kwargs)

def create_browser(playwright):
    """Create a browser instance with optimized settings."""
    return playwright.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-extensions',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-component-extensions-with-background-pages',
            '--disable-features=TranslateUI,BlinkGenPropertyTrees',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--enable-automation',
            '--memory-pressure-off',
            '--no-default-browser-check',
        ]
    )

@app.route('/favicon.ico')
def favicon():
    return '', 204

# ... [rest of your existing functions] ...

@app.route('/Tarren-Mill', methods=['GET'])
def Tarren():
    try:
        logger.info("Processing Tarren-Mill request...")
        
        # Use cached results if available
        @get_with_cache
        def fetch_prices():
            with sync_playwright() as playwright:
                usdt_price = get_usdt_price(playwright)
                if usdt_price is None:
                    raise Exception("Failed to fetch USDT price")
                
                best_offer = get_best_offer_Tarren(playwright)
                if best_offer is None:
                    raise Exception("Failed to fetch Tarren-Mill price")
                
                return usdt_price, best_offer

        try:
            usdt_price, best_offer = fetch_prices()
            result = int(best_offer * usdt_price * 0.75)
            logger.info(f"Tarren-Mill result calculated: {result}")
            return jsonify({"Tarren-Mill": result})
        except Exception as e:
            logger.error(f"Error in price calculation: {e}")
            return jsonify({"error": str(e)}), 500

    except Exception as e:
        logger.error(f"Error processing Tarren-Mill request: {e}")
        return jsonify({"error": str(e)}), 500

# Update Kazzak route similarly...

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Changed default port to 8080
    app.run(host='0.0.0.0', port=port)
