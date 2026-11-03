"""Cosmetic barcode -> ingredient list via Open Beauty Facts (plan 5.7).

Open Beauty Facts is an open, crowd-sourced database (openbeautyfacts.org).
Only the INCI text and name are taken; the analysis itself stays local
(services/ingredient_label.py). Missing or incomplete entries are common -
the caller falls back to the label photo or pasting the list.
"""
import re

import httpx

OBF_URL = "https://world.openbeautyfacts.org/api/v2/product/{code}.json"
FIELDS = "product_name,product_name_pl,brands,ingredients_text,ingredients_text_pl,ingredients_text_en"
_CODE = re.compile(r"^\d{8,14}$")


class BarcodeError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def lookup(code: str, get=httpx.get) -> dict:
    code = (code or "").strip()
    if not _CODE.match(code):
        raise BarcodeError(422, "Kod kreskowy to 8–14 cyfr.")
    try:
        resp = get(OBF_URL.format(code=code), params={"fields": FIELDS}, timeout=8.0,
                   headers={"User-Agent": "LookCoach/0.4 (personal use)"})
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        raise BarcodeError(503, "Baza Open Beauty Facts jest teraz niedostępna.") from e
    product = data.get("product") or {}
    if data.get("status") != 1 or not product:
        raise BarcodeError(404, "Nie ma tego produktu w Open Beauty Facts — zrób zdjęcie składu albo wklej go.")
    text = product.get("ingredients_text_pl") or product.get("ingredients_text_en") or product.get("ingredients_text") or ""
    if not text.strip():
        raise BarcodeError(404, "Produkt jest w bazie, ale bez składu — zrób zdjęcie listy składników.")
    name = product.get("product_name_pl") or product.get("product_name") or ""
    brand = (product.get("brands") or "").split(",")[0].strip()
    return {"product_name": f"{brand} {name}".strip(), "ingredients_text": text, "source": "Open Beauty Facts"}
