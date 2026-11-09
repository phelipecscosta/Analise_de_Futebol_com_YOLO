"""Sensibilidade da posse e do nº de passes ao raio de posse (Q5.2).

Roda o metricas.py com raios de 1, 2 e 3 m em cada trecho, junta os resultados
em uma tabela e um gráfico, e no final RESTAURA a execução padrão (raio 2 m),
para que os arquivos em saidas/ correspondam aos números do README.
"""
import json
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

TRECHOS = ["seg1", "seg2"]
RAIOS = [1.0, 2.0, 3.0]
PADRAO = 2.0
EXTRA = ["--ataque-time0", "direita"]  # Flamengo (time 0) ataca para a direita (conferido no vídeo)


def rodar(seg: str, raio: float) -> dict:
    subprocess.run([sys.executable, "src/metricas.py", "--saida", f"saidas/{seg}",
                    "--raio-posse", str(raio), *EXTRA],
                   check=True, stdout=subprocess.DEVNULL)
    return json.loads(Path(f"saidas/{seg}/metricas_times.json").read_text(encoding="utf-8"))


linhas = []
for seg in TRECHOS:
    for raio in RAIOS:
        r = rodar(seg, raio)
        linhas.append({"trecho": seg, "raio_m": raio,
                       "posse_fla_pct": r["time0"]["posse_pct"], "posse_cri_pct": r["time1"]["posse_pct"],
                       "passes_total": r["time0"]["passes"] + r["time1"]["passes"],
                       "quadros_com_bola": r["quadros_com_bola"]})
        print(f"{seg} raio={raio} m concluído")
    rodar(seg, PADRAO)  # restaura a execução padrão

tab = pd.DataFrame(linhas)
print("\n" + tab.to_string(index=False))
tab.to_csv("saidas/sensibilidade_raio.csv", index=False)

fig, axs = plt.subplots(1, 2, figsize=(10, 4))
for seg, g in tab.groupby("trecho"):
    axs[0].plot(g["raio_m"], g["posse_fla_pct"], marker="o", label=f"{seg} (Flamengo)")
    axs[1].plot(g["raio_m"], g["passes_total"], marker="o", label=seg)
axs[0].set(title="Posse do Flamengo x raio", xlabel="raio de posse (m)", ylabel="posse (%)", ylim=(0, 100))
axs[1].set(title="Nº de passes x raio", xlabel="raio de posse (m)", ylabel="passes")
for ax in axs:
    ax.set_xticks(RAIOS)
    ax.grid(alpha=0.3)
    ax.legend()
Path("figuras").mkdir(exist_ok=True)
fig.savefig("figuras/q5_2_sensibilidade_raio.png", dpi=120, bbox_inches="tight")
print("\nSalvo: saidas/sensibilidade_raio.csv e figuras/q5_2_sensibilidade_raio.png")
