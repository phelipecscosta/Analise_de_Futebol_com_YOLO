"""Compara execuções do detectar_rastrear.py (Q2.1 e Q2.3).

Lê saidas/testes/<execução>/meta.json e tracks.csv e calcula, para cada execução:
fps de processamento, jogadores por quadro, % de quadros com bola e
% de quadros com mais de uma candidata a bola (indicador de falso positivo).
"""
import json
from pathlib import Path

import pandas as pd

PASTA_TESTES = Path("saidas/testes")

linhas = []
for pasta in sorted(p for p in PASTA_TESTES.iterdir() if (p / "meta.json").exists()):
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    tracks = pd.read_csv(pasta / "tracks.csv")
    n = meta["n_frames"]  # total de quadros processados

    pessoas = tracks[tracks["classe"] != "bola"]
    bolas = tracks[tracks["classe"] == "bola"]

    # Jogadores por quadro: conta as detecções por quadro; quadros sem ninguém contam como 0
    jog_por_quadro = pessoas.groupby("frame").size().reindex(range(n), fill_value=0)

    # Candidatas a bola por quadro (o script guarda até 5 por quadro)
    bolas_por_quadro = bolas.groupby("frame").size().reindex(range(n), fill_value=0)

    linhas.append({
        "execucao": pasta.name,
        "modelo": meta["modelo"],
        "imgsz": meta["imgsz"],
        "conf_bola": meta["conf_bola"],
        "fps_proc": round(meta["fps_processamento"], 1),
        "jog_por_quadro": round(jog_por_quadro.mean(), 1),
        "%_quadros_com_bola": round(100 * (bolas_por_quadro > 0).mean(), 1),
        "%_quadros_>1_bola": round(100 * (bolas_por_quadro > 1).mean(), 1),
        "conf_media_bola": round(bolas["conf"].mean(), 3) if len(bolas) else None,
    })

tabela = pd.DataFrame(linhas)
print(tabela.to_string(index=False))

# Salva a tabela para usar no README (os números do README devem vir daqui)
tabela.to_csv(PASTA_TESTES / "comparacao_modelos.csv", index=False)
print(f"\nTabela salva em {PASTA_TESTES / 'comparacao_modelos.csv'}")
