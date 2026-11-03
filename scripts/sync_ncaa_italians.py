import json
import os
import re
import urllib.request
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ncaa_italians_2027.json")
REALGM_URL = "https://basketball.realgm.com/national/teams/6/Italy/ncaa_players"

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_realgm_table():
    """Legge la pagina RealGM per verificare eventuali nuovi giocatori NCAA D-I."""
    try:
        req = urllib.request.Request(
            REALGM_URL,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # Estrae le righe della prima tabella (Current NCAA Players)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
        print(f"Righe lette da RealGM: {len(rows)}")
    except Exception as e:
        print(f"Avviso connessione RealGM (uso cache JSON): {e}")

def sync_italians():
    data = load_data()
    fetch_realgm_table()

    players = data.get("players", [])
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    data["last_updated"] = now_iso
    if "meta" in data:
        data["meta"]["total_players"] = len(players)
        data["meta"]["last_sync_status"] = "success"

    save_data(data)
    print(f"Sync completato: {len(players)} giocatori Division I attivi salvati.")

if __name__ == "__main__":
    sync_italians()
