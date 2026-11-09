"""Desenha as cores dos centróides dos times (meta.json → times_bgr) de cada trecho (Q3.2)."""
import json
from pathlib import Path

import cv2
import numpy as np

TRECHOS = ["seg1", "seg2"]
ALT, LARG = 80, 160  # tamanho de cada quadradinho de cor (pixels)

linhas = []
for seg in TRECHOS:
    meta = json.loads(Path(f"saidas/{seg}/meta.json").read_text(encoding="utf-8"))
    linha = np.full((ALT, 120 + LARG * 3, 3), 255, np.uint8)  # fundo branco (até 3 grupos: T-2, T0, T1)
    cv2.putText(linha, seg, (10, ALT // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    for i, (time_, bgr) in enumerate(sorted(meta["times_bgr"].items())):
        x0 = 120 + i * LARG
        linha[:, x0:x0 + LARG - 10] = bgr  # pinta o quadradinho com a cor do centróide
        cv2.putText(linha, f"T{time_}", (x0 + 5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    linhas.append(linha)

Path("figuras").mkdir(exist_ok=True)
cv2.imwrite("figuras/q3_2_paleta_times.jpg", np.vstack(linhas))
print("Salvo: figuras/q3_2_paleta_times.jpg")
