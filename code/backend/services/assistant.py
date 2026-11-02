"""LookCoach assistant (plan 8.2-8.4, D10).

A chat about the user's looks plan, grounded in their own data
(assistant_context) and bound by the module's rules:
- LC-9: never rate attractiveness with a number - a reply that does anyway is
  replaced (`_violates_lc9`),
- LC-1: recommendations only from the provided list with their evidence level,
  anything else explicitly "hipoteza / porada stylistyczna",
- LC-8: health flags are hard limits,
- LC-4: no training plans or diets - ForgeBody / Dieta do that,
- body-image distress -> calm, non-judgemental reply + Mentalność, and the
  hub is told (at most once a week, wellbeing_guard).

Actions (8.4) are only *proposed*; the UI asks the user before running any.
"""
import json
import re

from sqlalchemy.orm import Session

from ..models.assistant_message import AssistantMessage
from .assistant_context import build_context

HISTORY_TURNS = 12
MAX_MESSAGE_CHARS = 2000

ALLOWED_ACTIONS = {
    "send_needs": "Wyślij potrzeby do ForgeBody/Diety",
    "start_experiment": "Zacznij eksperyment",
    "open_page": "Otwórz stronę",
}
PAGES = {"/photos", "/style", "/recommendations", "/skincare", "/consistency", "/experiments",
         "/training", "/nutrition", "/profile", "/progress", "/sleep", "/stress"}

SYSTEM_PROMPT = """Jesteś asystentem modułu LookCoach (wygląd, pielęgnacja, styl) w osobistym systemie użytkownika.
Odpowiadasz po polsku, krótko i konkretnie, życzliwie, bez oceniania.

ZASADY (bezwzględne):
1. Nigdy nie oceniasz atrakcyjności ani wyglądu liczbą, procentem, skalą czy rankingiem. Opisujesz stan
   (np. „obrzęk: niski”) i co można zrobić.
2. Rekomendacje opierasz na liście `recommendations` z kontekstu i podajesz ich poziom dowodów
   (RCT/meta/obserwacyjne/ekspert). Coś spoza listy oznacz wprost jako „hipoteza” albo „porada stylistyczna”.
   Nie wymyślasz liczb, procentów skuteczności ani badań.
3. `health_flags` to twarde przeciwwskazania — nie proponujesz niczego, co im przeczy.
4. Nie układasz planów treningowych ani diet: priorytety mięśni przekazuje ForgeBody, potrzeby
   żywieniowe — Dieta (akcja send_needs). Możesz wyjaśnić „dlaczego”.
5. Jeśli użytkownik źle mówi o swoim wyglądzie, porównuje się obsesyjnie lub opisuje cierpienie z tego
   powodu — odpowiadasz spokojnie, bez wzmacniania, sugerujesz przerwę od sprawdzania wyglądu i rozmowę
   z psychologiem (moduł Mentalność). Nie diagnozujesz.
6. W `hub_directives.survival_mode` proponujesz tylko wersję minimum.
7. Bazujesz wyłącznie na kontekście poniżej; jeśli czegoś nie wiesz (np. brak zdjęć) — powiedz to.

FORMAT: zwróć wyłącznie JSON: {"reply": "tekst", "actions": [...]}. Akcje (opcjonalne, max 2):
{"type": "send_needs"} | {"type": "start_experiment", "template_id": "..."} | {"type": "open_page", "path": "/style"}.
Akcje są tylko propozycją — użytkownik je zatwierdza."""

DISTRESS_PATTERNS = [
    r"\bbrzydk", r"nienawidz\w* (swoj|mojej|mojego|siebie)", r"obrzydliw", r"nie mog[eę] na siebie patrze",
    r"wstydz\w* si[eę] (swoj|wyglądu)", r"ci[aą]gle (sprawdzam|patrz[eę] w lustro)", r"obsesj",
    r"nikt mnie nie", r"jestem (gruby|gruba|odra[zż]aj)",
]
DISTRESS_NOTE = (
    "Słyszę, że wygląd sprawia Ci teraz dużo przykrości. Nie musisz niczego oceniać ani sprawdzać dziś. "
    "Jeśli takie myśli wracają często, warto porozmawiać z psychologiem — moduł Mentalność może pomóc."
)
LC9_REPLACEMENT = (
    "Nie oceniam wyglądu liczbami ani skalami — to nie mówi nic użytecznego i może szkodzić. "
    "Mogę za to opisać obserwowany stan i co konkretnie możesz zrobić. O co chcesz zapytać?"
)
_LC9 = re.compile(
    r"(\b\d+(?:[.,]\d+)?\s*/\s*10\b|\b\d+(?:[.,]\d+)?\s*/\s*100\b|\b\d+\s*%\s*(atrakcyj|urody|wygl))"
    r"|(atrakcyjno\w*[^.]{0,30}\b\d+\b)",
    re.IGNORECASE,
)


class AssistantUnavailable(Exception):
    pass


def is_distress(message: str) -> bool:
    text = message.lower()
    return any(re.search(p, text) for p in DISTRESS_PATTERNS)


def _violates_lc9(reply: str) -> bool:
    return bool(_LC9.search(reply))


def _parse(raw: str) -> tuple[str, list[dict]]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        data = json.loads(text)
        reply = str(data.get("reply", "")).strip()
        actions = data.get("actions") or []
    except (ValueError, AttributeError):
        return raw.strip(), []
    return reply or raw.strip(), actions if isinstance(actions, list) else []


def _clean_actions(actions: list) -> list[dict]:
    out = []
    for a in actions:
        if len(out) == 2:
            break
        if not isinstance(a, dict) or a.get("type") not in ALLOWED_ACTIONS:
            continue
        if a["type"] == "open_page" and a.get("path") not in PAGES:
            continue
        if a["type"] == "start_experiment" and not isinstance(a.get("template_id"), str):
            continue
        out.append({**{k: a[k] for k in ("type", "path", "template_id") if k in a},
                    "label": ALLOWED_ACTIONS[a["type"]]})
    return out


def _default_llm(messages: list[dict]) -> str:
    from .local_llm import LocalLLMService
    from .openrouter import OpenRouterService

    try:
        return OpenRouterService().chat(messages)
    except Exception:
        flat = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
        text = LocalLLMService().generate_text(flat, use_openrouter=False)
        if not text:
            raise AssistantUnavailable from None
        return text


def history(db: Session, user_id: int, limit: int = 50) -> list[dict]:
    rows = (
        db.query(AssistantMessage)
        .filter(AssistantMessage.user_id == user_id)
        .order_by(AssistantMessage.id.desc())
        .limit(limit)
        .all()
    )[::-1]
    return [
        {"role": r.role, "content": r.content, "actions": json.loads(r.actions) if r.actions else [],
         "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in rows
    ]


def chat(db: Session, user_id: int, message: str, llm=None) -> dict:
    message = message.strip()[:MAX_MESSAGE_CHARS]
    context = build_context(db, user_id)
    past = history(db, user_id, limit=HISTORY_TURNS)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": "KONTEKST UŻYTKOWNIKA (JSON):\n" + json.dumps(context, ensure_ascii=False, default=str)},
        *({"role": m["role"], "content": m["content"]} for m in past),
        {"role": "user", "content": message},
    ]
    raw = (llm or _default_llm)(messages)
    reply, actions = _parse(raw)
    actions = _clean_actions(actions)

    flags = []
    if _violates_lc9(reply):
        reply, flags = LC9_REPLACEMENT, ["lc9_replaced"]
    distress = is_distress(message)
    if distress:
        reply = f"{DISTRESS_NOTE}\n\n{reply}"
        flags.append("distress")
        _signal_distress(db, user_id)

    db.add(AssistantMessage(user_id=user_id, role="user", content=message))
    db.add(AssistantMessage(user_id=user_id, role="assistant", content=reply,
                            actions=json.dumps(actions, ensure_ascii=False)))
    db.commit()
    return {"reply": reply, "actions": actions, "flags": flags}


def _signal_distress(db: Session, user_id: int) -> None:
    """Same weekly-deduplicated channel as the photo-checking detector (H-6)."""
    from .wellbeing_guard import signal_hub_if_needed

    signal_hub_if_needed(db, user_id, {"level": "concern", "signals": ["distress_in_assistant_chat"]})


def clear(db: Session, user_id: int) -> int:
    n = db.query(AssistantMessage).filter(AssistantMessage.user_id == user_id).delete()
    db.commit()
    return n

