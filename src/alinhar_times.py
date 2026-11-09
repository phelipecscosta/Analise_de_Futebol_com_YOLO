"""Alinha a numeração dos times entre trechos: 0 = Flamengo, 1 = Criciúma.

O detectar_rastrear.py chama de time 0 o maior grupo nos quadros de calibração,
então a numeração pode inverter de um trecho para outro. Regra: entre os grupos
0 e 1, o de matiz mais próximo do VERMELHO é o Flamengo (camisa rubro-negra);
o outro é o Criciúma (amarelo). Reescreve tracks.csv e meta.json, guardando
um backup tracks_original.csv na primeira execução.
"""
import json
import shutil
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

TRECHOS = ["seg1", "seg2"]
NOMES = {"0": "Flamengo", "1": "Criciúma", "-2": "outros"}


def matiz(bgr) -> float:
    """Matiz OpenCV (0–179) de uma cor BGR."""
    return float(cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0, 0, 0])


def dist_vermelho(h: float) -> float:
    """Distância circular do matiz h ao vermelho (H=0 ≡ H=180 no OpenCV)."""
    return min(h, 180 - h)


for seg in TRECHOS:
    pasta = Path("saidas") / seg
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))

    # Backup do tracks.csv original (só na primeira vez, nunca sobrescreve)
    backup = pasta / "tracks_original.csv"
    if not backup.exists():
        shutil.copy(pasta / "tracks.csv", backup)

    # Sempre parte do ORIGINAL: rodar o script 2 vezes dá o mesmo resultado
    tracks = pd.read_csv(backup)
    cores = meta.get("times_bgr_original", meta["times_bgr"])

    h0, h1 = matiz(cores["0"]), matiz(cores["1"])
    inverter = dist_vermelho(h1) < dist_vermelho(h0)  # o grupo 1 é o mais vermelho?

    if inverter:
        tracks["time"] = tracks["time"].replace({0: 1, 1: 0})
        cores_alinhadas = {"0": cores["1"], "1": cores["0"], "-2": cores.get("-2")}
    else:
        cores_alinhadas = dict(cores)

    tracks.to_csv(pasta / "tracks.csv", index=False)
    meta["times_bgr_original"] = cores
    meta["times_bgr"] = cores_alinhadas
    meta["times_nomes"] = NOMES
    meta["times_invertidos"] = bool(inverter)
    (pasta / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"{seg} | matiz T0={h0:5.1f} T1={h1:5.1f} | "
          f"{'INVERTIDO' if inverter else 'mantido  '} → 0=Flamengo, 1=Criciúma")
