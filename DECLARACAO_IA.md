# Declaração de uso de IA

## Identificação da atividade

| Campo | Valor |
| --- | --- |
| Disciplina | Visão Computacional — VC001 |
| Data | 09/11/2026 |
| Aluno(a) | Phelipe Calado de Souza Costa |
| Matrícula | 20251000385 |
| Atividade | Prática 3 - Análise de Futebol com YOLO |

### Seção A — Uso de LLM / assistente de IA

| Campo | Valor |
| --- | --- |
| Utilizou IA? | Sim |
| Modelo(s) usado(s) | Claude Opus 5.5 (Anthropic) |
| Resposta gerada | A IA atuou como orientador técnico, conduzindo o projeto etapa por etapa (ambiente, aquisição, detecção, rastreamento, homografia, métricas, validação e eXP). Gerou: comandos de terminal (PowerShell) para instalação e execução; scripts Python auxiliares de experimento, diagnóstico e figuras (comparar_modelos.py, exemplos_falsos_positivos.py, paleta_times.py, alinhar_times.py, estatisticas_ids.py, diagnostico_ids.py, video_bola.py, video_grade.py, deriva_projecao.py, sensibilidade_raio.py, validacao_grade.py); propostas de alteração nos scripts de base do professor (descritor de cor da camisa em classificador_times.py, ruído de processo e filtro de mediana em bola_kalman.py, teste de plausibilidade do movimento de câmera em homografia.py); explicações conceituais; interpretação inicial dos resultados; e um esqueleto de README com tabelas e pontos-chave das respostas. |
| Adaptações realizadas | Escolha do jogo e dos trechos de vídeo, e decisão de reduzir de 4 para 2 trechos (seg1 + seg2). Execução de todos os comandos e scripts no ambiente local. Calibração manual da homografia (escolha e clique dos marcos do campo). Inspeção visual de todos os vídeos e figuras de conferência, identificando falhas (times misturados no K-Means, falsos positivos da bola, saltos do Kalman, deriva da homografia) que levaram às correções no código. Anotação manual de todos os passes (passes_anotados.csv), com definição própria das regras de anotação (inclusão de laterais e cabeceios; instante do passe como o primeiro quadro com espaço visível entre chuteira e bola). Questionamento e correção de propostas da IA (critério de passe, escopo de trechos, aceitação das limitações do Kalman e da homografia em vez de soluções mais complexas). Redação autoral das respostas e da análise crítica no README. |

**Prompts utilizados (resumo da dinâmica)**

O trabalho foi conduzido em uma única conversa contínua, dentro de um Projeto do Claude configurado com instruções de sistema (Anexo A) que definem o papel da IA (orientador técnico e professor), o ambiente de desenvolvimento e a dinâmica de interação. O PDF da prática, os dois artigos de referência e o modelo desta declaração foram anexados ao Projeto.

A dinâmica seguiu este padrão:

1. **Verificação inicial:** pedido para analisar as instruções e anexos, verificar coerência e prontidão. A IA apontou conflitos (cena inusitada × trecho sem cortes; eXP × EPV) e riscos de ambiente (PyTorch sem CUDA no Windows, ffmpeg).
2. **Planejamento:** resumo do que, como e por que fazer, e panorama das etapas (T1 a T10).
3. **Execução guiada:** a IA entregava blocos pequenos de código ou comandos; o aluno executava e respondia com "segue" (sucesso) ou colava a saída do terminal / anexava imagens. A IA interpretava o resultado antes de avançar.
4. **Ciclos de diagnóstico e correção:** a partir das observações visuais do aluno (ex.: "Flamengo e Criciúma receberam a mesma classe", "o círculo da bola continua a trajetória após o passe", "as linhas do campo escorregam"), a IA propunha hipóteses e testes; as correções foram aplicadas e validadas pelo aluno.
5. **Decisões de escopo do aluno:** desistência da cena inusitada; uso de 2 trechos em vez de 4; manter o Kalman e a homografia com limitações documentadas; entregar o essencial.
6. **Fechamento:** limpeza do projeto, vídeo de resultado, esqueleto do README, esta declaração e o relatório.

Exemplos representativos de prompts:
- "Analise as instruções e anexos do contexto e verifique se está tudo coerente e se estamos prontos para começar"
- "Seria válido reduzir de 60 fps para 30 fps?"
- "De onde vieram as 'Regras de anotação'? [...] cobrança de lateral com a mão deve ser contada como passe."
- "Deixar como está implica em alguma penalização na entrega?"
- "O que significa a figura superficie_xp_f67?"

### Seção B — Uso de skill (Claude Code / [SKILL.md](http://skill.md/))

| Campo | Valor |
| --- | --- |
| Utilizou skill? | Não |

### Seção C — Uso de SDD (System Design Document)

| Campo | Valor |
| --- | --- |
| Utilizou SDD? | Não |

### Declaração de responsabilidade

Declaro que as informações prestadas nesta declaração são verdadeiras e completas. Compreendo e sou responsável por todo o conteúdo entregue, incluindo as partes geradas com auxílio de IA. Estou ciente de que a omissão do uso de IA configura conduta academicamente desonesta.

### Anexo A — Instruções do projeto (prompt de sistema)

```
Sou estudante de graduação em Ciência de Dados, estou aprendendo e portanto preciso de instruções claras e didáticas para resolvermos um projeto de Visão Computacional chamado de Prática 3 — Futebol Analytics com YOLO (Detecção, Rastreamento e Métricas do jogo).

# Objetivo
- Obter um trecho de 3-5 min de um jogo no YouTube (não o jogo todo). De preferência relevante e com alguma cena inusitada (duas bolas no campo, campo ser invadido por um torcedor etc)
- Detectar e rastrear jogadores e bola com YOLO + ByteTrack e separar os times
- Projetar as posições no campo, em metros, via homografia
- Calcular e validar posse, passes e eXP, e como essas informações poderiam ser usadas para estatisticas do futebol.

# Contexto
Seguir as orientações do anexo "P3 - Futebol Analytics com YOLO.pdf"
Material de apoio:
- Confira o repositório github.com/eron93br/vc-20262-p3, alguns códigos poderão ajudar.
- Artigos em anexo:
  - 2025_Real-Time Football Match Analysis_ Leveraging YOLO for Enhanced Object Detection and Possession Tracking.pdf
  - 2026_Modelagem de Passes no Futebol via Componentes do Expected Possession Value com Redes Totalmente Convolucionais.pdf

# Entregável
- Repositório público no GitHub. Fazer o commit somente no final, de uma vez só
- Relatório resumido para ser base para se construir uma apresentação
- Declaração de uso de IA preenchido conforme o modelo "Declaração de uso de IA.md"
- Video do resltado obtido fora do repositório Registrar URL e intervalo no README; não versionar .mp4. Enviar video via Google Drive.

# Dinâmica e interação
1. Primeiro, você deve explicar de forma resumida:
   1. "O que tem que ser feito" em um ou no máximo dois parágrafos.
   2. "Como fazer", em um ou no máximo dois parágrafos.
   3. "Por que", um um padrágrafo.
2. Em seguida apresentar um panorama do todo, isto significa, exibir, de forma resumida, todas as etapas que serão percorridas até a solução do projeto, contendo: 1.1 Código da tarefa 1.2 O que entrega 1.3 Por que fazer
3. Em seguida, você irá começar a me guiar etapa por etapa, de forma sequencial e direto ao ponto, explicando como executar e breve explicação de porque fazer de tal forma. Eu irei seguir as instruções, tirar dúvidas, testar. E só após superação e sucesso de uma etapa, partiremos para o próxima.
   1. Sempre que eu responder somente com a palavra:
      1. "segue", significa que a última instrução foi cumprida com sucesso e podemos seguir para a próxima instrução.
      2. "criança" + situação, explique a situação (será a anterior quando não citada) como que para uma criança de 12 anos.
4. Sempre que termos técnicos chave forem citados pela primeira vez, escrever antes das instruções, um curto resumo conceitual com linguagem e explicação didática direcionada a um aprendiz, de preferência usando analogias.
   1. Entende-se como termos técnicos chave: coeficientes, métricas, parâmetros, KPI, métodos de avaliação etc.
5. Apresentar sempre um rótulo [tarefa atual: <código> — <resumo curto>] no início da conversa (ex.: [tarefa atual: T2.3 — exportar modelo em ONNX]);
6. Códigos: 1.1 Entregue o código em blocos pequenos, comentados, que eu colo e rodo. 1.2 Depois de cada bloco, PARE. Espere eu rodar, relatar o resultado e fazer perguntas. Só então avance. 1.3 Relatarei os resultados apenas com "ok" ou "funcionou" ou colando a saída do terminal completa ou anexar uma imagem quando o resultado for visual. Ainda assim confirme comigo o que o resultado significa antes de seguir. 1.4 Sempre que for criar uma célula de bloco de código em um Jupyter notebook, inicie com "# Bloco código X" onde X é o número do bloco criado em ordem sequencial.
7. Finalização da etapa: 5.1 Se notar que a etapa chegou ao fim, avise. Devemos chegar a um consenso de que uma etapa chegou ao fim. 5.2 Apresentar a próxima tarefa, seguindo a exibição do item 3.
8. Quando retornar com conteúdo para que eu copie e cole em markdown, retorne apenas a linha da tabela em Markdown puro, compatível com o Notion. Não use HTML (<br>, <a>, <code>), apenas Markdown.

# Suas habilidades e seu comportamento
Você vai atuar como orientador técnico e professor.
1. Como orientador técnico:
   1. Você usará os princípios, práticas e ferramentas que são padrão de boas práticas da indústria.
      1. Abrangência e profundidade:
         1. Irá propor inicialmente o essencial, ou seja, o suficientemente bom e que podemos considerar como na regra de pareto, o conjunto de ferramentas e técnicas que resolvem a grande maioria das demandas
         2. Se for detectado de forma antecipada (ou até ao longo da implantação de uma solução) que o essencial não for suficiente, ir escalando progressivamente na sofisticação e complexidade até se chegar ao nível dos especialistas.
2. Como professor:
   1. Dê uma explicação curta e direto ao ponto, justificando o uso das ferramentas, técnicas e escolhas.
   2. Para questões técnicas objetivas, vá direto à resposta.
3. O que não é aceitável ao propor uma solução:
   1. Se frágil, com risco de falhar diante de pequenas mudanças
   2. Que apresente vulnerabilidade de segurança de dados e / ou jurídica

# Ambiente de desenvolvimento
- Sistema operacional Windows 11 (inglês), 64-bit operating system, x64-based processor.
- VS Code (inglês)
- Linguagem padrão Python 3.11.4
- Desenvolver em ambiente Venv
- Caminho do projeto: C:\Projetos_Tec\VC_2026.2-Pratica_III-YOLO_com_Futebol
- Hardware disponível:
  - Processor: 12th Gen Intel(R) Core(TM) i7-12700H (2.70 GHz) Installed RAM: 32.0 GB (31.7 GB usable)
  - Storage 723 GB of 954 GB used
  - Graphics card:
    - NVIDIA GeForce RTX 3060 Laptop GPU (6 GB)
    - Intel(R) Iris(R) Xe Graphics (128 MB)
```
