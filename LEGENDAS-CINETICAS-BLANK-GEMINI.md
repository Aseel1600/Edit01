# LEGENDAS CINÉTICAS AGRESSIVAS — KA-ENGINE (KINETIC ARCHITECTURE 24FPS)

**Playbook de Produção de Tipografia Cinética Agressiva para Real Estate (Reels 9:16 & Tours 16:9)**

---

## 0. O SISTEMA KINETO-ARQUITECTÓNICO (KA-ENGINE)

Este manual estabelece o **KA-ENGINE (Kinetic Architecture Engine)**, um sistema de tipografia cinética desenhado especificamente para vídeo imobiliário de alto impacto. 

Diferente de abordagens tradicionais que usam animações genéricas de redes sociais ou sobreposições estáticas passivas, o KA-ENGINE trata a legenda como uma **estrutura tectónica viva**: um elemento gráfico com massa, aceleração, propriedades de reflexão e integração direta com a geometria da imagem (perspectiva, linhas de fuga, cortes de luz e transições de espaço).

---

## 1. DUAL-FORMAT & MATRIZ DE SAFE ZONES RÍGIDAS

O comportamento tipográfico varia radicalmente entre a rotação vertical rápida (9:16) e a contemplação cinematográfica horizontal (16:9). 

```text
================================================================================
                    MATRIZ VISUAL DE SAFE ZONES (24 FPS)
================================================================================

9:16 REELS / SHORTS / TIKTOK                      16:9 CINEMATIC TOURS
+-----------------------------------+             +-----------------------------------+
| [UI Top Overlay / Profile / Badges]|             |       BROADCAST TOP SAFE (8%)     |
| - - - - - - - - - - - - - - - - - |             | +-------------------------------+ |
|                                   |             | |                               | |
|         HERO TEXT ZONE            |             | |      TOP OVERLAY / HEADER     | |
|     (Ataque Visual Superior)      |             | |                               | |
|                                   |             | |                               | |
|                                   |             | |         CENTER FOCUS          | |
|       CENTER MASS METRICS         |             | |     (Arquitectura + Text)     | |
|      (Números / Preço / m2)       |             | |                               | |
|                                   |             | |                               | |
| - - - - - - - - - - - - - - - - - |             | |     LOWER THIRD KINETICS      | |
| [UI Right Actions: Like/Share/Sound|             | +-------------------------------+ |
| [UI Bottom Caption & Audio Wave]  |             |      BROADCAST BOTTOM SAFE (8%)   |
+-----------------------------------+             +-----------------------------------+
================================================================================
```

### 1.1 Regras Dimensional e de Ancoragem por Formato

| Parâmetro | Formato Vertical 9:16 (Reels/Shorts) | Formato Horizontal 16:9 (Tours) |
| :--- | :--- | :--- |
| **Resolução Nativa** | 1080x1920 px | 3840x2160 px (4K) / 1920x1080 px |
| **Ponto de Ancoragem Preferencial** | Centro Geométrico (X: 540, Y: 860 a 1150) | Terço Inferior Esquerdo ou Direito (X: 240/1440, Y: 820) |
| **Margem de Respiro Lateral** | Mínimo 120 px em cada bordo X | Mínimo 160 px (8% em 4K) |
| **Margem de Respiro Vertical** | Topo: > 320 px | Fundo: > 420 px | Topo: > 120 px | Fundo: > 140 px |
| **Densidade Máxima por Ecrã** | 1 a 3 palavras simultâneas | 3 a 6 palavras em hierarquia estruturada |
| **Tamanho Relativo da Fonte** | 72 pt a 120 pt (Hero Words: 140 pt+) | 48 pt a 84 pt (Hero Words: 96 pt+) |

---

## 2. GRELHA CRONOMÉTRICA FÍSICA @24 FPS (FRAME-PERFECT TIMINGS)

A agressividade cinética nasce da assimetria temporal: **entrada ultra-rápida, desaceleração magnética com overshoot elástico, e hold imóvel absoluto**.

```text
================================================================================
              CURVA CRONOMÉTRICA DE IMPACTO KINETIC (F0 - F24)
================================================================================
Valor
 120% |          /---\ (F3: Overshoot 112%)
 100% |         /     \------______ (F6: Settle 100%)
  80% |        /                    ---------------- (Hold Rígido F6-F20)
  40% |       /                                     \ (Exit F21-F24)
   0% +------/---------------------------------------\---- Frame
     F0     F1   F2    F3    F4    F5    F6        F20  F24
     [Antic] [SLAM]  [Overshoot]   [Settle]     [HOLD] [Corte/Snap]
================================================================================
```

### 2.1 Tabela de Micro-Ataques e Fases de Frame (@24 FPS)

| Fase de Animação | Duração (Frames) | Descrição do Movimento | Parâmetros de Keyframe / Curvas Bezier |
| :--- | :--- | :--- | :--- |
| **F0 (Pre-Roll / Anticipation)** | 1 a 2 frames | Micro-contração inversa (-5% Scale ou Y+12px) | Ease-In abrupto `cubic-bezier(0.55, 0, 1, 0.45)` |
| **F1–F3 (The Kinetic Slam)** | 2 a 3 frames | Expansão colossal de 0% a 112% Scale / Displacement | Acceleration explosiva `cubic-bezier(0.0, 0, 0.2, 1)` |
| **F3–F6 (Overshoot & Elastic Settle)**| 3 a 4 frames | Recuo elástico de 112% para 98% e estabilização a 100% | Dampened Sine Wave / `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| **F6–F20 (The Rigid Kinetic Hold)** | 14 a 18 frames | Imobilidade total com micro-glitch opcional ao frame 12 | Sem movimento ou drift contínuo imperceptível (+0.5% scale) |
| **F21–F24 (Snap Exit / Collapse)** | 2 a 3 frames | Corte seco (Snap Out) ou colapso vetorial rápido | `cubic-bezier(0.7, 0, 0.84, 0)` ou sem interpolação (Hold) |

### 2.2 Timings Cromáticos e Micro-Interrupções

* **1-Frame Strobe (F1):** Flash de texto a branco puro (`#FFFFFF`) ou tom invertido de contraste máximo exatamente no primeiro frame de entrada.
* **2-Frames Chromatic Bleed (F1–F2):** Deslocamento dos canais RGB (R: +6px, B: -6px) que se fundem de volta ao tom final no frame F3.
* **4-Frames High-G Glow Decay (F1–F4):** Intensidade de brilho/glow arranca nos 100% e decai a 0% ao longo de 4 frames sincronizado com o settle.

---

## 3. SISTEMAS CROMÁTICOS LIVRES DE ALTO IMPACTO

O KA-ENGINE descarta paletas corporativas genéricas e adota 4 matrizes cromáticas de alto contraste, otimizadas para fundos imobiliários variados (interiores iluminados, betão, noites, madeira e vegetação).

```text
================================================================================
                   MATRIZES DE CONTRASTE CROMÁTICO
================================================================================

PALETA 01: VOLT CONCRETE (Agressão Urbana / Edifícios Contemporâneos)
[ Fundo Vídeo ] + [ Caixas: #0D0E10 ] + [ Texto: #FFFFFF ] + [ Accent/Volt: #FFF500 ]

PALETA 02: RAW TERRACOTTA & CYAN (Propriedades de Luxo / Quinta / Terraço)
[ Fundo Vídeo ] + [ Caixas: #0A0A0B ] + [ Texto: #F4F4F6 ] + [ Accent/Cyan: #00FFCC ]

PALETA 03: ACID NEON QUARTZ (Interiores Minimalistas / Cozinhas / LED)
[ Fundo Vídeo ] + [ Caixas: #050508 ] + [ Texto: #FFFFFF ] + [ Accent/Acid: #00FF66 ]

PALETA 04: MONO GOLD & TITANIUM (Arquitectura Premium / Penthouses / VIP)
[ Fundo Vídeo ] + [ Caixas: #0F1012 ] + [ Texto: #E6E8EC ] + [ Accent/Gold: #D4AF37 ]
================================================================================
```

### 3.1 Atribuição Funcional de Cor por Paleta

| Papel no Ecrã | Volt Concrete | Terracotta & Cyan | Acid Neon Quartz | Mono Gold & Titanium |
| :--- | :--- | :--- | :--- | :--- |
| **Texto Base / Neutro** | `#FFFFFF` (Puro) | `#F4F4F6` (Gelo) | `#FFFFFF` (Puro) | `#E6E8EC` (Platina) |
| **Hero Word / Métrica** | `#FFF500` (Volt Yellow) | `#00FFCC` (Electric Cyan) | `#00FF66` (Acid Green) | `#D4AF37` (Metallic Gold) |
| **Alerta / Negativo / Rejeição**| `#FF2A2A` (Crimson) | `#FF5533` (Burnt Orange) | `#FF0055` (Magenta Pulse)| `#FF3333` (Red Alert) |
| **Caixa de Fundo (Plate)** | `#0D0E10` (Opacidade 88%)| `#0A0A0B` (Opacidade 92%)| `#050508` (Opacidade 85%)| `#0F1012` (Opacidade 95%)|
| **Borda Kinetic / Outline** | `#FFF500` (100% Solid) | `#00FFCC` (100% Solid) | `#00FF66` (100% Solid) | `#D4AF37` (100% Solid) |

---

## 4. DESIGN DE SFX & MAPPING FREQUENCIAL AUDIO-VISUAL

Um movimento gráfico agressivo sem sincronismo sonoro preciso perde 70% do seu peso percebido. O som deve conduzir ou colar-se à imagem com precisão de sub-frame.

```text
================================================================================
              CRONOGRAMA DE DUAL-SYNC AUDIO-VISUAL (F-1 a F6)
================================================================================
Frame:   F-1            F0           F1           F2           F3           F6
Áudio:  [Sub-Rumble] -> [Pre-Click] -> [KINETIC SLAM] -> [Tail/Reverb] -> [Silence/Hold]
Vídeo:  [Anticipation]  [1-Fr Flash]   [Overshoot]       [Settle]         [Rigid Hold]
================================================================================
```

### 4.1 Matriz de Mapeamento de SFX para Ações Tipográficas

| Acção Tipográfica | Tipo de Efeito Sonoro (SFX) | Gama de Frequência Dominante | Offset de Áudio Recomendado |
| :--- | :--- | :--- | :--- |
| **Slam de Título / Preço** | Heavy Sub-Impact + Metallic Thud | 40 Hz – 120 Hz (Low End) + 2 kHz Peak | **-1 Frame** (Áudio arranca 1 frame antes da imagem) |
| **Pop de Palavra Individual** | Mechanical Click / Camera Shutter | 1.5 kHz – 4 kHz (Mid-High Punch) | **0 Frames** (Sincronismo exato ao frame) |
| **Deslize Rápido / Whip Slide**| High-Speed Whip Whoosh | 300 Hz → 3 kHz (Pitch Sweep Up) | **-2 Frames** (O som antecipa o movimento) |
| **Revelação de Métrica (Contador)**| Digital Geiger Click / Tape Counter | 2.5 kHz – 6 kHz (High Crisp) | **0 Frames** por cada incremento numérico |
| **Saída em Colapso / Cut-Out** | Low Vacuum Drop / Air Pressure Release| 80 Hz – 250 Hz (Low-Mid Decay) | **+1 Frame** (O som estende-se ligeiramente após o corte) |

---

## 5. REGRAS RIGOROSAS ANTI-PATTERNS (O QUE NÃO FAZER)

1. **PROIBIDO usar "Typewriter Effect" lento:** O efeito de máquina de escrever letra-a-letra em velocidade normal destrói a retenção. Se usado, deve ser um "Fast-Burst" de no máximo 4 frames para a palavra inteira.
2. **PROIBIDO Fade-Ins graduais leves:** Fades de opacidade de 10 a 15 frames tornam o texto mole e passivo. A entrada deve ser imediata (0 a 100% em 1–2 frames com Scale ou Position Slam).
3. **PROIBIDO sobrepor texto a detalhes arquitectónicos críticos:** A legenda nunca deve ocultar focos de luz, torneiras de encastrar de autor, ilhas de cozinha ou vistas de horizonte. Usar a matriz de safe zones.
4. **PROIBIDO mais de 2 famílias tipográficas na mesma sequência:** Usar uma única família tipográfica com variações extremas de peso (ex: *Ultra-Condensed Black* para ganchos e *Medium/Bold* para qualificadores).
5. **PROIBIDO Bounces flácidos e lentos sem damping:** Bounces que demoram 15 frames a estabilizar dão um aspeto amador e "desenho animado". O settle deve durar no máximo 4 frames.
6. **PROIBIDO esquecer o contraste de fundo:** Nunca colocar texto branco direto sobre mármore claro ou céu sem usar caixas tónicas (plates), sombras paralelas de alta densidade ou modos de fusão de alto contraste.

---

## 6. SEQUÊNCIAS PRONTAS A MONTAR (READY HOOK SEQUENCES)

---

### HOOK SEQUENCE 01: O CHOQUE DA MÉTRICA (REELS 9:16)
* **Objectivo:** Capturar a atenção nos primeiros 2 segundos com o valor e a localização da propriedade.
* **Duração Total:** 48 Frames (2.0 segundos @ 24 fps).
* **Paleta:** Volt Concrete (Preto #0D0E10 / Volt Yellow #FFF500 / Branco #FFFFFF).

```text
--------------------------------------------------------------------------------
FRAME-BY-FRAME BREAKDOWN (HOOK 01 - 9:16)
--------------------------------------------------------------------------------
F00-F02: [VÍDEO] Plano de corte rápido (Speed Ramp) da fachada / piscina.
         [TEXTO] F00: Ecrã limpo. 
         [TEXTO] F01: Entrada em 1-Frame Strobe (Branco) da palavra "QUANTO?".
         [SFX]   Pre-impact Whoosh no F00.

F02-F08: [TEXTO] "QUANTO?" faz escala rápida de 180% para 100% com Overshoot (108% em F04).
         [COR]   Caixa preta solida (#0D0E10), Texto em Volt Yellow (#FFF500).
         [SFX]   Sub-Impact pesado em F02.

F09-F18: [TEXTO] "QUANTO?" desaparece por Snap Out (F09).
         [TEXTO] F09: Surge no centro "CUSTA VIVER" em caixa preta com texto Branco.
         [TEXTO] F12: Adiciona linha inferior "NA FOZ?".
         [SFX]   Dois Clicks Mecânicos secos (F09 e F12).

F19-F48: [TEXTO] Transição rápida para a Métrica Mestra:
         Caixa Amarela Volt (#FFF500) com Texto Preto (#0D0E10): "450.000€".
         [EFEITO] Ligeira vibração de opacidade no F19 (1 frame de inversão de cor).
         [HOLD]  Imóvel do F22 ao F44.
         [EXIT]  Snap Out limpo no F48 para o apresentador/plano seguinte.
--------------------------------------------------------------------------------
```

---

### HOOK SEQUENCE 02: A REVELAÇÃO ESPACIAL (REELS 9:16)
* **Objectivo:** Destacar uma característica física única da casa (ex: Pé-direito, Vista, Piscina).
* **Duração Total:** 60 Frames (2.5 segundos @ 24 fps).
* **Paleta:** Acid Neon Quartz (Preto #050508 / Acid Green #00FF66 / Branco #FFFFFF).

```text
--------------------------------------------------------------------------------
FRAME-BY-FRAME BREAKDOWN (HOOK 02 - 9:16)
--------------------------------------------------------------------------------
F00-F03: [VÍDEO] Pan vertical rápido (Tilt Up) de uma sala com pé-direito duplo.
         [TEXTO] Entrada de baixo para cima (Y Push): "PÉ-DIREITO".
         [EFEITO] Deslocamento cromático RGB nos primeiros 2 frames.
         [SFX]   Whip Sweep Rápido.

F04-F16: [TEXTO] "PÉ-DIREITO" fixa no topo (Y: 620).
         [TEXTO] Em F08 surge abaixo em tamanho gigante (140pt): "6 METROS".
         [COR]   "6 METROS" em Acid Green (#00FF66) com outline preto de 4px.
         [SFX]   Heavy Bass Drop no F08.

F17-F36: [TEXTO] Micro-interrupção em F20: A palavra "6 METROS" pisca 1 frame para caixa invertida.
         [HOLD]  Ancoragem perfeita no centro do ecrã enquanto a câmara estabiliza.

F37-F60: [TEXTO] Deslocamento em bloco para a esquerda e entrada da qualificação:
         "LUXO ABSOLUTO".
         [EXIT]  Desvanecimento por Zoom-Out explosivo nos últimos 3 frames (F57-F60).
--------------------------------------------------------------------------------
```

---

### HOOK SEQUENCE 03: O PORTAL ARQUITECTÓNICO (TOURS 16:9)
* **Objectivo:** Introduzir o título de um Tour Cinematográfico em formato horizontal com elegância e peso.
* **Duração Total:** 72 Frames (3.0 segundos @ 24 fps).
* **Paleta:** Mono Gold & Titanium (Platina #E6E8EC / Gold #D4AF37 / Caixa #0F1012).

```text
--------------------------------------------------------------------------------
FRAME-BY-FRAME BREAKDOWN (HOOK 03 - 16:9)
--------------------------------------------------------------------------------
F00-F06: [VÍDEO] Plano de drone lento a aproximar-se de uma Villa de luxo.
         [TEXTO] Linha horizontal superior (2px, D4AF37) expande do centro para os lados em 6 frames.
         [SFX]   Soft Sub-Rumble com Reverb longo.

F07-F24: [TEXTO] Surge abaixo da linha em mascaramento (Crop Reveal de cima para baixo):
         "VILLA MONOLÍTICA" (Tamanho: 84pt, Cor: Platina #E6E8EC).
         [TEXTO] Em F14 surge abaixo em D4AF37 (Gold, Bold CAPS): "CASCAIS".
         [SFX]   Metallic Clang Suave no F07.

F25-F60: [HOLD]  A legenda permanece perfeitamente estática no terço inferior esquerdo (X: 240, Y: 820).
         [EFEITO] Micro-brilho (Glow Pulse) passa pela palavra "CASCAIS" do frame 30 ao 40.

F61-F72: [EXIT]  A linha horizontal contrai de volta ao centro (F61-F68) e o texto faz Wipe para a esquerda (F65-F72).
--------------------------------------------------------------------------------
```

---

### HOOK SEQUENCE 04: TRANSIÇÃO AGRESSIVA DE DIVISÃO (TOURS 16:9)
* **Objectivo:** Marcar a mudança entre áreas principais da casa (ex: da Sala para a Cozinha/Suíte).
* **Duração Total:** 36 Frames (1.5 segundos @ 24 fps).
* **Paleta:** Terracotta & Cyan (Gelo #F4F4F6 / Cyan #00FFCC / Caixa #0A0A0B).

```text
--------------------------------------------------------------------------------
FRAME-BY-FRAME BREAKDOWN (HOOK 04 - 16:9)
--------------------------------------------------------------------------------
F00-F04: [VÍDEO] Corte em transição por movimento de câmara (Whip Pan lateral).
         [TEXTO] Entrada de alta velocidade da direita para a esquerda (+800px para 0px).
         [EFEITO] Skew X de -15 graus durante o movimento para simular força G.
         [SFX]   Air Whip / Swoosh Agressivo.

F05-F10: [TEXTO] Impacto com Overshoot (-20px além da posição final) e travagem abrupta em F08.
         [TEXTO] CONTEÚDO: "SUÍTE PRINCIPAL | 45 M²".
         [COR]   "SUÍTE PRINCIPAL" em Gelo (#F4F4F6), "45 M²" destacado em Cyan (#00FFCC) com caixa preta 92%.
         [SFX]   Mechanical Snap no F08.

F11-F30: [HOLD]  Fixação rígida no canto inferior direito (X: 1280, Y: 880).

F31-F36: [EXIT]  Corte seco (Snap Out no F32) sincronizado com o próximo beat da música.
--------------------------------------------------------------------------------
```

---

## 7. RECEITAS CINÉTICAS CONCRETAS DE MÓDULO ÚNICO

---

### RECEITA KA-01: THE KINETIC IMPACT SLAM
* **Aplicação:** Palavras de ordem, preços, ganchos de abertura em Reels (9:16).
* **Efeito:** A palavra explode da câmara para o ecrã com paragem instantânea e pulso de luz.

```text
================================================================================
PARÂMETROS DA RECEITA KA-01
================================================================================
Fonte Recomendada : Tipografia Extra-Bold / Heavy / Black (Ex: Impact, Syne, Inter)
Escala Inicial    : 220% (Frame 0) -> 100% (Frame 3) -> 105% (Overshoot F5) -> 100% (F8)
Opacidade         : 0% (F0) -> 100% (F1)
Motion Blur       : Ativo (Shutter Angle: 180°)
Sombra Paralela   : Opacidade 80%, Distância 12px, Suavidade 0px (Hard Shadow)
SFX Recomendado   : Heavy Sub Impact + Crisp Click
================================================================================
```

#### Código / Expressão After Effects (Aplicar à Propriedade "Scale"):
```javascript
// Expressão AE: Kinetic Overshoot Slam com Damping
fps = 24;
f = timeToFrames(time);
if (f < 0) f = 0;

sTime = 0; // Frame de arranque
startFrame = 0;
durFrames = 6;

if (f >= startFrame) {
    t = (f - startFrame);
    if (t < 2) {
        // Slam violento
        s = easeOut(t, 0, 2, 220, 100);
    } else if (t < 5) {
        // Overshoot elástico
        s = easeOut(t, 2, 5, 100, 110);
    } else if (t < 8) {
        // Settle final
        s = easeIn(t, 5, 8, 110, 100);
    } else {
        s = 100;
    }
    [s, s];
} else {
    [0, 0];
}
```

#### Setup de Nós DaVinci Resolve / Fusion:
```text
[Text+ (KA01_Text)] ---> [Transform (Kinetics)] ---> [Glow (Flash)] ---> [MediaOut]
  |
  +-- Text+ Props: Font Heavy, Style Bold CAPS, Tracking 1.2
  +-- Transform: Spline Keyframes em Scale (F0: 2.2, F3: 1.0, F5: 1.08, F8: 1.0)
      * Spline Handles: Bezier Tensão 85% no ponto F3
  +-- Glow: Blend Keyframes (F1: 1.0, F4: 0.0)
```

---

### RECEITA KA-02: DYNAMIC BOX ACCORDION
* **Aplicação:** Apresentação de características técnicas (ex: "3 SUÍTES", "GARAGEM DUPLA") com caixas que se ajustam automaticamente ao tamanho do texto.
* **Efeito:** A caixa de fundo expande-se horizontalmente antes das letras serem projetadas para fora.

```text
================================================================================
PARÂMETROS DA RECEITA KA-02
================================================================================
Fonte Recomendada : Sans-Serif Monospaced ou Geometric Heavy (Ex: Space Grotesk)
Caixa de Fundo    : Preenchimento Sólido, Margem Padding X: 40px, Y: 20px
Animação da Caixa : Escala X de 0% para 100% (F0 a F4), Escala Y constante (100%)
Animação do Texto : Entrada em Tracking / Espaçamento (F3 a F8)
SFX Recomendado   : Pneumatic Slide / Mechanical Latch
================================================================================
```

#### Código / Expressão After Effects (Aplicar ao Size do Rectangle Shape Path da Caixa):
```javascript
// Expressão AE: Auto-sizing Box com padding dinâmico
margin = [80, 40]; // Padding [Horizontal, Vertical]
txtVal = targetLayer = thisComp.layer("TEXTO_KA02");
b = txtVal.sourceRectAtTime(time, false);
w = b.width + margin[0];
h = b.height + margin[1];

// Expansão em acordeão nos primeiros 4 frames
f = timeToFrames(time - txtVal.inPoint);
scaleX = linear(f, 0, 4, 0, w);

[scaleX, h];
```

#### Setup de Nós DaVinci Resolve / Fusion:
```text
[Text+ (KA02_Text)] ------------------------+
                                            v
[Background (BoxColor)] ---> [RectangleMask] ---> [Merge] ---> [MediaOut]
  |                             |
  +-- Color: #0D0E10            +-- Width Expression ligado ao Text+ Width
  +-- Opacity: 90%              +-- Keyframe em Level/Width (F0: 0.0, F4: 1.0)
```

---

### RECEITA KA-03: THE VERTICAL TENSION SHUTTER
* **Aplicação:** Destacar métricas verticais em edifícios, tais como "PÉ-DIREITO", "ANDAR ALTO", "PISCINA NO TOPO".
* **Efeito:** Texto cortado por uma máscara de revelação vertical com efeito de persiana de alta velocidade.

```text
================================================================================
PARÂMETROS DA RECEITA KA-03
================================================================================
Animação Y        : Posição Y arranca +120px abaixo da máscara e sobe a 100%
Duração da Revelação: 4 Frames (F0 a F4)
Overshoot Vertical: Passa 10px acima da linha base no F3
Efeito Complementar: Motion Blur de 270° Shutter
SFX Recomendado   : Heavy Shutter Drop / Blade Switch
================================================================================
```

---

### RECEITA KA-04: THE CHROMATIC SPLIT STRIKE
* **Aplicação:** Momentos de revelação de valor, ganchos controversos ou chamadas de atenção instantâneas.
* **Efeito:** Separação violenta dos canais Vermelho/Ciano que chocam no centro para formar o texto limpo.

```text
================================================================================
PARÂMETROS DA RECEITA KA-04
================================================================================
Deslocamento Red  : Position X: -35px (F0) -> 0px (F3)
Deslocamento Cyan : Position X: +35px (F0) -> 0px (F3)
Modo de Fusão     : Screen / Add entre as camadas de cor
Glow Resultante   : Flash de 1 frame de cor branca pura na fusão (F3)
SFX Recomendado   : Electric Spark + Laser Snap
================================================================================
```

---

### RECEITA KA-05: THE SPLIT-COUNTER METRIC (CONTADOR DINÂMICO)
* **Aplicação:** Exibição de valores monetários, áreas em m² ou ano de construção.
* **Efeito:** Os números rolam em alta velocidade (estilo slot machine / odómetro) e travam com um slam metálico no valor final.

```text
================================================================================
PARÂMETROS DA RECEITA KA-05
================================================================================
Duração do Roll   : 12 Frames (F0 a F12)
Valor Inicial     : 0 ou valor aleatório gerado por script
Valor Final       : Exemplo "1.250.000 €" ou "380 M²"
Easing Curve      : Exponential Out `cubic-bezier(0.16, 1, 0.3, 1)`
SFX Recomendado   : High-Speed Mechanical Counter Click Stream + Final Slam
================================================================================
```

#### Código / Expressão After Effects (Aplicar ao "Source Text" de uma camada de texto):
```javascript
// Expressão AE: Contador Dinâmico de Preço com Formatação
startVal = 100000;
endVal = 450000;
startFrame = 0;
durFrames = 14;

f = timeToFrames(time - thisLayer.inPoint);

if (f < startFrame) {
    val = startVal;
} else if (f >= startFrame + durFrames) {
    val = endVal;
} else {
    t = (f - startFrame) / durFrames;
    // Curva Exponential Out para travagem abrupta
    factor = 1 - Math.pow(2, -10 * t);
    val = Math.floor(startVal + (endVal - startVal) * factor);
}

// Formatação com separador de milhares
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

numberWithCommas(val) + " €";
```

---

### RECEITA KA-06: THE WHIP SLIDE DIRECTIONAL
* **Aplicação:** Transição de texto acompanhando movimento pan/orbit da câmara.
* **Efeito:** O texto cruza o ecrã com inclinação geométrica (Skew) adaptada ao sentido do movimento.

```text
================================================================================
PARÂMETROS DA RECEITA KA-06
================================================================================
Deslocamento X    : -1000px (F0) -> +20px (F4 Overshoot) -> 0px (F7)
Skew / Deformação : -18° em F1-F3 (simula inércia/massa) -> 0° em F7
Opacidade         : 100% contínua (sem fade)
SFX Recomendado   : Heavy Whip Whoosh
================================================================================
```

---

### RECEITA KA-07: THE STROBE WARNING CALLOUT
* **Aplicação:** Chamadas de atenção críticas (Ex: "OPORTUNIDADE", "ÚLTIMO LOTE", "VENDIDO").
* **Efeito:** Piscar acelerado em inversão de cores (Preto/Volt Yellow) antes de travar imóvel.

```text
================================================================================
PARÂMETROS DA RECEITA KA-07
================================================================================
Frequência Strobe : F0 (Branco/Preto), F1 (Preto/Amarelo), F2 (Branco/Preto), F3 (Invertido)
Fixação (Hold)    : A partir do Frame F4 (Texto Amarelo / Caixa Preta)
Tamanho do Texto  : Extra Grande (Centro do ecrã, 110pt+)
SFX Recomendado   : Triple Emergency Click / Alarm Pulse
================================================================================
```

---

### RECEITA KA-08: THE MESH PERSPECTIVE ANCHOR (3D TRACKING)
* **Aplicação:** Inserir a legenda "colada" na parede, chão ou relvado da propriedade (Tours 16:9).
* **Efeito:** O texto respeita as linhas de fuga da arquitectura e acompanha a câmara via tracking 3D.

```text
================================================================================
PARÂMETROS DA RECEITA KA-08
================================================================================
Integração 3D     : Rotação X/Y/Z alinhada com o plano da parede/chão
Modo de Fusão     : Overlay ou Soft Light para fundir textura no texto
Opacidade da Caixa: 75% com ligeiro Blur de profundidade (Depth of Field)
Animação de Entrada: Unfold em Z a partir da superfície do plano
SFX Recomendado   : Low Concrete Thud
================================================================================
```

---

## 8. ENGENHARIA DE SCRIPTS & RIGS PROCEDURAIS DE PRODUÇÃO

Para manter a máxima velocidade de produção sem perda de precisão frame-a-frame, utiliza-se rigs procedurais reutilizáveis em After Effects e DaVinci Resolve.

### 8.1 After Effects Procedural Rig (Marker-Driven Engine)
Criar uma camada de texto principal com **Layer Markers** que controlam automaticamente o momento exato do *Slam*, *Overshoot* e *Exit*, sem necessidade de colocar keyframes manuais.

```javascript
// Expressão AE para o parâmetro "Position" ancorado em Markers de Camada
// Marker 1 = Entrada Slam | Marker 2 = Saída Snap Out
m1 = thisLayer.marker.key(1).time;
m2 = thisLayer.marker.key(2).time;

f1 = timeToFrames(time - m1);
f2 = timeToFrames(time - m2);

basePos = value;

if (time < m1) {
    // Posição fora do ecrã (Abaixo +200px)
    [basePos[0], basePos[1] + 200];
} else if (time >= m1 && time < m2) {
    if (f1 < 3) {
        // Slam de entrada
        yOffset = easeOut(f1, 0, 3, 200, -15);
    } else if (f1 < 6) {
        // Overshoot
        yOffset = easeIn(f1, 3, 6, -15, 0);
    } else {
        yOffset = 0;
    }
    [basePos[0], basePos[1] + yOffset];
} else {
    // Snap Out imediato no Marker 2
    [basePos[0], basePos[1] - 800];
}
```

---

### 8.2 DaVinci Resolve / Fusion Macro Structure (KA-Fusion-Template)

```text
================================================================================
ESTRUTURA DE NÓS REUTILIZÁVEL EM DAVINCI RESOLVE FUSION
================================================================================

 [MediaIn1 (Vídeo Base)] ---------------------------------------------------+
                                                                          |
 [TextPlus (KA_Core)] ---> [KeyframeStretcher] ---> [DVE3D (Perspective)] |
                                                           |              |
 [Background (Plate)] ---> [RectangleMask] ----------------+              |
                                                           |              |
                                                     [Merge1 (Over)] <----+
                                                           |
                                                    [Glow (Strobe)]
                                                           |
                                                      [MediaOut1]

* Configuração do KeyframeStretcher:
  - Source Range: [0 a 24] (1 Segundo de referência)
  - Stretch Range: [6 a 18] (Preserva os 6 frames de entrada e 6 frames de saída intactos)
================================================================================
```

---

## 9. CHECKLIST DE VALIDAÇÃO DE QUALIDADE DE PRODUÇÃO (QA)

Antes de exportar a renderização final para entrega ou distribuição, validar os seguintes 6 pontos de controlo crítico:

* [ ] **A regra dos 3-Frames:** O ataque de entrada completa a sua transição principal entre 2 e 4 frames no máximo?
* [ ] **Leitura à velocidade 1.5x:** A Hero Word / Métrica é legível por um espectador a passar rapidamente pelo feed?
* [ ] **Teste de Safe Zone 9:16:** O texto fica completamente livre de botões laterais do Instagram/TikTok e da barra de legenda do rodapé?
* [ ] **Alinhamento de SFX:** O pico do efeito sonoro (transiente) ocorre exatamente no frame de impacto (F1 ou F2)?
* [ ] **Contraste Luminoso:** O rácio de contraste entre o texto/caixa e a imagem de fundo da casa é de pelo menos 7:1?
* [ ] **Ausência de Tremer Flácido:** Todos os movimentos de bounce têm paragem rígida (hold absoluto) sem oscilações infinitas?
