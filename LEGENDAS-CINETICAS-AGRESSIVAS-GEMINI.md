# Legendas cinéticas agressivas — Motor CINE-PSICO (Câmara, Retenção & Dual-Format)

Playbook de produção avançado para **Reels (9:16)** e **Tours Cinematográficos (16:9)**. 

Este documento introduz o **Motor CINE-PSICO**: um princípio de organização focado na **Integração Física com a Câmara (Cine-Kinetics)**, **Psicologia de Retenção Visual (Micro-Interrupções)** e no **Sistema Adaptativo Dual-Format (9:16 vs 16:9)**.

Complementa e cruza diretamente a biblioteca de conhecimento do OpenMontage:
- [`LEGENDAS-CINETICAS-AGRESSIVAS.md`](LEGENDAS-CINETICAS-AGRESSIVAS.md) — Biblioteca-base de receitas R1–R8, timings e pipeline clássico AE/Resolve;
- [`LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md`](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md) — Modos de energia (Brand-safe / Social / Max), grelha BPM, papéis de cor e receitas SOL-01–10;
- [`LEGENDAS-CINETICAS-AGRESSIVAS-KIMI.md`](LEGENDAS-CINETICAS-AGRESSIVAS-KIMI.md) — Gramática semântica (função→assinatura), rig procedural AE com markers e receitas K01–K12;
- [`TIPOGRAFIA-REAL-ESTATE.md`](TIPOGRAFIA-REAL-ESTATE.md) — Hierarquia por gama, legibilidade e densidade;
- [`MASTERING.md`](MASTERING.md) — Speed ramps, optical flow, áudio e mastering;
- [`ESTILO-CLIENTE.md`](projects/video-service-business/clients/Mario%20Garces/ESTILO-CLIENTE.md) — Locks do Mário Garcês (Montserrat, caixa tinta, barra 4px, localização locked).

> **🔒 Respeito Absoluto pelos Client Locks:**
> No cliente Mário Garcês: manter sempre a **Montserrat** (variável com peso Medium no título e Bold CAPS no sobretítulo), caixa medida pela tinta `rgba(16,22,21,0.74)`, barra lateral 4px vermelho/azul, x=67 e localização integral locked `T4 Lumiar – QUINTA dos ALCOUTINS`. A "agressão cinética" deste manual altera a física do movimento, as acelerações e as micro-interrupções — nunca violando a identidade aprovada do cliente.

---

## 1. Princípio Fundador: Cine-Kinetics (A física da legenda colada à câmara)

O maior erro em kinetic typography imobiliária é tratar a legenda como uma camada gráfica 2D "colada no ecrã" enquanto o vídeo ao fundo se move em 3D. Quando a câmara faz um *drone fly-through*, um *pan* rápido ou um *speed ramp*, uma legenda com um simples *pop* 2D parece flutuar sem peso, desligada da realidade da casa.

**Cine-Kinetics** é a integração matemática do vetor da câmara com o vetor de entrada da legenda.

```text
[Vetor de Câmara (Pan Direita)]  ---> +150 px/s
[Vetor de Texto (Inércia Inversa)] <--- -350 px/s  ===> Colisão Visual Impactante
```

### 1.1 Tabela de Correlação Vetorial (Shot-Type ↔ Motion-Type)

| Tipo de Plano / Movimento | Vetor da Câmara | Vetor de Entrada da Legenda | Efeito Cinético Resultante |
|:---|:---|:---|:---|
| **FPV Drone / Forward Push** | Avanço rápido em Z (+Z) | Escala inversa a partir do ponto de fuga (Z-compression + 3° Roll) | A legenda parece atravessada pelo drone no movimento |
| **Speed Ramp (Aceleração)** | Deslocamento acelerado (Optical Flow) | Skew / Distortion X (12–18°) + Snap no travão | O texto sofre deformação elástica por força G |
| **Pan Horizontal (Sala / Varanda)** | Deslocamento em X (Esq → Dir) | Contra-vetor com aceleração inicial (Dir → Esq) | Inércia de massa física que colide com o olhar |
| **Tilt Vertical (Pé-Direito / Mezzanine)** | Ascensão em Y (Baixo → Cima) | Descida de alta velocidade com corte tipo guilhotina | Efeito elevador com paragem no ponto tónico |
| **Orbit 3D (Ilha de Cozinha / Piscina)** | Rotação orbital constante | Curva em arco simétrica (Paralaxe de curvatura) | A legenda gravita em redor do elemento central |

---

## 2. Psicologia de Retenção Visual & Micro-Interacções (<3 Frames)

Para capturar a atenção nos primeiros 3 segundos de um Reel e manter a retenção acima dos 70% sem estragar a estética do imóvel, aplicam-se estímulos cognitivos rápidos sub-conscientes.

### 2.1 Latência Cognitiva & Curiosity Gap

Dividir a frase em dois tempos assíncronos provoca a leitura compulsiva:

```text
[Tempo 1: f00–f08]   "O MAIOR TERRAÇO..."      (Gera a questão: de quanto?)
[Gap de espera: f09–f15] (Retenção pura — 7 frames de pausa visual)
[Tempo 2: f16–f24]   "...DE LISBOA (188 m²)"   (Entrega o dado com impacto G08/K09)
```

O cérebro recusa-se a passar o vídeo enquanto a segunda metade da afirmação não é entregue.

### 2.2 Gatilhos de Micro-Interrupção (1 a 3 Frames)

Pequenos "estresses" visuais colocados rigorosamente nos picos de áudio:

1. **Flash Invert (1 frame):** No frame exato do `#HIT`, inverte-se a cor da caixa (ex: de `rgba(16,22,21,0.74)` para `rgba(255,255,255,0.9)` durante 1 frame). Aumenta o impacto sem necessitar de aumentar o tamanho da fonte.
2. **Micro-Glitch Displacement (2 frames):** No frame 2 do movimento, desloca-se a layer de texto +12px Y e aplica-se um rasto vermelho/azul (RGB offset). Restabelece a posição normal no frame 4.
3. **Syllable Strobe (1 frame):** Na sílaba tónica da voz (ex: "LUM-**i**-ar"), a cor dessa palavra passa de BASE (`#FFFFFF`) para HERO/ACÇÃO durante exatamente 1 frame antes de estabilizar.

### 2.3 Modulação de Densidade de Informação

Não esfaqueies o espectador com estímulos constantes. O ritmo perfeito alterna entre alta densidade e respiração:

```text
0,0s - 1,8s:  [HOOK ALTA ENERGIA]   -> 3 palavras, 2 flashes, movimento G01
1,8s - 3,5s:  [RESPIRO VISUAL]      -> Vídeo límpido da sala, legenda em fade limpo
3,5s - 5,0s:  [DADO TÉCNICO DENSO]  -> 3 tiles de dados (área, quartos, garagem)
5,0s - 7,0s:  [RESPIRO VISUAL]      -> Plano de pormenor da cozinha
```

---

## 3. Sistema Dual-Format Adaptativo (9:16 Reels ↔ 16:9 Tour Master)

Trabalhar em agência exige produzir a versão **Vertical (9:16)** para Instagram/TikTok e a versão **Horizontal (16:9)** para YouTube/Site da Imobiliária sem duplicar o trabalho de animação.

### 3.1 Regras de Transformação Espacial

```text
               [ 9:16 VERTICAL ]                         [ 16:9 HORIZONTAL ]
        +-----------------------------+       +-------------------------------------+
        |          SAFE TOP           |       |              SAFE TOP               |
        |                             |       |  +-------+                       |
        |      HERO TEXT (CENTRO)     |       |  | LOGO  |    HERO TITLE 16:9     |
        |                             |       |  +-------+    (TERÇO SUPERIOR)      |
        |                             |       |                                     |
        |   LOWER THIRD (ABACADADO)   |       |  LOWER-THIRD (X=96, Y=820)          |
        |         SAFE BOTTOM         |       |  [Caixa com Tinta + Barra 4px]      |
        +-----------------------------+       +-------------------------------------+
```

### 3.2 Matriz de Conversão Dual-Format

| Parâmetro | Formato 9:16 (Vertical) | Formato 16:9 (Horizontal) |
|:---|:---|:---|
| **Eixo Dominante de Animação** | **Y-Axis (Vertical)** + Scale | **X-Axis (Horizontal)** + Slide |
| **Tamanho Título Principal** | 42pt – 56pt Bold/ExtraBold | 30pt – 38pt Medium/Bold |
| **Largura Máxima de Caixa** | 946 px (Margem 67px cada lado) | 720 px (Margem 96px à esquerda) |
| **Anchor Point Padrão** | Centro-Baixo (`x=540, y=1480`) | Esquerda-Baixo (`x=96, y=880`) |
| **Safe Margin Inferior** | ≥ 380 px (Livre de UI do IG/TikTok) | ≥ 96 px (Livre de leitor YouTube) |
| **Duração do Overshoot** | 3–4 frames (Agressivo) | 5–7 frames (Mais suave e amplo) |

---

## 4. Novas Receitas Frame-a-Frame G01–G12 (@24 fps)

Todas as receitas são calculadas para timelines a **24 fps real** sobre canvas de **1080×1920** (ajustar X/Y proporcionalmente para 1920×1080).

### G01 · FPV Drone Depth-Slam

Destinado a aberturas de terrenos, fachadas e planos de aproximação rápida em drone. O texto nasce no ponto de fuga central e expande com rotação em Z.

```text
f00  Scale 0%     RotateZ -6°   Opacity 0%    Blur 20px
f02  Scale 25%    RotateZ -4°   Opacity 100%  Blur 12px
f07  Scale 118%   RotateZ +1.5° Opacity 100%  Blur 0px   <-- #HIT (Flash 1f opcional)
f11  Scale 96%    RotateZ -0.5° Opacity 100%
f15  Scale 100%   RotateZ 0°    Opacity 100%             <-- #SETTLE
hold...
f(out) Scale 100% -> 220% em 6f + Blur 15px (O drone "atravessa" a letra)
```
- **SFX:** Whoosh grave profundo com transição para sub-drop no `f07`.

### G02 · Ramp Whip-Snap

Sincronizado ao milissegundo com o pico de aceleração de um *speed ramp* (Optical Flow) no vídeo.

```text
f00  Position X -600  SkewX +18°  Opacity 0%
f03  Position X -150  SkewX +14°  Opacity 100%  (Acompanha a velocidade do ramp)
f06  Position X +45   SkewX -6°   Opacity 100%  <-- #HIT (O vídeo trava; a legenda trava com travão)
f09  Position X -10   SkewX +2°   Opacity 100%
f12  Position X 0     SkewX 0°    Opacity 100%  <-- #LOCK
```
- **SFX:** Mechanical snap / whip seco de alta frequência.

### G03 · Kitchen Island Orbit

O texto descreve uma trajetória em arco curvo 3D, espelhando a rotação da câmara à volta de uma ilha de cozinha ou piscina.

```text
f00  Position [X-250, Y+40]  RotateY +25°  Scale 82%   Opacity 0%
f08  Position [X+30,  Y-8]   RotateY -5°   Scale 108%  Opacity 100%
f12  Position [X-5,   Y+2]   RotateY +1°   Scale 98%   Opacity 100%
f16  Position [X 0,   Y 0]   RotateY 0°    Scale 100%  Opacity 100%
```
- **SFX:** Smooth air sweep + tique metálico discreto ao travar no `f16`.

### G04 · Counter-Vector Pan

Utilizado em panorâmicas horizontais de salas amplas ou varandas. O texto move-se no sentido oposto ao da câmara para gerar colisão de massas.

```text
Câmara a mover para a DIREITA (180 px/s):
f00  Position X +450  ScaleX 120%  Opacity 0%
f06  Position X -35   ScaleX 92%   Opacity 100%  <-- #HIT
f10  Position X +8    ScaleX 103%  Opacity 100%
f14  Position X 0     ScaleX 100%  Opacity 100%
```
- Durante o *HOLD*: O texto mantém um *drift* contínuo de -1.5px por frame para continuar a lutar contra o movimento do vídeo.

### G05 · Vertical Tilt Elevator

Animação para valorizar pé-direito duplo, mezzanines ou fachadas verticais. A legenda faz um reveal de baixo para cima acompanhado por máscara de corte.

```text
f00  Position Y +160  Mask Height 0%    Opacity 0%
f05  Position Y -20   Mask Height 110%  Opacity 100%
f09  Position Y +6    Mask Height 100%  Opacity 100%
f12  Position Y 0     Mask Height 100%  Opacity 100%
```
- **Máscara:** A caixa de fundo expande a partir da baseline.

### G06 · Strobe Syllable Punch

Entrada limpa por caracteres, onde cada sílaba tónica aciona um disparo estroboscópico de cor.

```text
f00–f06: Animação de entrada por caracteres (Stagger 1.5f, Position Y +30 -> 0)
Sílaba 1 (ex: "AR"):  f04 -> Cor HERO (#FF2D55) durante 1 frame -> passa a BASE (#FFFFFF)
Sílaba 2 (ex: "QUI"): f08 -> Cor HERO (#FF2D55) durante 1 frame -> passa a BASE (#FFFFFF)
Sílaba 3 (ex: "TE"):  f12 -> Cor HERO (#FF2D55) durante 1 frame -> passa a BASE (#FFFFFF)
Sílaba 4 (ex: "TU"):  f16 -> Cor DADO (#FFD60A) FIXA no hold
```

### G07 · Architectural Cutout Stencil

A palavra nasce como um recorte transparente no meio de um bloco escuro (Alpha Inversion), deixando ver o vídeo da casa por dentro das próprias letras.

```text
f00  Block ScaleX 0%    Text Opacity 0%
f05  Block ScaleX 100%  Text Opacity 100%  (Texto em modo Alpha Silhouette)
f06–f24: O vídeo passa por dentro da tipografia gigante (200pt)
f25  Text Fills com cor sólida (BASE) e o bloco colapsa para a caixa de legenda normal
```

### G08 · Dual-Tile Collision

Dois blocos de dados entram de lados opostos do ecrã e colidem no centro com micro-bounce instantâneo.

```text
Tile 1 ("188 m²"):   Entra da Esquerda  (X -500 -> +20 -> 0 em 8 frames)
Tile 2 ("€685 000"): Entra da Direita   (X +500 -> -20 -> 0 em 8 frames)
Impacto no f08: Ambas as caixas fazem ScaleY 100% -> 115% -> 100% em 3 frames + Click SFX seco duplo.
```

### G09 · Kinetic Price Unroll

O valor financeiro é apresentado através de uma rotação vertical de rolo mecânico (estilo fita métrica ou placar de estádio).

```text
f00  Dígitos RotateX -90°  Opacity 0%    BlurY 15px
f06  Dígitos RotateX +20°  Opacity 100%  BlurY 4px
f10  Dígitos RotateX -8°   Opacity 100%  BlurY 0px
f13  Dígitos RotateX 0°    Opacity 100%  BlurY 0px   <-- Lock do Valor
```
- **Formatação:** Sempre com espaço nos milhares à norma portuguesa (`685 000 €`).

### G10 · Micro-Glitch Hook

Animação ultra-agressiva para os primeiros 6 frames de um Reel.

```text
f00  Text Position Y +40  RGB Offset [R:+12, B:-12]  Scale 130%
f01  Text Position Y -20  RGB Offset [R:-8,  B:+8]   Scale 110%  Inversion 1f
f02  Text Position Y +8   RGB Offset [R:+4,  B:-4]   Scale 120%
f03  Text Position Y 0    RGB Offset [0, 0]          Scale 100%  <-- Settle total em 3 frames!
```

### G11 · Glass-Morph Floating Badge

Para propriedades de arquitetura moderna/luxo. A caixa simula vidro fosco acrílico e mantém um movimento perpétuo senoidal suave durante o *HOLD*.

```text
Caixa: Fill rgba(255, 255, 255, 0.15) + Backdrop Blur 24px + Stroke 1px rgba(255, 255, 255, 0.4).
Entrada: Fade + Scale 95% -> 100% em 10 frames.
Durante o HOLD (f11 em diante):
Position Y = Y_Base + Math.sin(time * 2.5) * 6.0; (Flutuação contínua de 6px)
```

### G12 · Outro Curtain Sweep

Varretura de fecho da legenda que se transforma na transição para o cartão final do agente.

```text
f00  Legenda normal
f04  Caixa expande ScaleX 100% -> 400% e ScaleY 100% -> 800%
f08  A caixa cobre o ecrã inteiro em cor sólida (ex: Navy #1C355E)
f09  Revela o Cartão Final com o logo e contacto sobre a cor sólida
```

---

## 5. Setups Técnicos Avançados (AE Graph Editor & Resolve Fusion Hybrid)

### 5.1 Parâmetros Exatos do After Effects Graph Editor

Para obter a assinatura cinética "agressiva mas limpa", ajusta os cabos de influência no **Speed Graph** do AE para os seguintes valores numéricos:

```text
[Ataque Íngreme (Slam)]
Keyframe 1 (f00): Outgoing Velocity Influence = 85% a 92%
Keyframe 2 (#HIT): Incoming Velocity Influence = 15% a 22%

[Settle Macio]
Keyframe 2 (#HIT): Outgoing Velocity Influence = 65%
Keyframe 3 (#LOCK): Incoming Velocity Influence = 80%
```

```javascript
// Expressão AE: Inércia de Câmara Automática (Aplicar em Position)
// Lê a velocidade de uma layer de câmara/vídeo e reage em contra-fase
const camLayer = thisComp.layer("VIDEO_BACKGROUND");
const camVel = camLayer.transform.position.velocityAtTime(time);
const inertiaFactor = -0.08; // Intensidade da reação
value + (camVel * inertiaFactor);
```

### 5.2 Fusion Node Tree (Resolve) sem Expressões Complexas

Para editores que trabalham exclusivamente no DaVinci Resolve sem querer digitar código JS/LUA:

```text
[MediaIn1] ---> [ColorCorrector] ------------> [Merge1] ---> [MediaOut1]
                                                 ^
[TextPlus1] -> [Transform_Inertia] -> [Blur1] ---+
```

1. **TextPlus1:** Configurar fonte (Montserrat), tamanho e cor.
2. **Transform_Inertia (Transform Node):**
   - Rola para a aba *Modifiers*, clica com o botão direito em *Center* -> **Anim Curves**.
   - **Source:** Video Out; **Curve:** Elastic ou Custom Transition.
   - **Scale:** -0.15 (gera o contra-vetor de entrada automático).
3. **Blur1 (Directional Blur):**
   - Conecta o parâmetro *Length* à velocidade do *Transform_Inertia* via Expression simples: `Transform_Inertia.XSize * 0.02`.

---

## 6. Matriz de Áudio Háptico e Frequências SFX

A sensação de "agressão" de uma legenda é 50% auditiva. O ouvido humano processa frequências diferentes a velocidades diferentes.

### 6.1 Tabela de Camadas de Frequência e Alinhamento de Timeline

| Camada de Frequência | Frequência Base | Função Emocional | Alinhamento de Frame na Timeline |
|:---|:---|:---|:---|
| **Sub-Bass Drop** | 40 Hz – 60 Hz | Soco no peito / Gravidade / Grande Revelação | **-1 frame** em relação ao `#HIT` (Sente-se antes de ver) |
| **Mid Impact (Corpo)** | 150 Hz – 400 Hz | Peso de madeira, pedra ou metal da casa | **Exactamente no frame `#HIT`** |
| **Transient Click** | 2 000 Hz – 4 500 Hz | Precisão mecânica, números a travar, caixa a fechar | **+1 frame** após o `#HIT` (Confirmação de lock) |
| **Air Whoosh** | 600 Hz – 1 800 Hz | Velocidade do ar, movimento da câmara | **-3 a -2 frames** antes do `#HIT` (Antecipação) |

```text
Timeline Audio Alignment (@24fps):
Frame:      f04       f05       f06       f07       f08
Visual:   [Move]    [Move]    [Move]    [#HIT]    [Hold]
Whoosh:   [========WE-EE-EE-EE========]
Sub-Bass:                     [D-R-O-P]
Mid Impact:                             [PUNCH]
Click:                                            [CLICK]
```

---

## 7. Mapeamento de Sequências Prontas para Hooks Imobiliários

### Hook G-01 · FPV Luxury Entry (6s / 144 frames)
**Objetivo:** Agarrar a atenção num plano FPV a entrar pela porta da frente ou sobre a piscina.

```text
f00–f12  G01 Depth-Slam: "NÃO É UMA MAQUETE" (Cores: BASE + HERO vermelho)
f13–f28  Respiro de vídeo (O drone avança pela sala)
f29–f45  G04 Counter-Vector Pan: "SÃO 450 m² DE ÁREA" (Caixa tinta + barra 4px)
f46–f72  Respiro de vídeo
f73–f96  G08 Dual-Tile Collision: Tile 1 ["T4 DUPLEX"] + Tile 2 ["CASCAIS"]
f97–f144 G11 Glass-Morph Badge: "685 000 €" a flutuar no canto enquanto o plano estabiliza
```

### Hook G-02 · Speed Ramp Tour Highlights (4s / 96 frames)
**Objetivo:** Retenção máxima num vídeo de montagem rápida.

```text
f00–f10  G10 Micro-Glitch Hook: "T4 LUMIAR" (Localização completa no rodapé)
f11–f24  G02 Ramp Whip-Snap: "PÉ-DIREITO 3.3m" (Trava exatamente no fim do ramp 1)
f25–f48  G05 Elevator Wipe: "COZINHA EQUIPADA" (Acompanha o tilt vertical da câmara)
f49–f72  G09 Price Unroll: "685 000 €" (Rolamento mecânico com ratchet SFX)
f73–f96  G12 Outro Curtain Sweep -> Transição para o Cartão Mário Garcês
```

### Hook G-03 · Quick-Fire Property Stats (5s / 120 frames)
**Objetivo:** Apresentar 3 grandes argumentos de venda em menos de 5 segundos.

```text
f00–f24  G08 Dual-Tile: ["188 m² ÚTEIS"] + ["VISTA RIO"] (Entrada em colisão)
f25–f48  G06 Syllable Punch: ["ESTACIONALMENTE PERFEITO"] (Strobe de cor nas tónicas)
f49–f72  G07 Stencil Cutout: ["GARAGEM 3 CARROS"] (Recorte transparente na imagem)
f73–f120 G11 Floating Badge com CTA: ["MARQUE VISITA"] + Telefone
```

---

## 8. Anti-Padrões Específicos do Motor CINE-PSICO

1. **Ignorar o vetor da câmara:** Animar uma legenda para a esquerda enquanto a câmara faz um pan violento para a esquerda (provoca enjoo visual e perda de legibilidade).
2. **Flash Invert prolongado:** Deixar o flash de inversão de cor durar mais do que 1 ou 2 frames (parece um erro de piscar de monitor).
3. **Desfasamento de frequências no áudio:** Colocar o Sub-bass *depois* do click mecânico, invertendo a física natural do som.
4. **Duplicação de animação em 9:16 e 16:9:** Tentar usar a mesma posição Y do Reels no corte 16:9 de YouTube (corta a imagem e tapa o centro de interesse do plano).
5. **Aceleração linear sem easing no Whip-Snap:** Movimentos de transição sem curva íngreme no Graph Editor parecem animações de Powerpoint dos anos 90.
6. **Violência cinética sobre elementos locked do cliente:** Tentar aplicar *Micro-Glitch* ou *Rubber Band* na barra oficial de 4px ou na localização locked `T4 Lumiar – QUINTA dos ALCOUTINS` do Mário Garcês. Os elementos de marca e localização mantêm-se **sempre limpos e estáveis** (fade/wipe simples).

---

## 9. Quando usar este doc vs os outros três

O repositório do OpenMontage conta agora com **quatro playbooks especializados** em tipografia e legendas cinéticas. Utiliza esta matriz para escolher o documento certo conforme a necessidade do projeto:

```text
+-----------------------------------------------------------------------------------+
|                            MATRIZ DE DECISÃO DE PLAYBOOKS                         |
+-----------------------------------+-----------------------------------------------+
| Se a tua necessidade principal é: | Utiliza este documento:                       |
+-----------------------------------+-----------------------------------------------+
| Consultar receitas de animação    | LEGENDAS-CINETICAS-AGRESSIVAS.md              |
| rápidas R1–R8 e timings padrão    | (O Dicionário de Receitas Rápidas)            |
+-----------------------------------+-----------------------------------------------+
| Definir o nível de energia A/B/C, | LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md          |
| cores por função e grelha BPM     | (O Manual de Modos de Energia e Cores)        |
+-----------------------------------+-----------------------------------------------+
| Montar rigs procedurais em AE com | LEGENDAS-CINETICAS-AGRESSIVAS-KIMI.md         |
| markers, expressões e gramática   | (O Motor de Rigs e Automação de Comps)        |
+-----------------------------------+-----------------------------------------------+
| Sincronizar movimento com a       | LEGENDAS-CINETICAS-AGRESSIVAS-GEMINI.md       |
| câmara (Cine-Kinetics), retenção  | (O Manual de Física de Câmara, Psicologia de  |
| de Reels e conversão 9:16/16:9    | Retenção e Formato Dual) [ESTE DOC]           |
+-----------------------------------+-----------------------------------------------+
```

### Resumo Combinado de Produção Ideal:
1. Começa pelo **SOL** para escolher o Modo de Energia (Brand-Safe vs Social vs Max) e definir a paleta de cores.
2. Utiliza o **KIMI** para estruturar a comp do After Effects com a layer `CTRL` e markers `#IN/#HIT/#LOCK/#OUT`.
3. Aplica as receitas **GEMINI (G01–G12)** para conectar os movimentos do texto à física de câmara do plano imobiliário (FPV, speed ramp, pan, tilt).
4. Recorre à **v2 original (R1–R8)** para preencher transições rápidas e detalhes secundários.
5. Valida os locks do cliente em `ESTILO-CLIENTE.md` e faz o mastering de áudio/export conforme o `MASTERING.md`.

---
*Playbook vivo de produção OpenMontage — Atualizado em Agosto de 2026.*
