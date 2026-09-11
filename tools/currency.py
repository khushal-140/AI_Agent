"""Currency tool: live exchange rates via open.er-api.com (free, no key).

Rates are never hardcoded - if the API is unreachable the tool returns an
error instead of pretending to know today's rate.
"""

import requests

from config import API_TIMEOUT

EXCHANGE_API = "https://open.er-api.com/v6/latest/{base}"


def convert_currency(amount=1.0, from_currency="USD", to_currency="INR") -> dict:
    """Convert `amount` from one currency to another using live rates."""
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return {"status": "error", "error": "Amount must be a number."}
    if value <= 0:
        return {"status": "error", "error": "Amount must be greater than zero."}

    base = str(from_currency or "").strip().upper()
    target = str(to_currency or "").strip().upper()
    if len(base) != 3 or not base.isalpha() or len(target) != 3 or not target.isalpha():
        return {"status": "error", "error": "Currency codes must be 3 letters, e.g. USD or INR."}

    try:
        response = requests.get(EXCHANGE_API.format(base=base), timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Exchange-rate service timed out. Please try again."}
    except requests.exceptions.RequestException:
        return {"status": "error", "error": "Exchange-rate service is currently unavailable."}
    except ValueError:
        return {"status": "error", "error": "Exchange-rate service returned unexpected data."}

    if data.get("result") != "success":
        return {"status": "error", "error": f"Could not fetch exchange rates for {base}."}

    rate = (data.get("rates") or {}).get(target)
    if rate is None:
        return {"status": "error", "error": f"Unsupported target currency '{target}'."}

    return {
        "status": "success",
        "source": "open.er-api.com (live)",
        "from": base,
        "to": target,
        "amount": value,
        "rate": rate,
        "converted": round(value * rate, 2),
        "last_updated": data.get("time_last_update_utc", "unknown"),
    }
