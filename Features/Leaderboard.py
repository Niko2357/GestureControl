import json
import os

FILE_NAME = "leaderboard.json"


def save_score(game, name, player_class, score):
    data = {}
    # Načtení existujících dat, pokud soubor existuje
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}

    if game not in data:
        data[game] = []

    # Přidání nového hráče
    data[game].append({"name": name, "class": player_class, "score": score})

    # Seřazení od nejlepšího po nejhoršího
    data[game] = sorted(data[game], key=lambda x: x["score"], reverse=True)

    # Uložení zpět do souboru
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_top_scores(game, limit=5):
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(game, [])[:limit]
