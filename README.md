# Prática 3 — Futebol Analytics com YOLO

**Disciplina:** Visão Computacional — VC001 · CESAR School
**Aluno:** Phelipe Calado de Souza Costa (individual)

Pipeline que, a partir de um vídeo de transmissão do YouTube, **detecta** e **rastreia** jogadores e bola (YOLOv8 + ByteTrack), **separa os times** pela cor da camisa (K-Means), **projeta as posições no campo em metros** (homografia + compensação do movimento de câmera) e calcula **posse, distância, passes e eXP** (expected pass), com **validação manual dos passes**.


---

## 1. Vídeo utilizado

| Item | Valor |
|---|---|
| Jogo | Flamengo 2 × 1 Criciúma — Campeonato Brasileiro 2024, 18ª rodada (20/07/2024), Estádio Mané Garrincha |
| URL | https://www.youtube.com/watch?v=kNBc1yj454w |
| Trecho 1 (`seg1`) | 13:50 → 16:20 do vídeo (duração real após corte: 148,0 s) |
| Trecho 2 (`seg2`) | 32:17 → 33:11 do vídeo (duração real após corte: 52,0 s) |
| Total analisado | 200 s (3 min 20 s) |
| Vídeo de resultado (fora do repositório) | https://drive.google.com/file/d/1UqvgUFOxPPiWvCTfKOv8fh-daFyoogDJ/view?usp=sharing |

O vídeo **não é versionado** (`.gitignore` bloqueia `*.mp4` e `dados/videos/`). Uso exclusivamente acadêmico; apenas os trechos acima foram baixados.

---

## 2. Ambiente

- Windows 11, Python 3.11.4 (venv), VS Code
- GPU NVIDIA RTX 3060 Laptop (6 GB), PyTorch 2.11 + CUDA 12.8
- ffmpeg 9.0.2; dependências em `requirements.txt`
- Variável `PYTHONUTF8=1` (evita erros de codificação no console do Windows)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements.txt
```

---

## 3. Estrutura do repositório

```
src/                      código (base: github.com/eron93br/vc-20262-p3 + scripts e alterações autorais)
saidas/seg1, saidas/seg2  CSV/JSON de cada trecho (tracks, bola, calibração, métricas, passes, eXP)
saidas/testes/            comparação de modelos YOLO (Parte 2) e testes de k=3 (Parte 3)
saidas/*.csv|txt          tabelas consolidadas (IDs, Kalman, sensibilidade, validação)
figuras/                  figuras das respostas (q2_*, q3_*, q4_*, q5_*)
saidas/segN/figuras/      mapas de calor, passes, posse, calibração e superfície de eXP
saidas/segN/passes_anotados.csv  anotação manual dos passes (validação)
DECLARACAO_IA.md          declaração de uso de IA
```

### Pipeline e comandos executados

```powershell
# Parte 1 — aquisição (um trecho por pasta) e conversão para 30 fps
python src\baixar_video.py "https://www.youtube.com/watch?v=kNBc1yj454w" --inicio 13.8333 --fim 16.3333 --saida dados\videos\seg1
python src\baixar_video.py "https://www.youtube.com/watch?v=kNBc1yj454w" --inicio 32.2833 --fim 33.1833 --saida dados\videos\seg2
ffmpeg -i dados\videos\segN\segN.mp4 -vf fps=30 -c:v libx264 -preset veryfast -crf 18 -an dados\videos\segN\segN_30fps.mp4

# Parte 2 — comparação de modelos (seg1, 0–30 s)
python src\detectar_rastrear.py --video dados\videos\seg1\seg1_30fps.mp4 --saida saidas\testes\v8s_1280 --modelo yolov8s.pt --imgsz 1280 --inicio 0 --fim 0.5
python src\detectar_rastrear.py --video dados\videos\seg1\seg1_30fps.mp4 --saida saidas\testes\v8m_1280 --modelo yolov8m.pt --imgsz 1280 --inicio 0 --fim 0.5
python src\detectar_rastrear.py --video dados\videos\seg1\seg1_30fps.mp4 --saida saidas\testes\v8m_640  --modelo yolov8m.pt --imgsz 640  --inicio 0 --fim 0.5
python src\detectar_rastrear.py --video dados\videos\seg1\seg1_30fps.mp4 --saida saidas\testes\v8m_1280_cb025 --modelo yolov8m.pt --imgsz 1280 --conf-bola 0.25 --inicio 0 --fim 0.5
python src\comparar_modelos.py
python src\exemplos_falsos_positivos.py

# Parte 3 — detecção + rastreamento + times (configuração final), alinhamento e diagnóstico
python src\detectar_rastrear.py --video dados\videos\segN\segN_30fps.mp4 --saida saidas\segN --modelo yolov8m.pt --imgsz 1280 --k 3
python src\alinhar_times.py
python src\paleta_times.py
python src\estatisticas_ids.py
python src\diagnostico_ids.py

# Parte 4 — bola e homografia
python src\bola_kalman.py --saida saidas\segN --ruido-processo 30 --max-lacuna 6 --mediana 7
python src\video_bola.py segN 60
python src\homografia.py calibrar --saida saidas\segN --pontos <marcos visíveis no frame0>
python src\homografia.py camera   --saida saidas\segN
python src\homografia.py projetar --saida saidas\segN
python src\video_grade.py segN
python src\deriva_projecao.py

# Parte 5 — métricas, sensibilidade e validação
python src\metricas.py --saida saidas\segN --ataque-time0 direita
python src\sensibilidade_raio.py
python src\validar_passes.py --saida saidas\segN --anotado saidas\segN\passes_anotados.csv
python src\validacao_grade.py

# Parte 6 — eXP (seg1 + passes do seg2)
python src\xpass.py --saida saidas\seg2
python src\xpass.py --saida saidas\seg1 --extra saidas\seg2\passes_features.csv --what-if
```

### Alterações autorais no código de base

| Arquivo | Alteração | Motivo |
|---|---|---|
| `classificador_times.py` | Descritor de cor usa **só pixels coloridos** (S ≥ 70, V ≥ 60) | Flamengo e Criciúma compartilham preto/branco; a média de todos os pixels juntava os dois times |
| `bola_kalman.py` | Parâmetro `--ruido-processo` exposto e **filtro de mediana** pós-Kalman (`--mediana`) | O Kalman padrão não acompanhava chutes/passes e "saltava" para falsos positivos |
| `homografia.py` | **Teste de plausibilidade** do movimento de câmera entre quadros (`_salto_px`, plano A/B/C) | Homografias degeneradas (poucos pontos casados) esticavam o campo e contaminavam os quadros seguintes |
| Novos | `comparar_modelos.py`, `exemplos_falsos_positivos.py`, `paleta_times.py`, `alinhar_times.py`, `estatisticas_ids.py`, `diagnostico_ids.py`, `video_bola.py`, `video_grade.py`, `deriva_projecao.py`, `sensibilidade_raio.py`, `validacao_grade.py` | Experimentos, diagnóstico e figuras das respostas |

---

## 4. Respostas

### Parte 1 — Aquisição

**Q1.1 — Escolha do jogo e do trecho**

Critérios:

- De preferência 3 a 5 minutos contínuo na câmera principal (plano aberto) e sem replays/cortes.
- **Uniformes diferentes** entretimes e em relação ao árbitro (para o K-Means separar os times).
1. **Linhas do campo visíveis** no primeiro quadro (meio-campo, círculo central ou grande área), para calibrar a homografia.
2. **Luz uniforme**, sem metade do campo na sombra.

Escolha e justificativa:

- **Flamengo x Criciúma - 18ª Rodada do Campeonato Brasileiro - 20/07/2024**

Link do vídeo: https://www.youtube.com/watch?v=kNBc1yj454w

- Conseguir um trecho de 3 a 5 minutos contínuo na câmera principal (plano aberto) é extremamente difícil, principalmente pelo fato de os jogos modernos terem demandas comerciais de exibição de patrocínios ou mudanças de câmera para reter a atenção. Jogos mais antigos talvez não tenham este problema, porém têm a resolução menor. Há jogos menos importantes que haveriam menor apelo comercial ou de técnicas de reter a atenção, sendo que são mais raros de encontrar por uma pesquisa genérica do YouTube. A solução portanto foi focar em obter os trechos mais longos possíveis na câmera principal (plano aberto) da mesma partida, cortar estes trechos e os juntar para se conseguir um tempo razoável entre 3 e 5 minutos.


**Q1.2 — Resolução, fps, quadros e custo**

| Trecho | Resolução | fps (original → usado) | Duração | Quadros processados |
|---|---|---|---|---|
| seg1 | 1280×720 | 60 → 30 | 148,0 s | 4.441 |
| seg2 | 1280×720 | 60 → 30 | 52,0 s | 1.561 |
| **Total** | | | **200 s** | **6.002** |

- - Processamento com YOLOv8m, imgsz 1280, na RTX 3060 (fonte: `fps_processamento` em `saidas/seg1/meta.json` e `saidas/seg2/meta.json`): seg1 a 14,0 fps (318 s), seg2 a 13,5 fps (116 s); total de 6.002 quadros em 433 s (7,2 min), média de 13,9 fps. O tempo inclui a gravação do vídeo anotado e a predição extra da bola.

Vídeo original possuía 60 fps que foi reduzido para 30 fps, trazendo ganho em reduzir pela metade o custo computacional. O maior risco de se reduzir seria em penalizar a rastreabilidade da bola, porém calculou-se que para passes fortes (~25 m/s), o deslocamento entre um quadro e outro seria estimado em até 0,8m, distância que o filtro de Kalman que prever a posição a partir da velocidade, consegue acompanhar. Além disto, os parâmetros dos scripts medidos em quadros (ex.: `--max-lacuna`, `--calib-frames`) passam a corresponder a intervalos de tempo maiores: a 30 fps, --max-lacuna 15 equivale a 0,5 s, contra apenas 0,25 s a 60 fps.


### Parte 2 — Detecção

**Q2.1 — Comparação de modelos** (Parâmetros: seg1, 0–30 s, 900 quadros; fonte: `saidas/testes/comparacao_modelos.csv`)

* ** YOLOv8:**
  * 5 tamanhos: n (nano), s (small), m (medium), l (large) e x (extra-large).
  * Quanto maior, mais “neurônios” (parâmetros) e mais detalhes enxerga, porém, fica mais lento.

* **Parâmetros:**
  * imgsz: Tamanho da imagem a ser analisada (640 ou 1280).
  * conf-bola: Índice de confiança mínimo (0 a 1) para se rotular uma bola.

| Execução | Modelo | imgsz | conf-bola | fps | Jogadores/quadro | % quadros com bola | % quadros com >1 bola | Conf. média bola |
|---|---|---|---|---|---|---|---|---|
| v8s_1280 | yolov8s | 1280 | 0,10 | 18,1 | 14,9 | 74,8 | 19,6 | 0,307 |
| **v8m_1280** | **yolov8m** | **1280** | **0,10** | 12,1 | 14,3 | **76,8** | 15,8 | 0,379 |
| v8m_640 | yolov8m | 640 | 0,10 | 23,1 | 12,5 | 47,2 | 3,3 | 0,365 |
| v8m_1280_cb025 | yolov8m | 1280 | 0,25 | 13,3 | 14,3 | 56,7 | 4,0 | 0,499 |

Configuração escolhida: **yolov8m, imgsz 1280, conf-bola 0,10**.

**Justificativa**

* Buscou-se o melhor equilíbrio entre velocidade de processamento e qualidade
* Vídeo original tem 1280 x 720, sendo a bola 8 - 10 px. Reduzir pela metade (640), iria para 4 - 5 px, praticamente um ponto apenas.
* Limiar baixo de 0,10 capta mais bolas com o custo de vir detecções indesejáveis mas que seriam filtradas depois (melhor ter um falso positivo e repois o remover pelo filtro de Kalman, do que perder a detecção da bola já no início)
* Esta configuração aprsentou a melhor cobertura de bola (76,8%), com menos "lixo" detectado (15,8% sendo a segunda melhor detecção) e a segunda melhor confiança (0,379) com o custo mais baixo de todos (12,1 fps)


**Q2.2 — Por que a bola é mais difícil**

* Ocupa poucos pixels. A bola tem entre 8 e 10 px e um quadro com 1280px, o que significa 0,6% a 0,8%.
* Sofre oclusão constantemente (jogadores, chuteiras etc) e pode criar borrão de movimento.
* Sua classe COCO é genérica "sports ball".
* Facilmente confundida com chuteiras brancas, marcas de pênalti, objetos brancos no gramado.
* Ahmad Yousef et al. (2025, Tabela 2): F1 da bola ≈ 0,31 sem Kalman (0,958 com). Já para jogaores ≈ 0,93.

**Q2.3 — Efeito de imgsz e conf-bola; falsos positivos** (figuras `figuras/q2_3_falso_positivo_1..6.jpg`)

* Usando imgsz 640, foi 2 vezes mais rápidos, porém confiança caiu de 76,8% para 47,2% dos quadros (−29,6 p.p. (pontos percentuais), uma perda relativa de 38,5%), e o número médio de pessoas detectadas caiu de 14,3 para 12,5 por quadro (−1,8 jogador por quadro).
* Usando conf-bola 0,25, os quadros com falsos candidatos caem de 15,8% para 4,0%, porém a bola sumia em −20 p.p. dos quadros.
* Os falsos positivos observados para a bola:
  * Marca do pênalti
  * Cabelos claros
  * Chuteiras brancas ou amarelas
  * Bandeira do bandeirinha
  * Reflexo de luz no gramado
  * Objetos (copo) fora do campo
* A confiança sozinha não separa bola dos outros falsos positivos, sendo necessario adicionar uma filtragem por coerência temporal.


**Q2.4 (opcional)** — não realizada; ver Trabalhos futuros.

### Parte 3 — Rastreamento e times

**Q3.1 — Trocas de ID** (fonte: `saidas/estatisticas_ids.csv`, `src/diagnostico_ids.py`)

| Trecho | Pessoas máx. simultâneas | IDs distintos | IDs novos/min | Vida mediana do ID (s) | % IDs < 1 s |
|---|---|---|---|---|---|
| seg1 | 27 | 1.313 | 532,2 | 0,3 | 67,5 |
| seg2 | 24 | 585 | 674,6 | 0,1 | 74,0 |

O ByteTrack conecta as detecções de pessoas de um quadro ao seguinte, atribuindo um número fixo a cada pessoa (`track_id`). Caso a detecção se perca (por exemplo devido a obstrução), ele atribui um novo id quando a pessoa reaparece.

Assistindo ao `rastreado.mp4`, observou-se que:
* Rótulos sumiam para:
  * Oclusão: um jogador passa na frente de outro;
  * Foco de luz forte: o jogador “estoura” para branco e o detector perde confiança;
  * Movimento rápido da câmera: os rótulos piscam ou desaparecem.
* Casos de aglomeração (escanteio, disputa) foi bem tratado.
* Seg1: os IDs < 1 s são 68% dos IDs, mas só **5,7% das detecções**; são menores (43 px × 72 px), de menor confiança (0,49 × 0,82) e ficam no alto da imagem (torcida/lado oposto). Assim 37,5% deles foram rotulados como Flamengo que eram **torcedores de vermelho e preto**.
* Fragmentação real de jogadores na faixa de 1–5 s (284 IDs, 26,5% das detecções).
* A maior parte dos IDs curtos era de pessoas fora do jogo, eliminadas pela projeção, e que a fragmentação real de jogadores, embora existente, é uma entre várias causas dos erros de passe.
* Decisão tomada: não ajustar o ByteTrack (pois a projeção descarta quem está fora do campo); um gatilho para revisar seria a validação de passes.

**Q3.2 — K-Means de cor** (figuras `figuras/q3_2_paleta_times_k2_original.jpg` e `figuras/q3_2_paleta_times.jpg`)

* Observou-se que:
  * k=2 com média de todos os pixels: separou **"azul" (arbitragem + goleiro) × "todo o resto"**; os dois times caíram no mesmo grupo (cinza).

* A causa foi devido aos uniformes de todos eles possuírem preto e branco, mesmo que em posições diferentes.
* a correção foui usar só pixels coloridos, estabilizando os rótulos do Flamengo e Criciúma.
* O script numera como time 0 o maior grupo na calibração, assim a numeração inverteu entre trechos. `alinhar_times.py` aplica a regra "matiz mais próximo do vermelho = Flamengo" , de forma que Flamengo = 0 e Criciúma = 1).


**Q3.3 — k=3** (`saidas/testes/v8m_1280_k3`, `saidas/testes/v8m_1280_k3_cor`)

Com k=3 obteve-se melhores resultados, isolando arbitragem e goleiro (ambos com azul predominante) no grupo "outros", que pode ser considerando um ganho. Porém. isto também fez com que o goleiro fique fora do seu time e recuo para o goleiro vira "passe errado" na detecção. E pessoas fora do campo oscilaram entre grupos.


### Parte 4 — Bola e homografia

**Q4.1 — Cobertura da bola antes/depois do Kalman** (fonte: `saidas/resumo_kalman.txt`)

| Trecho | Quadros com candidata (YOLO) - "Antes" | Aceitas após gating | Preenchidas pelo Kalman | Cobertura final - "Depois"|
|---|---|---|---|---|
| seg1 | 3.611 / 4.441 (81,3%) | 3.225 | 1.052 | 96,3% |
| seg2 | 1.314 / 1.561 (84,2%) | 1.132 | 384 | 97,1% |

Parâmetros finais: `--ruido-processo 30 --max-lacuna 6 --mediana 7`.

* Trechos em que inventa:
  * Seg1:
    * 0:00–0:03: Bola ausente, o círculo de detecção alterna entre a marca do pênalti, chuteiras e a cabeça de um jogador de cabelo branco (`figuras\4_1_kalman_inventa.png`).
    * 0:16–0:18: Lance de bola alta para a área, o círculo de detecção erra a trajetória e reaparece na marca do pênalti (`figuras\4_2_kalman_inventa.png`).
* Trehcos que acerta:
  * 0:04 a 0:15 e 0:19 a 0:30 (`figuras\4_1_kalman_acerta.png`).

Pontos-chave:
* Cobertura alta **por construção** (o filtro prevê e reinicia na candidata mais confiável) — não equivale a acerto; o F1 de Ahmad Yousef et al. foi medido contra gabarito.
* Kalman padrão (Q=1, lacuna 15): não aceitava chutes/passes (velocidade constante), rejeitava a bola real após o chute, reiniciava na marca do pênalti.
* Q=30 + lacuna 6: segue chutes, mas salta para chuteiras; + mediana 7: mais estável.
* Falhas restantes (vídeo `conferencia_bola.mp4`): aglomeração (chuteiras), luz forte, bola alta, marca do pênalti.
* Conclusão: o gargalo é o detector COCO; o Kalman de velocidade constante tem limitações no futebol.

**Q4.2 — Calibração e erro de reprojeção** (fonte: `saidas/segN/calibracao.json`; figura `saidas/segN/calibracao_grade.jpg`)

| Trecho | Marcos | Erro de reprojeção (m) |
|---|---|---|
| seg1 | ga_esq_sup, ga_esq_inf, canto_sup_esq, penalti_esq, pa_esq_sup, pa_esq_inf | 0,05–0,14 (máx.: penalti_esq) |
| seg2 | canto_sup_dir, ga_dir_sup, ga_dir_inf, ga_dir_sup_linha, penalti_dir, pa_dir_sup, pa_dir_inf | 0,02–0,41 (máx.: ga_dir_inf) |

* Marcos com mais erro:
  * ga_dir_inf, no seg2: 0,41 m, foi o maior de todos.
  * penalti_esq, no seg1: 0,14 m, foi o maior do seg1.

* Interpretação:
  * Marcos “inf” (na borda de baixo da imagem) estão mais pertos da câmera, onde a distorção da lente é maior. A homografia supõe uma câmera sem distorção. Por isso ela não consegue encaixar esses pontos tão bem.
  * Marca do pênalti é apenas um "ponto" sem cruzamento de linhas, dificultando até erro por um clique menos preciso que numa quina, onde duas linhas se encontram.

**Legenda dos marcos** (definidos em [`src/campo.py`](src/campo.py), dicionário `MARCOS`; campo padrão FIFA de 105 × 68 m)

Convenção dos nomes: `ga`/`pa` = grande/pequena área · `esq`/`dir` = gol da esquerda/direita da imagem · `sup`/`inf` = lado de cima (lateral distante da câmera)/de baixo (lateral próxima) · `_linha` = ponto em que a área encontra a linha de fundo (sem `_linha` = quina da frente da área). Origem (0, 0) no canto superior esquerdo do campo visto na imagem; x ao longo do comprimento, y ao longo da largura.

| Marco | Posição (x, y) em metros | Onde fica |
|---|---|---|
| `canto_sup_esq` | (0; 0) | Canto do campo: linha de fundo esquerda × lateral de cima |
| `canto_sup_dir` | (105; 0) | Canto do campo: linha de fundo direita × lateral de cima |
| `ga_esq_sup` | (16,5; 13,8) | Quina de cima da frente da grande área esquerda |
| `ga_esq_inf` | (16,5; 54,2) | Quina de baixo da frente da grande área esquerda |
| `ga_dir_sup` | (88,5; 13,8) | Quina de cima da frente da grande área direita |
| `ga_dir_inf` | (88,5; 54,2) | Quina de baixo da frente da grande área direita |
| `ga_dir_sup_linha` | (105; 13,8) | Lateral de cima da grande área direita × linha de fundo |
| `pa_esq_sup` | (5,5; 24,8) | Quina de cima da frente da pequena área esquerda |
| `pa_esq_inf` | (5,5; 43,2) | Quina de baixo da frente da pequena área esquerda |
| `pa_dir_sup` | (99,5; 24,8) | Quina de cima da frente da pequena área direita |
| `pa_dir_inf` | (99,5; 43,2) | Quina de baixo da frente da pequena área direita |
| `penalti_esq` | (11; 34) | Marca do pênalti do gol esquerdo |
| `penalti_dir` | (94; 34) | Marca do pênalti do gol direito |


**Q4.3 — Composição H0·Gt e deriva** (figura `figuras/q4_3_deriva_projecao.png`; vídeo de conferência `video_grade.py`)

- Composição `H0 · G_t`
    - Analisa um ponto de qualquer quadro em distância sempre relativa para o primeiro quadro (0).
    - Torna possível avaliar métricas de distância, velocidade, raio de posse e eXP.
    - Unidades: metro e segundo
- Componente G_t: Faz o referenciamento de um ponto em um dado quadro t para a posição que estaria no quadro 0 (de referência)
- Componente H0: Converte o ponto do quadro 0 para metros, calculado uma única vez.

- Erro ao longo do clipe (deriva):
    - O `G_t` é estimado quadro a quadro, e **cada estimativa tem um pequeno erro associado**. Se a câmera se move muito, o script troca de quadro de referência (quadro-chave), e **os erros se somam**: é a **deriva**. Quanto mais longe a câmera vai do quadro 0, maior será o erro acumulado.

- Correção (re-aconramento de calibração): A raiz do problema está em depender de um único H0 para o trecho inteiro.
Possíveis soluções:
    - Fazer acoragens periódicas (manualmente), criando novos pontos de calibração, podendo ser periodicamente espaçado ou sempre que a câmera mostrar uma região nova.
    - Homografia por quadro (automática, a solução da indústria). Usa-se um modelo já treinado para **detectar os pontos do campo** (ex.: cruzamentos de linhas, quinas das áreas, círculo central) em **todo** quadro e calcular a homografia diretamente. Elimina a **deriva**, pois cada quadro é calibrado de forma independente.


**Q4.4 — Pé do jogador × centro do box; bola no ar**

- Homografia: Técnica para correção de uma vista de um plano inclinado para traduzir em uma vista ortogonal.
- Para a homografia funcinar no caso da partida de futebol, ela tem que avaliar os pontos que estão sob o plano do gramado.
- Os pés tocam o chão, logo, sob o plano do gramado e a projeção ocorre sem grandes distorções. Caso fosse no centro do box, aproximadamente na altura da cintura e assim algo em torno de 1m acima do chão, a homografia iria calcular este ponto como se estivesse “tocando” no gramado e iria fazer uma projeção mais distante do que o jogador realmente está.#
- Para a bola:
    - Bola rolando: O centro é pequeno, em torno de 10cm do chão, com um erro desprezível e a projeção funciona.
    - Bola lançada: Quando a bola é lançada alta o suficiente a ponto de do fundo deixar de ser o gramado, nota-se q**uedas no gráfico de deriva** (bola “fora do campo”).

### Parte 5 — Métricas

**Q5.1 — Posse, distância, velocidade** (fonte: `saidas/segN/metricas_times.json` e `saidas/segN/metricas_jogadores.csv`; raio de posse 2 m; 0 = Flamengo, 1 = Criciúma)

| Trecho | Posse Fla | Posse Cri | Passes Fla (certos) | Passes Cri (certos) | Distância Fla (m) | Distância Cri (m) |
|---|---|---|---|---|---|---|
| seg1 | 58,1% | 41,9% | 22 (13) | 26 (15) | 2.808,3 | 2.438,5 |
| seg2 | 12,5% | 87,5% | 5 (0) | 11 (8) | 1.022,4 | 766,3 |

| Trecho | Time | Velocidade máxima (km/h) | Velocidade média típica (m/min) |
|---|---|---|---|
| seg1 | Flamengo | 41,4 (track 5981, rastro de 4 s) | 221 (mediana de 25 rastros ≥ 10 s) |
| seg1 | Criciúma | 33,7 (track 9000, rastro de 17 s) | 202 (mediana de 18 rastros ≥ 10 s) |
| seg2 | Flamengo | 35,1 (track 2057, rastro de 2 s) | 195 (mediana de 6 rastros ≥ 10 s) |
| seg2 | Criciúma | 29,5 (track 1664, rastro de 2 s) | 189 (mediana de 5 rastros ≥ 10 s) |

Fonte: `saidas/segN/metricas_jogadores.csv`. Velocidade média típica = mediana de `vel_media` dos rastros com pelo menos 10 s (os rastros curtos, fragmentos de ID, são ruidosos).

**Interpretação:**

* Velocidade: Exibem valores bem acima do que seria fisicamente plausível. A velocidade média calculada para os jogadores ficou entre 189 e 221 m/min, o que é 1,6 a 1,8 vez a de referência (120 m/min e 10 a 12 km em 90 min). A velocidade máxima chegou a 41,4 km/h, acima dos sprints de corredores de elite (cerca de 35 a 37 km/h).

**Possíveis causas:**
* O tremor da posição projetada, vindo da oscilação do bounding box e falhas da homografia (Q4.3), somado deslocamento, superestimando distância e velocidade. O script já descarta saltos acima de 12 m/s, mas os erros menores entram na soma. A distância total por time também é afetada pela fragmentação de IDs e pelos jogadores fora do quadro, que não são contabilizados.

**Possíveis melhorias:**
* Fazer uma suavização mais forte das trajetórias de cada jogador (filtro de mediana ou de Kalman).
* Homografia mais estável.
* Descarte de rastros curtos no cálculo das velocidades.


**Q5.2 — Sensibilidade ao raio de posse** (fonte: `saidas/sensibilidade_raio.csv`; figura `figuras/q5_2_sensibilidade_raio.png`)

| Trecho | Raio | Posse Fla | Passes |
|---|---|---|---|
| seg1 | 1 m | 42,2% | 29 |
| seg1 | 2 m | 58,1% | 48 |
| seg1 | 3 m | 54,7% | 55 |
| seg2 | 1 m | 7,1% | 10 |
| seg2 | 2 m | 12,5% | 16 |
| seg2 | 3 m | 27,5% | 20 |

* Raio de posse: É a distância máxima entre a bola e um jogador para considerar que ele está com a bola. Se essa distância for menor que o raio (em m), esse jogador é o dono da bola naquele quadro. Se ninguém estiver dentro do raio, ninguém tem a posse naquele quadro.

* Gráfico em `q5_2_sensibilidade_raio.png`


**Q5.3 — Validação manual dos passes** (fontes: `saidas/segN/passes_anotados.csv`, `saidas/validacao_passes_grade.csv`)

Regras de anotação:
1. Passe = toda ação intencional de enviar a bola a um companheiro, incluindo cabeceios, lançamentos, cruzamentos e cobranças de lateral.
2. Não conta: chute a gol, chutão sem alvo, bola que apenas esbarra no jogador.
3. `t_s` = primeiro quadro com espaço visível entre a chuteira (ou as mãos) e a bola.
4. `time` = time do passador (0 = Flamengo, 1 = Criciúma); recuo para o goleiro = passe do próprio time.
5. `sucesso` = 1 se um companheiro domina; 0 se o adversário intercepta ou a bola sai.

| Trecho | Detectados | Anotados | Casados | Precisão | Revocação | F1 | Acordo certo/errado |
|---|---|---|---|---|---|---|---|
| seg1 | 48 | 42 | 23 | 0,48 | 0,55 | 0,51 | 0,74 |
| seg2 | 16 | 16 | 10 | 0,62 | 0,62 | 0,62 | 0,80 |
| **Total** | **64** | **58** | **33** | **0,52** | **0,57** | **0,54** | — |

(raio 2 m, tolerância 1 s). Grade completa de raio × tolerância em `saidas/validacao_passes_grade.csv`.

Pontos-chave:
- Aumentar tolerância de 1 para 2 s acrescenta só mais 3 casamentos (de 33 para 36), logo, erro de tempo é marginal. Dominam passes falsos (~48% dos detectados) e perdidos (~43% dos reais).
- Raio 1 m: P 0,64 / R 0,43 / F1 0,51; 2 m: 0,52 / 0,57 / 0,54; 3 m: 0,49 / 0,64 / 0,56 . F1 quase constante: o teto vem de antes (bola, IDs, homografia).
- Causas: bola não detectada no momento do passe; bola "pulando" para chuteiras (erro detecção); fragmentação de IDs; goleiro no grupo "outros" (não conta como passe correto); erro de posição no meio-campo.
- Com 58 passes, a incerteza de cada métrica é da ordem de ±0,13 (IC 95%).

**Q5.4 — Direção de ataque; efeito de IDs e jogadores fora do quadro**

**Direção de ataque**

- **Está correta.** O script (`metricas.py`) estimou `{"0": "direita", "1": "esquerda"}`: o Flamengo (time 0) ataca para o gol da direita. Conferido nos vídeos nos dois trechos (ambos do 1º tempo).
- **O que poderia causar erro:** A heurística olha os jogadores mais extremos de cada time, que normalmente são os goleiros. Para este caso e com `k=3`, os goleiros caíram no grupo “outros” e ficaram fora dessa conta; o script acertou usando os jogadores de linha, mas isso pode ser frágil para casos de um trecho com um time todo recuado ou todo adiantado. Por segurança, a direção foi **fixada manualmente** com `-ataque-time0 direita`.

**Efeito das trocas de ID**

- **Distância:** A corrida de um mesmo jogador fica dividida em vários rastros, então a distância por jogador ficou subestimada e sem sentido. Além disso, os fragmentos curtos geraram velocidades falsas: as máximas de 35–41 km/h vieram de rastros de 2–4 s (Q5.1).
- **Passes:** se o jogador troca de ID enquanto tem a bola, o script enxerga uma “troca de dono” e conta um "passe dele para ele mesmo" e como sendo correto (mesmo time). Isso infla o número de passes e a precisão. O filtro de distância mínima de 3 m reduz, mas não elimina, esse efeito.

**Efeito dos jogadores fora do quadro**

- **Distância:** Enquanto o jogador está fora da imagem, ele não acumula distância. O total por time fica subestimado e depende de quanto tempo cada time apareceu.
- **Passes:** Se o receptor de um passe está fora do quadro, este passe é perdido ou é atribuído a quem estiver visível mais perto da bola. Isso contribui para a revocação baixa (0,57).

**Correções propostas**

1. **Reidentificação por aparência (re-ID):** Comparar a “aparência” de cada rastro (cor, número da camisa, silhueta) para unir fragmentos do mesmo jogador.
2. Ajustar o ByteTrack: Aumentar a memória do rastro (`track_buffer`) e usar as detecções de baixa confiança na segunda associação, reduzindo as quebras em oclusões.
3. **Regra contra “passe para si mesmo”:** Descartar trocas de dono entre dois rastros que não coexistem no tempo e estão na mesma posição, que é a assinatura de uma troca de ID.
4. **Normalizar por tempo visível:** Reportar distância por minuto em que o jogador aparece, em vez da soma bruta.
5. **Direção de ataque:** Definir manualmente por tempo de jogo, que é simples e confiável, ou usar um detector com classe goleiro.

### Parte 6 — eXP

**Q6.1 — Features × canais de Gomes et al. (2026)**

* eXP (expected pass): Probabilidade (de 0 a 1) de um passe ser completado com sucesso para um determinado contexto: distância, adversários no caminho, pressão etc.

* Features e os canais da Tabela 1 de Gomes et al. (2026):

| Feature (`xpass.py`) | O que mede | Canal relacionado |
| --- | --- | --- |
| `distancia` | Distância em metros da origem ao destino do passe | 3 (distância à bola) e 17 (distância ao início do evento) |
| `adversarios_na_linha` | Nº de adversários num “cone” ao longo da linha do passe; o cone alarga com a distância, porque o defensor tem mais tempo para chegar | 11 (defensores entre a bola e a célula) |
| `pressao_passador` | Nº de adversários a menos de 3 m do passador | Derivada do canal 2 (posição dos defensores), em volta da bola |
| `espaco_destino` | Distância do destino ao adversário mais próximo (satura em 10 m: “livre”) | Derivada do canal 2 (ocupação defensiva), em volta do destino |
| `progressao_x` | Quanto o passe avança em direção ao gol adversário | Relacionada aos canais 4 e 7 (geometria em relação ao gol) |
| `dist_destino_gol` | Distância do destino ao gol adversário | 4 (distância ao gol) |

- Limitação quanto a extração:
    - O SoccerMap recebe os **17 canais como mapas inteiros do campo** (17 × 104 × 68) e devolve uma **superfície** de probabilidade. No modelo, é resumido tudo em **6 números por passe**. A superfície de eXP que foi gerada é uma aproximação: o mesmo modelo, avaliado em cada ponto do campo.
    - O que não pode ser extraído e por quê:


        | Canais | Motivo |
        | --- | --- |
        | **8, 9: velocidade da bola** (x, y) | A bola falha em parte dos quadros (o Kalman “inventa” trechos), e **bola no ar** é projetada no lugar errado (a homografia só vale para o chão). Derivar a posição para obter velocidade **amplifica** esses erros |
        | **12–16: velocidade do portador, dos atacantes e dos defensores** | O tremor da projeção já infla a velocidade em ~2× (Q5.1), e a fragmentação de IDs quebra as trajetórias. Velocidades seriam mais ruído que sinal |
        | **1, 2 completos: posição de todos os jogadores** | A câmera mostra **só parte do campo**, então os jogadores fora do quadro não existem para o modelo. E os goleiros ficam no grupo “outros”, sem time |

        A causa comum: o artigo usa **dados de rastreamento profissional** (Gradient Sports), com **todos os 22 jogadores, sempre**, posições e velocidades medidas. Para o caso deste trabalho, tem-se um vídeo de **uma câmera de TV**, com cortes, oclusões e erro de projeção.

- Extraíveis, mas não implementados no xpass.py:
  - 5, 6, 7 (ângulos em relação ao gol) e 10 (atacantes entre a bola e a célula): são geometria pura sobre posições que já foi obtida, e dariam para acrescentar. O modelo atual simplesmente ignora os companheiros (só olha adversários).

**Q6.2 — Comparação de modelos** (fonte: `saidas/seg1/resultados_xp.csv`; 64 passes, 48 do seg1 + 16 do seg2, 56,2% certos)

| Modelo | AUC-ROC ↑ | Brier ↓ | Log-Loss ↓ |
|---|---|---|---|
| Baseline (distância) | 0,415 | 0,249 | 0,691 |
| Heurístico (β fixos) | 0,741 | 0,256 | 0,786 |
| Logístico (seus passes) | 0,801 | 0,167 | 0,531 |
| SoccerMap · Gomes et al. | 0,622 | 0,138 | 0,444 |

- O que muda com poucos passes:
    - **A incerteza se torna grande.:**Com 64 passes (36 certos, 28 errados), o intervalo de 95% da AUC fica em torno de **±0,11**, numa estimativa aproximada pelo método de Hanley & McNeil:
        - logístico: 0,80 → entre ~**0,69 e 0,91**;
        - baseline: 0,42 → entre ~**0,28 e 0,55**. O intervalo **inclui 0,5**, ou seja, não dá para afirmar que ele é diferente de um chute.
      - Para comparação, o artigo avaliou 6.973 passes: lá, uma diferença de 0,03 na AUC já é significativa; aqui, não.

**Q6.3 — Calibração** (figura `saidas/seg1/figuras/calibracao_xp.png`)

- Curva de calibração:
    - Responde: **“quando o modelo diz X% de chance, o passe dá certo X% das vezes?”**
    - Os passes são agrupados por faixa de probabilidade


**Análise média prevista × taxa observada**

* Logístico (verde):
  * É o mais calibrado
  * Média prevista 0,553 × observada 0,562, praticamente iguais.

* Heurístico (azul):
  * Foi otimista demais
  * 0,792 contra 0,562

* Baseline (laranja):
  * Calibrado na média, mas inútil.
  * Sem poder de separação; ~13 passes por ponto.

**Q6.4 — Superfície de eXP** (figura `saidas/seg1/figuras/superficie_xp_f67.png`)

- **superfície de eXP:** É um **“mapa de chances de passe” para um dado instante do jogo.**
    - Gradiente de cores: **Vermelho escuro** = chance alta (perto de 100%); **amarelo** = ~50%; **azul escuro** = chance baixa (perto de 0%).
        - Zona **azuis** em volta dos adversários são as “proibidas”.
    - Pontos coloridos: P**ontos vermelhos** são os adversários, os **azuis** os companheiros , e a **seta branca** é o passe que de fato ocorreu.
- **Limitações:**
  - Lançamentos de 60–70 m com eXP ≈ 1 são irreais (o modelo não conhece altura/velocidade da bola nem tempo de reação).


**Q6.5 — What-if e PAx** (fontes: `saidas/seg1/jogadores_xp.csv`, `saidas/seg1/what_if.csv`)

- what-if:
    - É uma **simulação “e se”** para cada **passe errado.**
    - O modelo pergunta *“e se o receptor estivesse alguns metros para o lado, o passe teria mais chance de dar certo?”*.
    - O destino do passe é deslocado **3, 4,5 e 6 m** em 16 direções, e o eXP é recalculado em cada posição.
    - O resultado é o **ganho, que seria** o eXP na melhor posição alternativa menos o eXP original.

**Resultado** (`saidas/seg1/what_if.csv`): ganho médio de **+0,33** no eXP; em **80%** dos passes errados, um reposicionamento de 3–6 m aumentaria o eXP em mais de 0,10.

- **PAx (passes acima do esperado):**
    - **Resultado de passes certos − soma dos eXP** dos passes de um jogador.
    - Se um jogador fez 4 passes cujos eXP somam 1,85 (ou seja, “o esperado” era acertar ~2) e acertou 3, o PAx dele é **+1,15**: acertou mais do que a dificuldade sugeria.
    - **Positivo** = acerta passes difíceis; **negativo** = erra passes fáceis.

| Track | Time | Passes | Certos | Soma eXP | PAx |
| --- | --- | --- | --- | --- | --- |
| 4029 | Criciúma | 4 | 3 | 1,85 | **+1,15** |
| 3374 | Criciúma | 2 | 2 | 0,91 | +1,09 |
| 6611 | Flamengo | 4 | 3 | 2,18 | +0,82 |

Não é possível afirmar se que algum jogador se destaca. O “4029” é um fragmento de rastro (IDs fragmentados, Q3.1), não um jogador. O mesmo jogador real pode estar dividido em vários IDs, e um ID pode até misturar jogadores. Além disso, 2 a 4 passes por “jogador” é pouco demais para separar habilidade de sorte.

**Limitações de tirar conclusões de um trecho curto**

O trecho analisado tem 3 min 20 s, enquanto que um jogo tem pelo menos 90 min:

* Amostra minúscula: 64 passes no total e 1 a 4 por jogador. Um único passe certo ou errado muda o PAx de um jogador em até ±1.
* Sem identidade dos jogadores: Os IDs do rastreador não correspondem a jogadores (não há leitura do número da camisa), então o PAx é por fragmento de rastro, não por pessoa.
* Rótulos ruidosos: “certo/errado” vem da detecção automática (precisão de 0,52; acordo certo/errado de ~0,76). O PAx herda esses erros.
* Contexto do trecho: 3 minutos oriundos da junção de 2 segmentos refletem momentos específicos (um time pressionando, outro recuado etc), não o padrão do jogo.

Em resumo: PAx e what-if são ferramentas úteis para análise tática pós-jogo, mas exigem jogos inteiros (ou vários jogos), identificação dos atletas e rótulos confiáveis. Num trecho curto, servem apenas para demonstrar o método, não para avaliar jogadores.

---

## 5. Limitações e trabalhos futuros

Os resultados formam uma cadeia de erros: detecção da bola -> posição projetada -> posse -> passes -> eXP. Cada etapa herda o erro da anterior, por isso nenhum ajuste de parâmetro no fim da cadeia (como o raio de posse) eleva o F1 dos passes acima de ~0,56. As propostas abaixo estão em ordem de impacto esperado.

### 5.1 Detector de bola específico para futebol

- **Limitação:** O YOLOv8 pré-treinado no COCO reconhece "sports ball" de forma genérica e não conhece a bola de futebol vista de cima, a 50 m. A bola faltou em ~16–19% dos quadros e houve falsos positivos em ~16% (chuteiras, marca do pênalti, cabeças claras, bandeira do bandeirinha). O Kalman não corrige isso: ele só escolhe entre as candidatas que o detector oferece.
- **Evidência:** em 3 de 6 quadros analisados (Q2.3) a bola real nem estava entre as candidatas; nos vídeos de conferência (Q4.1) o filtro "grudou" em chuteiras e na marca do pênalti.
- **Proposta:** ajuste fino (fine-tuning) do YOLO com um dataset de futebol do Roboflow Universe (classes *player, goalkeeper, referee, ball*, imagens de transmissão), ou uso de um detector de bola já treinado para futebol. Para a bola pequena, inferência por fatias (*slicing*): dividir o quadro em pedaços de 640×640 e analisar cada um separadamente, o que "amplia" a bola. Complementarmente, trocar o Kalman em tempo real por um rastreamento offline (olhar quadros anteriores e posteriores para remover detecções incoerentes e interpolar as lacunas).
- **Impacto esperado:** é o gargalo de maior efeito. Melhora diretamente a posse e a detecção de passes (revocação de 0,57 e precisão de 0,52) e, por consequência, os rótulos do eXP.

### 5.2 Homografia por quadro ou re-ancoragem da calibração

- **Limitação:** a calibração foi feita uma única vez no primeiro quadro, com marcos só da grande área. Quando a câmera mostra o meio-campo, a projeção extrapola e as linhas "escorregam"; a estimativa do movimento da câmera (ORB + RANSAC) também acumula erro (deriva) em um gramado degradado e com pouca textura.
- **Evidência:** grade desalinhada fora da região calibrada (Q4.2); bola projetada dentro do campo em apenas 80% (seg1) e 83% (seg2) dos quadros mesmo após a correção de plausibilidade (Q4.3); velocidades ~2× acima do plausível (Q5.1).
- **Proposta:** (a) solução simples: calibrar novas âncoras ao longo do trecho (por exemplo, sempre que o meio-campo aparecer) e usar a âncora mais próxima no tempo; (b) solução robusta: um modelo de detecção de pontos-chave do campo (quinas das áreas, círculo central, cruzamentos de linhas) que calcule a homografia em cada quadro, sem encadear estimativas e, portanto, sem deriva. Também incluir a correção da distorção da lente, que pesa nos marcos próximos à câmera.
- **Impacto esperado:** posições em metros confiáveis no campo inteiro, o que corrige distância, velocidade, raio de posse e as features do eXP.

### 5.3 Reidentificação de jogadores e goleiros com time próprio

- **Limitação:** o ByteTrack fragmenta os rastros em oclusões, luz forte e movimentos rápidos de câmera, e o K-Means com k=3 coloca os goleiros no grupo "outros", junto com a arbitragem.
- **Evidência:** 1.313 IDs para no máximo 27 pessoas no seg1 (Q3.1), com 284 IDs de jogadores durando apenas 1–5 s; o maior PAx (+1,15) pertence a um fragmento de rastro, não a um atleta (Q6.5); recuos para o goleiro são contados como passe errado (Q3.3).
- **Proposta:** reidentificação por aparência (re-ID), comparando características visuais dos rastros para unir fragmentos do mesmo jogador; ajuste do ByteTrack (maior memória de rastro, uso das detecções de baixa confiança na segunda associação); leitura do número da camisa para identificar atletas; atribuir cada goleiro ao seu time pela posição (o goleiro fica no campo de defesa do próprio time) ou com um detector que tenha a classe *goalkeeper*.
- **Impacto esperado:** elimina os "passes para si mesmo", torna distância e PAx por jogador significativos e corrige os passes ao goleiro.

### 5.4 Mais dados e rótulos manuais para o eXP

- **Limitação:** apenas 64 passes, rotulados pela própria detecção automática. As métricas do eXP são instáveis e há circularidade: o rótulo "errado" e a feature `espaco_destino` vêm das mesmas posições rastreadas.
- **Evidência:** a AUC do logístico tem incerteza de cerca de ±0,11; com só 16 passes a ordem dos modelos era a inversa da obtida com 64 (Q6.2); a taxa de acerto de 56% está muito abaixo dos ~83% do futebol profissional, sinal de rótulos contaminados por passes falsos.
- **Proposta:** processar mais trechos (ou jogos inteiros) e juntar os passes de outros grupos com `--extra`; usar a anotação manual como rótulo de sucesso, registrando também a posição de origem e de destino do passe, para treinar o eXP com rótulos que não dependem do rastreamento; com volume suficiente, testar a `soccermap_mini.py` e comparar com a regressão logística.
- **Impacto esperado:** métricas do eXP com incerteza menor e sem circularidade, permitindo uma comparação honesta com o SoccerMap de Gomes et al.

### 5.5 Outras limitações

- **Bola no ar:** a homografia só vale para o plano do gramado; lançamentos são projetados longe da posição real. Proposta: usar apenas os pontos em que a bola toca o chão e interpolar, ou modelar a trajetória como parábola em 3D.
- **Campo parcialmente visível:** a câmera de TV mostra só parte do campo, então jogadores fora do quadro não entram nas métricas. Proposta: normalizar a distância pelo tempo em que cada jogador aparece e, idealmente, usar câmera tática (plano geral fixo).
- **Trecho curto:** 3 min 20 s de um jogo de 90 min não representam o padrão da partida; posse e PAx servem para demonstrar o método, não para avaliar times ou atletas.

---

## 6. Referências

- Ahmad Yousef, K. M. et al. (2025). *Real-Time Football Match Analysis: Leveraging YOLO for Enhanced Object Detection and Possession Tracking*. Procedia Computer Science 272, 38–45.
- Gomes, R. et al. (2026). *Modelagem de Passes no Futebol via Componentes do Expected Possession Value com Redes Totalmente Convolucionais*. REIC 24:1.
- Código de apoio: https://github.com/eron93br/vc-20262-p3
- Ultralytics YOLOv8 e ByteTrack.

## 7. Uso de IA

Ver [`DECLARACAO_IA.md`](DECLARACAO_IA.md).
