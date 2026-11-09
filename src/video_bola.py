"""Vídeo de conferência da bola: candidatas do YOLO x escolha do Kalman (Q4.1).

Legenda no vídeo:
  círculo VERDE   = bola aceita pelo gating (detecção confirmada)
  círculo LARANJA = bola "chutada" pelo Kalman (sem detecção aceita)
  ponto VERMELHO  = candidatas do YOLO (inclusive falsos positivos rejeitados)
Uso: python src/video_bola.py seg1 60   (trecho, segundos iniciais a gravar)
"""
import sys
from pathlib import Path

import cv2
import pandas as pd

seg = sys.argv[1] if len(sys.argv) > 1 else "seg1"
segundos = float(sys.argv[2]) if len(sys.argv) > 2 else 60
pasta = Path("saidas") / seg

tracks = pd.read_csv(pasta / "tracks.csv")
cands = tracks[tracks["classe"] == "bola"].groupby("frame")
bola = pd.read_csv(pasta / "bola.csv").set_index("frame")

cap = cv2.VideoCapture(f"dados/videos/{seg}/{seg}_30fps.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
W, H = int(cap.get(3)), int(cap.get(4))
saida = pasta / "conferencia_bola.mp4"  # .mp4 é ignorado pelo Git
out = cv2.VideoWriter(str(saida), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

f = 0
while f < segundos * fps:
    ok, img = cap.read()
    if not ok:
        break
    # Candidatas do YOLO (pontos vermelhos)
    if f in cands.groups:
        for c in cands.get_group(f).itertuples():
            cv2.circle(img, (int(c.px), int(c.py)), 3, (0, 0, 255), -1)
    # Escolha do Kalman (verde = detectada, laranja = prevista)
    if f in bola.index:
        b = bola.loc[f]
        cor = (0, 255, 0) if b["fonte"] == "detectada" else (0, 165, 255)
        cv2.circle(img, (int(b["px"]), int(b["py"])), 12, cor, 2)
    cv2.putText(img, f"{seg}  quadro {f}  {f/fps:5.1f}s", (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    out.write(img)
    f += 1

cap.release()
out.release()
print(f"Salvo: {saida}  ({f} quadros)")
