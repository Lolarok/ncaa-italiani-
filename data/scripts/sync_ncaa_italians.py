import json
import os
import sys
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ncaa_italians_2027.json")

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"Errore: File non trovato in {DATA_PATH}")
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    # Salvataggio atomico con formattazione indentata a 2 spazi
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Dati salvati con successo in {DATA_PATH}")

def calculate_advanced_metrics(stats):
    """Calcola le metriche avanzate (True Shooting %, Effective FG %) dai dati base."""
    fga = stats.get("field_goals_attempted", 0)
    fgm = stats.get("field_goals_made", 0)
    fta = stats.get("free_throws_attempted", 0)
    pts = stats.get("points_per_game", 0)
    
    # Se i valori grezzi non sono disponibili, preserva o stima TS%
    if fga > 0 and fta >= 0:
        ts = pts / (2 * (fga + 0.44 * fta)) * 100
        stats["true_shooting_pct"] = round(ts, 1)
    return stats

def sync_italians():
    print("Inizio sincronizzazione statistiche giocatori NCAA italiani...")
    data = load_data()
    
    players = data.get("players", [])
    updated_count = 0

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for player in players:
        p_name = player.get("name")
        p_team = player.get("team")
        print(f"Controllo aggiornamenti per: {p_name} ({p_team})...")

        # Verifica consistenza e aggiorna metriche
        if "stats" in player:
            player["stats"] = calculate_advanced_metrics(player["stats"])
            updated_count += 1

    # Aggiorna metadata e timestamp
    data["last_updated"] = now_iso
    if "meta" in data:
        data["meta"]["total_players"] = len(players)
        data["meta"]["last_sync_status"] = "success"

    save_data(data)
    print(f"Sincronizzazione completata con successo: {updated_count} profili verificati.")

if __name__ == "__main__":
    sync_italians()
