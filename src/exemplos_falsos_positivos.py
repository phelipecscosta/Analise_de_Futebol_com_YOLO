"""Salva quadros com mais de uma candidata a bola (Q2.3).

Como só existe uma bola em jogo, quadros com 2+ candidatas contêm pelo menos
um falso positivo. Desenha todas as candidatas com sua confiança e salva em figuras/.
"""
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

EXECUCAO = Path("saidas/testes/v8m_1280")          # execução escolhida (base)
VIDEO = "dados/videos/seg1/seg1_30fps.mp4"         # mesmo vídeo usado na execução
SAIDA = Path("figuras")
N_EXEMPLOS = 6                                     # quantos quadros salvar

SAIDA.mkdir(exist_ok=True)
tracks = pd.read_csv(EXECUCAO / "tracks.csv")
bolas = tracks[tracks["classe"] == "bola"]

# Quadros com 2 ou mais candidatas a bola
contagem = bolas.groupby("frame").size()
quadros = contagem[contagem > 1].index.to_numpy()
print(f"{len(quadros)} quadros com mais de uma candidata a bola")

# Escolhe N quadros espalhados ao longo do trecho (não todos seguidos)
escolhidos = quadros[np.linspace(0, len(quadros) - 1, N_EXEMPLOS).astype(int)]

cap = cv2.VideoCapture(VIDEO)
for i, f in enumerate(escolhidos, start=1):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(f))   # vai direto ao quadro f
    ok, img = cap.read()
    if not ok:
        continue
    cands = bolas[bolas["frame"] == f].sort_values("conf", ascending=False)
    for rank, c in enumerate(cands.itertuples(), start=1):
        # Verde = candidata mais confiável; vermelho = demais
        cor = (0, 255, 0) if rank == 1 else (0, 0, 255)
        cv2.rectangle(img, (c.x1 - 6, c.y1 - 6), (c.x2 + 6, c.y2 + 6), cor, 2)
        cv2.putText(img, f"{rank}: {c.conf:.2f}", (c.x1, c.y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2, cv2.LINE_AA)
    cv2.putText(img, f"quadro {f} ({f/30:.1f}s) - {len(cands)} candidatas", (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    arq = SAIDA / f"q2_3_falso_positivo_{i}.jpg"
    cv2.imwrite(str(arq), img)
    print(f"Salvo: {arq}")
cap.release()
