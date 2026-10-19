#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP API for the АльфаДент Telegram Mini App.

Run behind HTTPS/reverse proxy. Telegram WebApp initData is validated before any
CRM write. The API creates leads in Bitrix24; it does not reserve real MIS slots.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()
import bot_telegram as bot

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
log = logging.getLogger("alfadent_webapp_api")
WEB_DIR = Path(__file__).resolve().parent / "web"
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
INITDATA_MAX_AGE_SECONDS = int(os.getenv("INITDATA_MAX_AGE_SECONDS", "86400"))

app = FastAPI(title="АльфаДент Mini App API", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=WEB_DIR / "assets"), name="assets")

class RequestBody(BaseModel):
    initData: str = Field(default="", max_length=10000)
    payload: dict[str, Any]


def validated_telegram_user(init_data: str) -> dict[str, Any]:
    if not BOT_TOKEN:
        raise HTTPException(status_code=503, detail="API не настроен: отсутствует TELEGRAM_TOKEN.")
    if not init_data:
        raise HTTPException(status_code=401, detail="Откройте Mini App из Telegram, чтобы отправить запрос.")
    try:
        parts = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        raise HTTPException(status_code=401, detail="Некорректные данные запуска Telegram.")
    received_hash = parts.pop("hash", "")
    if not received_hash:
        raise HTTPException(status_code=401, detail="В данных запуска отсутствует подпись Telegram.")
    check_string = "\n".join(f"{key}={value}" for key, value in sorted(parts.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise HTTPException(status_code=401, detail="Не удалось проверить подпись Telegram.")
    try:
        user = json.loads(parts.get("user", "{}"))
        auth_date = int(parts.get("auth_date", "0"))
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Некорректные данные пользователя Telegram.")
    now = int(time.time())
    if not auth_date or auth_date > now + 60 or now - auth_date > INITDATA_MAX_AGE_SECONDS:
        raise HTTPException(status_code=401, detail="Данные запуска устарели. Закройте и снова откройте Mini App.")
    if not isinstance(user, dict) or not str(user.get("id", "")).isdigit():
        raise HTTPException(status_code=401, detail="Не удалось определить пользователя Telegram.")
    return user


def clean(value: Any, limit: int = 300) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value or "")).strip()[:limit]


def normalize_payload_phone(raw: str) -> str:
    normalized = bot.normalize_phone(raw)
    if not normalized:
        raise HTTPException(status_code=422, detail="Укажите корректный российский номер телефона.")
    return "+7" + normalized


def write_general_lead(user_id: int, name: str, phone: str, title: str, comments: str) -> dict[str, Any]:
    if not bot.BITRIX24_WEBHOOK:
        bot.save_pending_request({"type": title, "user_id": user_id, "description": comments, "phone": phone})
        raise HTTPException(status_code=503, detail="Интеграция с CRM не настроена. Обращение сохранено локально, но не передано администратору.")
    result = bot.bitrix_call("crm.item.add", {"entityTypeId": 1, "fields": {
        "title": title[:255], "name": name or "Пациент Mini App", "comments": comments,
        "sourceId": "WEB", "assignedById": int(os.getenv("BITRIX_ASSIGNED_BY_ID", "33")),
        "OPENED": "Y", "observers": bot.ADMIN_IDS,
    }})
    lead_id = result.get("result", {}).get("item", {}).get("id")
    if not lead_id:
        bot.save_pending_request({"type": title, "user_id": user_id, "description": comments, "phone": phone, "bitrix_error": result.get("error", "unknown")})
        raise HTTPException(status_code=502, detail="CRM не подтвердила создание обращения. Данные сохранены в резервной очереди; пожалуйста, позвоните в клинику.")
    if phone:
        bot.bitrix_call("crm.item.update", {"entityTypeId": 1, "id": lead_id, "fields": {
            "fm": [{"typeId": "PHONE", "valueType": "WORK", "value": phone}]
        }})
    return {"lead_id": str(lead_id)}


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "miniapp.html")

@app.get("/miniapp.html")
def miniapp_page():
    return FileResponse(WEB_DIR / "miniapp.html")

@app.get("/health")
def health():
    return {"ok": True, "service": "alfadent-miniapp-api", "crm_configured": bool(bot.BITRIX24_WEBHOOK)}

@app.post("/api/appointment")
def create_appointment(body: RequestBody):
    tg_user = validated_telegram_user(body.initData)
    user_id = int(tg_user["id"])
    p = body.payload
    name = clean(p.get("name"), 100) or clean(tg_user.get("first_name"), 100) or "Пациент"
    phone = normalize_payload_phone(clean(p.get("phone"), 40))
    appointment = {
        "problem": clean(p.get("problem"), 200),
        "service": clean(p.get("service"), 200),
        "doctor": clean(p.get("doctor"), 200),
        "date": clean(p.get("date"), 40),
        "time": clean(p.get("time"), 40),
        "mode": "Mini App",
    }
    if not any(appointment.get(k) for k in ("problem", "service", "doctor")):
        raise HTTPException(status_code=422, detail="Выберите проблему, услугу или врача.")
    session = bot.session_for(user_id, name)
    session["name"] = name
    session["phone"] = phone
    result = bot.create_appointment_lead(user_id, appointment)
    lead_id = result.get("result", {}).get("item", {}).get("id")
    if not lead_id:
        raise HTTPException(status_code=502, detail="CRM не подтвердила создание заявки. Данные сохранены в резервной очереди, но запись не создана; свяжитесь с клиникой по телефону " + bot.CLINIC_PHONE + ".")
    return {"ok": True, "lead_id": str(lead_id), "message": "Заявка принята. Администратор свяжется с вами для подтверждения времени. Это ещё не подтверждённая запись."}

@app.post("/api/support")
def create_support(body: RequestBody):
    tg_user = validated_telegram_user(body.initData)
    user_id = int(tg_user["id"])
    p = body.payload
    name = clean(p.get("name"), 100) or clean(tg_user.get("first_name"), 100) or "Пациент"
    phone = normalize_payload_phone(clean(p.get("phone"), 40)) if clean(p.get("phone"), 40) else ""
    message = clean(p.get("message"), 2000)
    if len(message) < 3:
        raise HTTPException(status_code=422, detail="Напишите вопрос администратору.")
    session = bot.session_for(user_id, name)
    session["name"] = name
    session["phone"] = phone
    urgent = message.lower().startswith("срочное обращение") or "экстренно" in message.lower()
    title = ("[MINI APP] ЭКСТРЕННОЕ обращение" if urgent else "[MINI APP] Вопрос пациента")
    comments = f"Пациент: {name}\nТелефон: {phone or 'не указан'}\nTelegram ID: {user_id}\nКанал: Telegram Mini App\n\n{message}"
    result = write_general_lead(user_id, name, phone, title, comments)
    return {"ok": True, "lead_id": result["lead_id"], "message": "Экстренное обращение передано в CRM." if urgent else "Обращение передано в CRM. Администратор свяжется с вами."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "127.0.0.1"), port=int(os.getenv("API_PORT", "8001")), log_level=os.getenv("LOG_LEVEL", "info").lower())
