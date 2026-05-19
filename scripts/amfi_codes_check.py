import requests

def validate_scheme(code, expected_keywords):
    url = f"https://api.mfapi.in/mf/{code}"

    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return False, "INVALID_CODE"

        name = res.json()["meta"]["scheme_name"].lower()

        for kw in expected_keywords:
            if kw not in name:
                return False, name

        return True, name

    except Exception as e:
        return False, str(e)

INDEX_REGISTRY = {

"INDEX_NIFTY_50": ("ICICI Prudential Nifty 50 Index Fund Direct Growth", "120620"),
"INDEX_NIFTY_NEXT_50": ("ICICI Prudential Nifty Next 50 Index Fund Direct Growth", "120684"),


"INDEX_NIFTY_100": ("Axis Nifty 100 Index Fund - Direct Plan ", "147666"),

"INDEX_NIFTY_500": ("ICICI Prudential Nifty 500 Index Fund Direct Growth", "153161"),

"INDEX_MIDCAP_150": ("ICICI Prudential Nifty Midcap 150 Index Fund Direct Growth", "149389"),
"INDEX_SMALLCAP_250": ("ICICI Prudential Nifty Smallcap 250 Index Fund Direct Growth", "149283"),

"INDEX_BANK": ("ICICI Prudential Nifty Bank Index Fund Direct Growth", "149858"),
"INDEX_IT": ("ICICI Prudential Nifty IT Index Fund Direct Growth", "150468"),
"INDEX_PHARMA": ("ICICI Prudential Nifty Pharma Index Fund Direct Growth", "150930"),
"INDEX_AUTO": ("ICICI Prudential Nifty Auto Index Fund Direct Growth", "150643"),
"INDEX_PRIVATE_BANK": ("ICICI Prudential Nifty Private Bank Index Fund Direct Growth", "153679"),

"INDEX_MOMENTUM": ("ICICI Prudential Nifty 200 Momentum 30 Index Fund Direct Growth", "150452"),
"INDEX_VALUE": ("ICICI Prudential Nifty50 Value 20 Index Fund Direct Growth", "152365"),
"INDEX_QUALITY": ("ICICI Prudential Nifty200 Quality 30 Index Fund Direct Growth", "153546"),


"INDEX_RAILWAYS": ("Groww Nifty India Railways PSU Index Fund - Direct Plan", "153230"),

"INDEX_NASDAQ_100": ("ICICI Prudential Nasdaq 100 Index Fund Direct Growth", "149219"),


"INDEX_SP_500": ("Motilal Oswal S&P 500 Index Fund Direct Growth", "148381"),

"INDEX_AXIS_SENSEX": ("Axis BSE Sensex Index Fund - Direct Plan", "152422"),

"INDEX_SENSEX": ("ICICI Prudential BSE Sensex Index Fund Direct Growth", "141841"),
"INDEX_EQUAL_WEIGHT": ("ICICI Prudential Nifty50 Equal Weight Index Fund Direct Growth", "150639"),
}

for key, (name, code) in INDEX_REGISTRY.items():
    keywords = ["index", "nifty"] if "nifty" in name.lower() else ["index"]

    valid, actual = validate_scheme(code, keywords)

    print(f"{key}: {'OK' if valid else 'FAIL'} → {actual}")
