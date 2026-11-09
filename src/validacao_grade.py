"""Validação dos passes variando o raio de posse e a tolerância de tempo (Q5.2/Q5.3).

Para cada trecho, raio (1, 2, 3 m) e tolerância (1 s, 2 s), roda metricas.py +
validar_passes.py e junta precisão/revocação/F1. No final RESTAURA o raio padrão (2 m).
"""
import re
import subprocess
import sys

import pandas as pd

TRECHOS = ["seg1", "seg2"]
RAIOS = [1.0, 2.0, 3.0]
TOLS = [1.0, 2.0]
PADRAO = 2.0


def metricas(seg, raio):
    subprocess.run([sys.executable, "src/metricas.py", "--saida", f"saidas/{seg}",
                    "--raio-posse", str(raio), "--ataque-time0", "direita"],
                   check=True, stdout=subprocess.DEVNULL)


def validar(seg, tol):
    out = subprocess.run([sys.executable, "src/validar_passes.py", "--saida", f"saidas/{seg}",
                          "--anotado", f"saidas/{seg}/passes_anotados.csv", "--tolerancia", str(tol)],
                         check=True, capture_output=True, text=True).stdout
    num = lambda rot: float(re.search(rf"{rot}\s*:\s*([\d.]+)", out).group(1))
    m = re.search(r"Detectados: (\d+) \| Anotados: (\d+) \| Casados: (\d+)", out)
    return {"detectados": int(m.group(1)), "anotados": int(m.group(2)), "casados": int(m.group(3)),
            "precisao": num("Precisão"), "revocacao": num("Revocação"), "f1": num("F1")}


linhas = []
for seg in TRECHOS:
    for raio in RAIOS:
        metricas(seg, raio)
        for tol in TOLS:
            linhas.append({"trecho": seg, "raio_m": raio, "tol_s": tol, **validar(seg, tol)})
    metricas(seg, PADRAO)  # restaura a execução padrão

tab = pd.DataFrame(linhas)
# Total dos dois trechos (soma das contagens e recálculo das métricas)
tot = tab.groupby(["raio_m", "tol_s"], as_index=False)[["detectados", "anotados", "casados"]].sum()
tot["precisao"] = (tot["casados"] / tot["detectados"]).round(2)
tot["revocacao"] = (tot["casados"] / tot["anotados"]).round(2)
tot["f1"] = (2 * tot["precisao"] * tot["revocacao"] / (tot["precisao"] + tot["revocacao"])).round(2)
tot.insert(0, "trecho", "total")
tab = pd.concat([tab, tot], ignore_index=True)

print(tab.to_string(index=False))
tab.to_csv("saidas/validacao_passes_grade.csv", index=False)
print("\nSalvo: saidas/validacao_passes_grade.csv")
