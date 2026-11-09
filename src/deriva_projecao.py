"""Deriva da projeção ao longo do tempo (Q4.3).

Usa a bola como termômetro: ela deveria estar quase sempre DENTRO do campo.
Calcula o % de posições válidas da bola em janelas de 5 s e gera um gráfico.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

FPS, JANELA_S = 30, 5
fig, ax = plt.subplots(figsize=(10, 4))

for seg in ["seg1", "seg2"]:
    b = pd.read_csv(Path("saidas") / seg / "bola_campo.csv")
    b["janela"] = (b["frame"] / FPS // JANELA_S * JANELA_S).astype(int)  # início da janela (s)
    valido = b.groupby("janela")["x_m"].apply(lambda s: 100 * s.notna().mean())
    ax.plot(valido.index, valido.values, marker="o", label=seg)
    print(f"{seg}: " + "  ".join(f"{t}s={v:.0f}%" for t, v in valido.items()))

ax.set_xlabel("tempo no trecho (s)")
ax.set_ylabel("% da bola projetada dentro do campo")
ax.set_title("Deriva da homografia ao longo do tempo (janelas de 5 s)")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
ax.legend()
Path("figuras").mkdir(exist_ok=True)
fig.savefig("figuras/q4_3_deriva_projecao.png", dpi=120, bbox_inches="tight")
print("\nSalvo: figuras/q4_3_deriva_projecao.png")
