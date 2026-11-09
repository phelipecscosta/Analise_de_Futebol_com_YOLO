"""Estimativa indireta de trocas de ID do ByteTrack (Q3.1).

Compara o nº de IDs distintos criados com o nº de pessoas visíveis ao mesmo
tempo. IDs "excedentes" indicam trocas de ID ou reaparecimentos com ID novo.
"""
from pathlib import Path

import pandas as pd

TRECHOS = ["seg1", "seg2"]
FPS = 30

linhas = []
for seg in TRECHOS:
    t = pd.read_csv(Path("saidas") / seg / "tracks.csv")
    p = t[t["classe"] != "bola"]                      # só pessoas
    n_quadros = t["frame"].max() + 1
    minutos = n_quadros / FPS / 60

    por_quadro = p.groupby("frame")["track_id"].nunique()
    duracao_s = p.groupby("track_id")["frame"].agg(lambda f: (f.max() - f.min() + 1) / FPS)

    ids = p["track_id"].nunique()
    max_sim = int(por_quadro.max())
    linhas.append({
        "trecho": seg,
        "duracao_min": round(minutos, 2),
        "pessoas_max_simult": max_sim,
        "pessoas_media": round(por_quadro.mean(), 1),
        "ids_distintos": ids,
        "ids_excedentes": ids - max_sim,
        "ids_novos_por_min": round(ids / minutos, 1),
        "vida_mediana_id_s": round(duracao_s.median(), 1),
        "%_ids_<1s": round(100 * (duracao_s < 1).mean(), 1),  # IDs "relâmpago"
    })

tabela = pd.DataFrame(linhas)
print(tabela.to_string(index=False))
tabela.to_csv("saidas/estatisticas_ids.csv", index=False)
print("\nSalvo: saidas/estatisticas_ids.csv")
