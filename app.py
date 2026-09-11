from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import json, uuid
from pathlib import Path

app = Flask(__name__)
LOG = Path("locations.jsonl")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/location")
def location():
    data = request.get_json(force=True)

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Gera o link direto para o Google Maps
    maps_url = None

    if latitude is not None and longitude is not None:
        maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    record = {
        "id": str(uuid.uuid4()),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "latitude": latitude,
        "longitude": longitude,
        "accuracy_m": data.get("accuracy_m"),
        "client_timestamp": data.get("timestamp"),
        "maps_url": maps_url
    }

    # Para um laboratório real, mantenha retenção curta e acesso restrito.
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Retorna o link do Google Maps
    return jsonify({
        "ok": True,
        "id": record["id"],
        "maps_url": maps_url
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)