"""Localiza exemplos para a Q4.1: lacunas preenchidas pelo Kalman em que a bola
reapareceu PERTO da previsão (acerto) ou LONGE dela (o Kalman inventou)."""
import numpy as np
import pandas as pd

FPS, PERTO_PX, LONGE_PX = 30, 15, 80
b = pd.read_csv("saidas/seg1/bola.csv").sort_values("frame").reset_index(drop=True)

acertos, inventa = [], []
for i in range(1, len(b) - 1):
    # fim de uma lacuna: quadro previsto seguido de um quadro detectado
    if b.loc[i, "fonte"] == "kalman" and b.loc[i + 1, "fonte"] == "detectada":
        j = i
        while j > 0 and b.loc[j - 1, "fonte"] == "kalman":
            j -= 1                                    # início da lacuna
        if j == 0 or b.loc[j - 1, "fonte"] != "detectada":
            continue
        salto = np.hypot(b.loc[i + 1, "px"] - b.loc[i, "px"], b.loc[i + 1, "py"] - b.loc[i, "py"])
        item = (round(b.loc[j, "frame"] / FPS, 1), i - j + 1, round(salto, 1))
        if salto <= PERTO_PX:
            acertos.append(item)
        elif salto >= LONGE_PX:
            inventa.append(item)

print("ACERTOS (tempo s, quadros previstos, distância da previsão à bola reaparecida px):")
for a in sorted(acertos, key=lambda x: -x[1])[:8]:   # lacunas mais longas primeiro
    print("  ", a)
print("INVENTA (mesmo formato, maiores saltos primeiro):")
for a in sorted(inventa, key=lambda x: -x[2])[:8]:
    print("  ", a)
