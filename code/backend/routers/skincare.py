import json
from datetime import date as date_type

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.skincare_engine import SkincareEngine

router = APIRouter()

SKINCARE_ENGINE = SkincareEngine()


@router.get("/routine")
async def get_skincare_routine(
    user_id: int = 1,
    db: Session = Depends(get_db),
    include_adaptations: bool = Query(True, description="Include skin reaction adaptations"),
    include_rotation: bool = Query(True, description="Include ingredient rotation recommendations"),
    include_conflicts: bool = Query(True, description="Include ingredient conflict checks"),
    include_evidence: bool = Query(True, description="Include evidence summary"),
):
    engine = SkincareEngine(db_session=db, user_id=user_id)  # per user: logged reactions count
    skin_analysis = {"skin_type": "combination", "problems": []}
    lifestyle = {"sleep": 7, "stress": 5}

    routine = engine.generate_adaptive_routine(skin_analysis=skin_analysis, lifestyle=lifestyle)

    # INT-3 survival_mode from the hub: only the basics
    from ..models.directive_state import DirectiveState

    state = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    if state and state.survival_mode:
        routine["survival_mode"] = True
        routine["morning"] = ["Przemycie twarzy wodą", "SPF 30+"]
        routine["evening"] = ["Delikatne oczyszczenie"]
        routine["notes"] = "Tryb minimum: tylko podstawy. Wszystko inne może poczekać."

    if include_conflicts:
        routine["conflicts"] = engine.check_ingredient_conflicts(routine)

    if include_evidence:
        routine["evidence_summary"] = engine.get_evidence_summary(routine)

    return routine


@router.post("/routine/adaptive")
async def get_adaptive_skincare_routine(
    skin_analysis: dict,
    lifestyle: dict,
    current_routine: dict = None,
    reaction_history: list = None,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Generate adaptive routine with full context."""
    engine = SkincareEngine(db_session=db, user_id=user_id)

    routine = engine.generate_adaptive_routine(
        skin_analysis=skin_analysis,
        lifestyle=lifestyle,
        reaction_history=reaction_history,
        current_routine=current_routine
    )

    routine["conflicts"] = engine.check_ingredient_conflicts(routine)
    routine["evidence_summary"] = engine.get_evidence_summary(routine)

    return routine


@router.post("/reaction/log")
async def log_skin_reaction(
    ingredient: str,
    reaction: str,
    severity: str,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Log a skin reaction to an ingredient."""
    engine = SkincareEngine(db_session=db, user_id=user_id)
    record = engine.reaction_tracker.log_reaction(ingredient, reaction, severity)
    return {"status": "logged", "record": record}


@router.get("/rotation/recommendations")
async def get_rotation_recommendations(
    current_routine: dict,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get ingredient rotation recommendations for current routine."""
    engine = SkincareEngine(db_session=db, user_id=user_id)
    recommendations = engine.rotation_manager.get_rotation_recommendations(current_routine)
    return {"recommendations": recommendations}


@router.get("/tolerance/{ingredient}")
async def get_ingredient_tolerance(
    ingredient: str,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get tolerance level for a specific ingredient."""
    engine = SkincareEngine(db_session=db, user_id=user_id)
    tolerance = engine.reaction_tracker.get_tolerance_level(ingredient)
    overall = engine.reaction_tracker.get_overall_sensitivity()
    return {
        "ingredient": ingredient,
        "tolerance_level": tolerance,
        "overall_sensitivity": overall
    }

# ── My products: label scan / pasted INCI, "Użyłem dziś" (owner request 2026-09-27) ──

MAX_LABEL_BYTES = 8 * 1024 * 1024


class ParseRequest(BaseModel):
    text: str
    name: str = ""


class ProductIn(BaseModel):
    name: str
    ingredients: list[str]
    slot: str | None = None  # morning | evening | both


class UsageIn(BaseModel):
    product_ids: list[int]
    date: str | None = None


def _product_report(db: Session, user_id: int, ingredients: list[str], name: str = "") -> dict:
    """Actives, irritant flags, conflicts with products already in the routine, tolerance from reactions."""
    from ..models.skincare_product import SkincareProduct
    from ..services.ingredient_label import analyze_ingredients, concentration_hint

    found = analyze_ingredients(ingredients)
    for a in found["actives"]:
        a["hint"] = concentration_hint(a["position"], len(ingredients))

    engine = SkincareEngine(db_session=db, user_id=user_id)
    others = db.query(SkincareProduct).filter(SkincareProduct.user_id == user_id, SkincareProduct.in_routine.is_(True))
    routine_actives = sorted({n for p in others for n in json.loads(p.actives_json)})
    new = [a["name"] for a in found["actives"]]
    before = engine.check_ingredient_conflicts({"morning": routine_actives, "evening": []})
    after = engine.check_ingredient_conflicts({"morning": routine_actives + new, "evening": []})
    conflicts = [c for c in after if c not in before]  # only conflicts this product brings in

    tolerance = []
    for n in new:
        level = engine.reaction_tracker.get_tolerance_level(n)
        if level != "none":
            tolerance.append({"ingredient": n, "reaction_level": level,
                              "message": f"Po składniku {n} zapisane były reakcje skóry ({level}). Wprowadzaj ostrożnie albo pomiń."})
    return {"name": name, "ingredients": ingredients, "actives": found["actives"], "flags": found["flags"],
            "conflicts": conflicts, "tolerance_warnings": tolerance, "routine_actives": routine_actives}


@router.post("/products/parse")
async def parse_product(req: ParseRequest, user_id: int = 1, db: Session = Depends(get_db)):
    """Pasted ingredient list - no AI involved."""
    from ..services.ingredient_label import parse_inci

    ingredients = parse_inci(req.text)
    if not ingredients:
        raise HTTPException(422, "Nie znaleziono składników — wklej listę INCI oddzieloną przecinkami.")
    return _product_report(db, user_id, ingredients, req.name)


@router.post("/products/scan")
async def scan_product(file: UploadFile = File(...), user_id: int = 1, db: Session = Depends(get_db)):
    """Photo of the label: AI transcribes the INCI list, the analysis is local."""
    from ..services.gemini_vision import GeminiVisionService
    from ..services.ingredient_label import parse_inci

    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Wyślij zdjęcie etykiety (JPG/PNG).")
    data = await file.read()
    if len(data) > MAX_LABEL_BYTES:
        raise HTTPException(413, "Zdjęcie za duże (max 8 MB).")
    label = GeminiVisionService().read_ingredient_label(data) or {}
    ingredients = parse_inci(label.get("ingredients_text") or "")
    if not ingredients:
        raise HTTPException(422, "Nie udało się odczytać składu. Zrób ostrzejsze zdjęcie listy składników albo wklej ją ręcznie.")
    return _product_report(db, user_id, ingredients, label.get("product_name") or "")


def _product_out(row) -> dict:
    return {"id": row.id, "name": row.name, "slot": row.slot, "in_routine": row.in_routine,
            "actives": json.loads(row.actives_json), "ingredients": json.loads(row.ingredients_json)}


@router.post("/products", status_code=201)
async def save_product(p: ProductIn, user_id: int = 1, db: Session = Depends(get_db)):
    from ..models.skincare_product import SkincareProduct
    from ..services.ingredient_label import analyze_ingredients

    actives = [a["name"] for a in analyze_ingredients(p.ingredients)["actives"]]
    row = SkincareProduct(user_id=user_id, name=p.name.strip() or "Produkt", slot=p.slot,
                          ingredients_json=json.dumps(p.ingredients, ensure_ascii=False),
                          actives_json=json.dumps(actives, ensure_ascii=False))
    db.add(row)
    db.commit()
    db.refresh(row)
    return _product_out(row)


@router.get("/products")
async def list_products(user_id: int = 1, db: Session = Depends(get_db)):
    from ..models.skincare_product import IngredientUsage, SkincareProduct

    rows = db.query(SkincareProduct).filter(SkincareProduct.user_id == user_id).order_by(SkincareProduct.id).all()
    used_today = {r[0] for r in db.query(IngredientUsage.product_id).filter(
        IngredientUsage.user_id == user_id, IngredientUsage.date == date_type.today())}
    return [{**_product_out(r), "used_today": r.id in used_today} for r in rows]


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    from ..models.skincare_product import SkincareProduct

    row = db.query(SkincareProduct).filter(SkincareProduct.id == product_id, SkincareProduct.user_id == user_id).first()
    if not row:
        raise HTTPException(404, "Nie ma takiego produktu")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/usage/log")
async def log_usage(u: UsageIn, user_id: int = 1, db: Session = Depends(get_db)):
    """'Użyłem dziś': one row per active of each product (idempotent per day) - feeds rotation."""
    from ..models.skincare_product import IngredientUsage, SkincareProduct

    day = date_type.fromisoformat(u.date) if u.date else date_type.today()
    logged = 0
    for p in db.query(SkincareProduct).filter(SkincareProduct.user_id == user_id, SkincareProduct.id.in_(u.product_ids)):
        for active in json.loads(p.actives_json) or ["(bez aktywnych)"]:
            exists = db.query(IngredientUsage).filter(
                IngredientUsage.user_id == user_id, IngredientUsage.product_id == p.id,
                IngredientUsage.ingredient == active, IngredientUsage.date == day).first()
            if not exists:
                db.add(IngredientUsage(user_id=user_id, ingredient=active, product_id=p.id, date=day))
                logged += 1
    db.commit()
    return {"status": "logged", "entries": logged, "date": day.isoformat()}


@router.get("/rotation/mine")
async def my_rotation(user_id: int = 1, db: Session = Depends(get_db)):
    """Rotation advice for the actives in the user's own products."""
    from ..models.skincare_product import SkincareProduct

    rows = db.query(SkincareProduct).filter(SkincareProduct.user_id == user_id, SkincareProduct.in_routine.is_(True)).all()
    actives = sorted({a for r in rows for a in json.loads(r.actives_json)})
    engine = SkincareEngine(db_session=db, user_id=user_id)
    return {"actives": actives,
            "recommendations": engine.rotation_manager.get_rotation_recommendations({"morning": actives, "evening": []})}
