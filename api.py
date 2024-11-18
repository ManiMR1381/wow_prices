import re
import logging
from flask import Flask, jsonify, send_from_directory
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return a 204 No Content response for favicon requests

def remove_commas(number_str):
    """Remove commas and convert to an integer."""
    try:
        return int(number_str.replace(',', ''))
    except (ValueError, AttributeError) as e:
        logger.error(f"Error converting number: {e}")
        return None

def extract_price(input_str):
    """Extract the first floating-point number from a string."""
    try:
        match = re.search(r"\d+\.\d+", input_str)
        return float(match.group()) if match else None
    except (AttributeError, ValueError) as e:
        logger.error(f"Error extracting price: {e}")
        return None

def get_usdt_price(playwright):
    """Fetch the USDT price from Nobitex."""
    browser = None
    try:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(30000)  # 30 seconds timeout
        
        logger.info("Fetching USDT price from Nobitex...")
        page.goto("https://nobitex.ir/panel/exchange/usdt-irt")
        price = page.locator(
            "#nobitex-panel > div > div.nobitex-panel__main.sidebar-is-minimize > "
            "div.nobitex-panel__main--nuxt > div.mb-40 > div.max-w-1730px.mx-auto > "
            "div.exchange.d-flex.flex-column.text-aligned.pb-8.pb-32-md > "
            "div.exchange__main.d-flex.mx-8-md.mx-8-lg.mx-8-xl > "
            "div.exchange__main--overview.d-flex.flex-column-reverse.flex-xl-row.w-100.ml-8-multi-md.ml-8-multi-xl > "
            "div.exchange-order-list.mr-8-multi-md.position-relative.custom-scroll-bar.w-100.card-box > "
            "div:nth-child(2) > div > div.exchange-table-container__tables > div:nth-child(3) > "
            "div.exchange-table.mb-0.h-100 > div > div:nth-child(10) > div.item-price.exchange-table__row--column.px-8.flex-1.text-right.fs-15.fw-bold.py-1.text-success"
        ).inner_text()
        logger.info(f"USDT price fetched: {price}")
        return remove_commas(price)
    except PlaywrightTimeout as e:
        logger.error(f"Timeout error fetching USDT price: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching USDT price: {e}")
        return None
    finally:
        if browser:
            browser.close()

def get_best_offer_Tarren(playwright):
    """Fetch the best offer from G2G."""
    browser = None
    try:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(30000)  # 30 seconds timeout
        
        logger.info("Fetching Tarren Mill price from G2G...")
        page.goto(
            "https://www.g2g.com/offer/Tarren-Mill--EU----Horde?service_id=lgc_service_1&brand_id=lgc_game_2299"
            "&region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_2299_dropdown_17%3Algc_2299_dropdown_17_42127"
            "&sort=lowest_price&include_offline=1"
        )
        best_offer = page.locator(".precheckout__price-card").inner_text()
        logger.info(f"Tarren Mill price fetched: {best_offer}")
        return extract_price(best_offer)
    except PlaywrightTimeout as e:
        logger.error(f"Timeout error fetching Tarren price: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching Tarren price: {e}")
        return None
    finally:
        if browser:
            browser.close()

def get_best_offer_Kazzak(playwright):
    """Fetch the best offer from G2G."""
    browser = None
    try:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(30000)  # 30 seconds timeout
        
        logger.info("Fetching Kazzak price from G2G...")
        page.goto(
            "https://www.g2g.com/offer/Kazzak--EU----Horde?service_id=lgc_service_1&brand_id=lgc_game_2299"
            "&region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_2299_dropdown_17%3Algc_2299_dropdown_17_41959"
            "&sort=lowest_price&include_offline=1"
        )
        best_offer = page.locator(".precheckout__price-card").inner_text()
        logger.info(f"Kazzak price fetched: {best_offer}")
        return extract_price(best_offer)
    except PlaywrightTimeout as e:
        logger.error(f"Timeout error fetching Kazzak price: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching Kazzak price: {e}")
        return None
    finally:
        if browser:
            browser.close()

@app.route('/Tarren-Mill', methods=['GET'])
def Tarren():
    try:
        logger.info("Processing Tarren-Mill request...")
        with sync_playwright() as playwright:
            usdt_price = get_usdt_price(playwright)
            if usdt_price is None:
                return jsonify({"error": "Failed to fetch USDT price"}), 500
            
            best_offer = get_best_offer_Tarren(playwright)
            if best_offer is None:
                return jsonify({"error": "Failed to fetch Tarren-Mill price"}), 500
            
            result = int(best_offer * usdt_price * 0.75)
            logger.info(f"Tarren-Mill result calculated: {result}")
            return jsonify({"Tarren-Mill": result})
    except Exception as e:
        logger.error(f"Error processing Tarren-Mill request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/Kazzak', methods=['GET'])
def Kazzak():
    try:
        logger.info("Processing Kazzak request...")
        with sync_playwright() as playwright:
            usdt_price = get_usdt_price(playwright)
            if usdt_price is None:
                return jsonify({"error": "Failed to fetch USDT price"}), 500
            
            best_offer = get_best_offer_Kazzak(playwright)
            if best_offer is None:
                return jsonify({"error": "Failed to fetch Kazzak price"}), 500
            
            result = int(best_offer * usdt_price * 0.75)
            logger.info(f"Kazzak result calculated: {result}")
            return jsonify({"Kazzak": result})
    except Exception as e:
        logger.error(f"Error processing Kazzak request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
