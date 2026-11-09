"""Desenha as linhas do campo (via H0·Gt inversa) sobre cada quadro (Q4.3).

Se as linhas amarelas acompanham as linhas reais do gramado, a projeção está boa;
se escorregam, há deriva ou falha na estimativa do movimento da câmera.
Uso: python src/video_grade.py seg1
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, "src")
from campo import COMPRIMENTO, LARGURA, _GA_Y0, _GA_Y1, _PA_Y0, _PA_Y1  # noqa: E402

seg = sys.argv[1] if len(sys.argv) > 1 else "seg1"
pasta = Path("saidas") / seg
H0 = np.array(json.loads((pasta / "calibracao.json").read_text(encoding="utf-8"))["H0"])
G = np.load(pasta / "camera.npy")

# Segmentos das linhas do campo, em metros
L, W = COMPRIMENTO, LARGURA
segs = [[(0, 0), (L, 0)], [(L, 0), (L, W)], [(L, W), (0, W)], [(0, W), (0, 0)],   # contorno
        [(L / 2, 0), (L / 2, W)]]                                                   # meio-campo
for x0, s in ((0, 1), (L, -1)):                                                     # áreas
    for prof, y0, y1 in ((16.5, _GA_Y0, _GA_Y1), (5.5, _PA_Y0, _PA_Y1)):
        xf = x0 + s * prof
        segs += [[(x0, y0), (xf, y0)], [(xf, y0), (xf, y1)], [(xf, y1), (x0, y1)]]
ang = np.linspace(0, 2 * np.pi, 40)                                                  # círculo central
circ = np.c_[L / 2 + 9.15 * np.cos(ang), W / 2 + 9.15 * np.sin(ang)]
segs += [[circ[i], circ[i + 1]] for i in range(len(circ) - 1)]


def amostrar(a, b, n=20):
    """Divide cada segmento em n pontos (a perspectiva curva as retas longas na tela)."""
    a, b = np.array(a, float), np.array(b, float)
    return a + (b - a) * np.linspace(0, 1, n)[:, None]


cap = cv2.VideoCapture(f"dados/videos/{seg}/{seg}_30fps.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
W_img, H_img = int(cap.get(3)), int(cap.get(4))
out = cv2.VideoWriter(str(pasta / "conferencia_grade.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W_img, H_img))

f = 0
while True:
    ok, img = cap.read()
    if not ok or f >= len(G):
        break
    Hinv = np.linalg.inv(H0 @ G[f])                     # metros → pixels do quadro f
    for a, b in segs:
        pts = cv2.perspectiveTransform(amostrar(a, b).reshape(-1, 1, 2), Hinv).reshape(-1, 2)
        pts = np.clip(pts, -1e4, 1e4).astype(np.int32)
        cv2.polylines(img, [pts], False, (0, 255, 255), 2)
    cv2.putText(img, f"{seg}  {f / fps:5.1f}s", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    out.write(img)
    f += 1

cap.release()
out.release()
print(f"Salvo: {pasta / 'conferencia_grade.mp4'}  ({f} quadros)")
