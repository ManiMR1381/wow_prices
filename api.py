import re
from flask import Flask, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def remove_commas(number_str):
    """Remove commas and convert to an integer."""
    return int(number_str.replace(',', ''))

def extract_price(input_str):
    """Extract the first floating-point number from a string."""
    match = re.search(r"\d+\.\d+", input_str)
    return float(match.group()) if match else None

def get_usdt_price(playwright):
    """Fetch the USDT price from Nobitex."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
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
    context.close()
    browser.close()
    return remove_commas(price)

def get_best_offer_Tarren(playwright):
    """Fetch the best offer from G2G."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(
        "https://www.g2g.com/offer/Tarren-Mill--EU----Horde?service_id=lgc_service_1&brand_id=lgc_game_2299"
        "&region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_2299_dropdown_17%3Algc_2299_dropdown_17_42127"
        "&sort=lowest_price&include_offline=1"
    )
    best_offer = page.locator(".precheckout__price-card").inner_text()
    context.close()
    browser.close()
    return extract_price(best_offer)

def get_best_offer_Kazzak(playwright):
    """Fetch the best offer from G2G."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(
        "https://www.g2g.com/offer/Kazzak--EU----Horde?service_id=lgc_service_1&brand_id=lgc_game_2299&region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_2299_dropdown_17%3Algc_2299_dropdown_17_41959&sort=lowest_price&include_offline=1"
    )
    best_offer = page.locator(".precheckout__price-card").inner_text()
    context.close()
    browser.close()
    return extract_price(best_offer)

@app.route('/Tarren-Mill', methods=['GET'])
def Tarren():
    with sync_playwright() as playwright:
        usdt_price = get_usdt_price(playwright)
        best_offer = get_best_offer_Tarren(playwright)
        result = int(best_offer * usdt_price * 0.75)
    return jsonify({"Tarren-Mill": result})

@app.route('/Kazzak', methods=['GET'])
def Kazzak():
    with sync_playwright() as playwright:
        usdt_price = get_usdt_price(playwright)
        best_offer = get_best_offer_Kazzak(playwright)
        result = int(best_offer * usdt_price * 0.75)
    return jsonify({"Kazzak": result})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
