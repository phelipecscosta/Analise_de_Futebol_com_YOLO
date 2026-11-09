"""Diagnóstico: quem são os IDs de vida curta (< 1 s)? (Q3.1)

Compara IDs curtos x longos em confiança, tamanho do box (altura em px),
posição vertical (py: perto do topo = longe/arquibancada) e rótulo de time.
"""
import pandas as pd

FPS = 30
t = pd.read_csv("saidas/seg1/tracks.csv")
p = t[t["classe"] != "bola"].copy()
p["altura_box"] = p["y2"] - p["y1"]

# Resumo por ID
por_id = p.groupby("track_id").agg(
    duracao_s=("frame", lambda f: (f.max() - f.min() + 1) / FPS),
    conf_media=("conf", "mean"),
    altura_media=("altura_box", "mean"),
    py_medio=("py", "mean"),
    time_mais_comum=("time", lambda s: s.mode().iat[0]),
)
por_id["grupo"] = pd.cut(por_id["duracao_s"], [0, 1, 5, 1e9], labels=["<1s", "1-5s", ">5s"])

resumo = por_id.groupby("grupo", observed=True).agg(
    n_ids=("duracao_s", "size"),
    conf_media=("conf_media", "median"),
    altura_px=("altura_media", "median"),
    py_medio=("py_medio", "median"),
).round(2)
print("=== Por faixa de duração do ID (seg1) ===")
print(resumo.to_string())

print("\n=== Rótulo de time dos IDs < 1 s (-1 = sem rótulo, -2 = outros) ===")
curtos = por_id[por_id["grupo"] == "<1s"]
print(curtos["time_mais_comum"].value_counts(normalize=True).mul(100).round(1).to_string())

# Quantas detecções (linhas) vêm de IDs longos? (é o que importa para as métricas)
p = p.join(por_id["grupo"], on="track_id")
print("\n=== % das DETECÇÕES por faixa de duração do ID ===")
print(p["grupo"].value_counts(normalize=True).mul(100).round(1).to_string())
