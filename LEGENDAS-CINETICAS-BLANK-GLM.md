# LEGENDAS CINÉTICAS AGRESSIVAS — MOTOR DE PROJÉCTIL (BALLISTIC TYPOGRAPHY @24FPS)

**Playbook de produção para tipografia cinética agressiva em vídeo imobiliário — Reels 9:16 e Tours 16:9.**

---

## 0. O motor balístico

Este manual não legenda o que se ouve. **Dispara palavras contra o olho.**

Cada legenda é tratada como um **projéctil**: tem calibre, velocidade de boca, trajetória, ponto de impacto, penetração (tempo de leitura) e ricochete (saída). A agressividade não vem de "animar rápido" — vem de **transferir energia ao olhar num intervalo curto e mensurável**, deixar o projéctil cravado no ecrã o tempo exacto da leitura, e retirá-lo antes de virar ruído.

O sistema é **balístico** e não tectónico, nem de pressão, nem de partitura:

- Não há "arquitectura" nem "assentamento de materiais". Há **velocidade, trajetória e impacto**.
- Não há níveis de intensidade abstractos. Há **calibres** (peso tipográfico) que determinam energia cinética.
- Não há notação musical. Há **tabelas de tiro** (frame timings exactos) e **alcances** (hold times).

Tudo a **24 fps**. Um frame = **41,67 ms**. Frames escrevem-se `f00`, `f12`, `f120`. Tempos absolutos escrevem-se `t0.500s`.

O motor tem seis fases por projéctil, todas obrigatórias:

```text
1. CARGA      (chamber)   — antecipação invisível, 1–3 f
2. TIRO       (muzzle)    — saída da boca, 2–6 f
3. VOO        (flight)    — trajetória + desaceleração, 3–10 f
4. IMPACTO    (impact)    — cravagem + overshoot, 2–4 f
5. PENETRAÇÃO (hold)      — leitura plena, 12–48 f
6. RICOCHETE  (exit)      — saída com vector, 2–6 f
```

A regra de ouro: **a energia que entra tem de sair**. Um projéctil que entra e fica parado é um bug de produção, não um estilo.

---

## 1. Calibres — peso tipográfico como energia

O **calibre** é a classe de peso do projéctil. Define escala, densidade, sombra, duração mínima de leitura e direito a cor de acento. Não há calibre "certo" — há o calibre certo para o alvo.

| Calibre | Classe | Uso | Escala 9:16 | Escala 16:9 | Sombra | Hold mín. | Acento |
|---|---|---|---:|---:|---|---:|---|
| **.22 LSR** | micro-acento | sílabas, números isolados, "m²", "€" | 64–88 pt | 36–52 pt | nula ou 1px | 8 f | só BONE |
| **9 mm** | acento curto | 1–3 palavras de apoio | 96–128 pt | 56–78 pt | drop 4px 30% | 14 f | ASH |
| **.45 ACP** | claim padrão | frases-claim, benefícios | 140–180 pt | 84–110 pt | drop 8px 45% | 22 f | EMBER |
| **.50 BMG** | hero claim | hero words, preço, hooks | 200–280 pt | 120–160 pt | drop 14px 60% + stroke | 30 f | EMBER + COIN |
| **12 GA** | takeover | invasão full-frame, cortes de plano | 320–480 pt | 180–260 pt | stroke 3px + bloom | 36 f | EMBER sobre INK |
| **20 mm** | ruptura | 1–2 momentos por peça, máscara o imóvel | 520–900 pt | 300–520 pt | bloom + chromatic | 24 f | SIGNAL |

**Regras de calibre:**

- **Máximo 3 calibres por peça.** Misturar mais lê-se como artilharia aleatória.
- **Hierarquia por calibre, não por cor.** Se tudo é `.50 BMG`, nada é hero.
- **Um `.20 mm` por vídeo, no máximo dois**, sempre isolado por `tacet` antes e depois.
- **Calibre nunca se herda do plano anterior.** Cada plano re-avalia o calibre do seu projéctil.

### 1.1 Gamas de corpo por calibre

```text
.22 LSR  →  1 sílaba, 1 número, 1 símbolo         (ex.: "94", "m²", "€")
9 mm     →  2–4 sílabas, 1–3 palavras              (ex.: "PÉ-DIREITO 3,1 m")
.45 ACP  →  3–6 palavras, claim completo           (ex.: "TRES VARANDAS. RIO.")
.50 BMG  →  1–4 palavras, hero                    (ex.: "PARA DE FAZER SCROLL")
12 GA    →  1–6 palavras, takeover                (ex.: "ESTE É O ANDAR")
20 mm    →  1–3 palavras, ruptura                  (ex.: "VEM.")
```

## 2. Safe zones — os dois teatros de operação

A balística muda com o formato. Um projéctil desenhado para 9:16 falha em 16:9 e vice-versa: o ângulo de tiro, a zona de impacto e o respiro são diferentes.

### 2.1 Matriz dual

```text
9:16 REELS / SHORTS / TIKTOK              16:9 TOURS / WALKTHROUGHS
+----------------------------------+    +----------------------------------+
| [UI topo: perfil, badges 8%]    |    |  safe topo 8% (logo player)      |
| - - - - - - - - - - - - - - - - |    | +------------------------------+ |
|                                |    | |  zona de tiro superior 12%   | |
|        ZONA DE TIRO             |    | |  (claims de abertura)        | |
|        (hero, hook)             |    | +------------------------------+ |
|                                |    | |                              | |
|                                |    | |    CENTRO LIMPO (imóvel)     | |
|        CENTRO DE MASSA         |    | |    → nunca ocupar > 30%      | |
|        (métricas, preço)       |    | |                              | |
|                                |    | +------------------------------+ |
| - - - - - - - - - - - - - - - - |    | |  lower-third balístico 18%  | |
| [UI direita: like/share/sound]  |    | |  (claims, preço, CTA)       | |
| [UI fundo: caption + waveform] |    | +------------------------------+ |
+----------------------------------+    |  safe fundo 8% (controls)       |
                                        +----------------------------------+
```

### 2.2 Tabela de ancoragem por formato

| Parâmetro | 9:16 (1080×1920) | 16:9 (1920×1080 / 3840×2160) |
|---|---|---|
| **Ponto de tiro preferencial** | centro geométrico, X=540, Y=760–1240 | lower-third esquerdo, X=240–1680, Y=720–880 |
| **Respiro lateral mínimo** | 110 px cada bordo | 140 px (160 px em 4K) |
| **Respiro vertical mínimo** | topo > 320 px, fundo > 360 px | topo > 96 px, fundo > 110 px |
| **Densidade máxima por plano** | 1–3 palavras simultâneas | 3–6 palavras em hierarquia |
| **Body text (calibre 9 mm)** | 96–128 pt | 56–78 pt |
| **Hero (calibre .50 BMG)** | 200–280 pt | 120–160 pt |
| **Takeover (calibre 12 GA)** | 320–480 pt | 180–260 pt |

### 2.3 Regras de não-colisão com o imóvel

- **Em 16:9 o centro é sagrado.** O imóvel vive no terço superior-central; o texto vive no lower-third. Um claim que cruza o centro tem de ser `.45 ACP` ou maior e durar menos de 24 f.
- **Em 9:16 o centro é o palco.** O imóvel é vertical; o texto compete com ele. Regra: nunca sobrepor texto a uma janela, porta ou vaidade — o olho vai ao branco da abertura, não ao texto.
- **Nunca disparar sobre uma cara humana.** Se há agente/pessoa no plano, o projéctil desloca-se para o terço oposto ou espera o plano seguinte.
- **Safe-zone dinâmica:** se o plano tem movimento de câmara (pan/tilt/orbit), o ponto de ancoragem do projéctil acompanha o vector de câmara, não o ecrã. Texto que fica fixo enquanto a câmara se move é um artefacto de amador.

## 3. Tabelas de tiro — frame timings @24 fps

A balística é mensurável. Cada calibre tem uma **tabela de tiro** fixa: quantos frames para cada fase, com que curva, com que velocidade de boca. Não se inventa o tempo no editing — carrega-se a tabela.

### 3.1 Tabela mestra por calibre (fases em frames)

| Calibre | CARGA | TIRO | VOO | IMPACTO | PENETRAÇÃO | RICOCHETE | TOTAL | Leitura |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| .22 LSR | 1 | 2 | 2 | 1 | 8–14 | 2 | 16–22 | sílaba/número |
| 9 mm | 2 | 3 | 4 | 2 | 14–22 | 3 | 28–36 | 1–3 palavras |
| .45 ACP | 2 | 4 | 6 | 3 | 22–36 | 4 | 41–55 | claim curto |
| .50 BMG | 3 | 5 | 8 | 4 | 30–48 | 5 | 55–65 | hero word |
| 12 GA | 3 | 4 | 6 | 3 | 36–60 | 4 | 56–80 | takeover |
| 20 mm | 2 | 6 | 4 | 4 | 24–36 | 2 | 42–54 | ruptura |

**Leitura:** um `.50 BMG` total dura 55–65 f = **2,29 s a 2,71 s**. Se o plano tem 3 s, há respiro. Se tem 2 s, é curto — baixa para `.45 ACP`.

### 3.2 Velocidades de boca (px/frame @ escala 1080)

A velocidade de boca é a distância percorrida pelo projéctil durante o TIRO, medida em px/frame na comp 1080. Em 4K multiplica-se por 2.

| Calibre | Vel. boca (px/f) | Deslocação típica TIRO | Easing TIRO |
|---|---:|---:|---|
| .22 LSR | 220–280 | 440–560 px | `cubic-bezier(0.0,0.0,0.15,1)` linear-ish |
| 9 mm | 320–420 | 960–1260 px | `cubic-bezier(0.1,0.0,0.2,1)` |
| .45 ACP | 380–520 | 1520–2080 px | `cubic-bezier(0.2,0.0,0.1,1)` |
| .50 BMG | 460–620 | 2300–3100 px | `cubic-bezier(0.3,0.0,0.05,1)` |
| 12 GA | 520–700 | 2080–2800 px (com spread) | `cubic-bezier(0.4,0.0,0.0,1)` |
| 20 mm | 600–900 | 2400–3600 px | `cubic-bezier(0.5,0.0,0.0,1)` snap |

### 3.3 Curvas de easing por fase (expressão universal)

```text
CARGA      →  cubic-bezier(0.55, 0, 1, 0.45)   (pull-back abrupto)
TIRO       →  cubic-bezier(0.0, 0.0, 0.15, 1)  (aceleração quase linear, sem ease-in)
VOO        →  cubic-bezier(0.25, 1, 0.5, 1)    (desaceleração suave)
IMPACTO    →  cubic-bezier(0.34, 1.56, 0.64, 1) (overshoot elástico standard)
PENETRAÇÃO →  linear (hold rígido, zero movimento)
RICOCHETE  →  cubic-bezier(0.36, 0, 0.66, -0.2) (saída com overshoot inverso)
```

A curva de IMPACTO é a única que varia por calibre: calibres pequenos (`.22`, `9 mm`) usam overshoot 1,56; calibres grandes (`.50 BMG`, `12 GA`) baixam para `cubic-bezier(0.34, 1.3, 0.64, 1)` — overshoot de 30% apenas, senão o projéctil "salta" e perde peso.

### 3.4 Envelope de um projéctil .50 BMG (hero hook)

```text
f00–f02  CARGA      scale 100→96, opacity 0→0 (invisível)
f03–f07  TIRO       scale 96→112, opacity 0→100, deslocação 2300 px
f08–f15  VOO        scale 112→100, desaceleração
f16–f19  IMPACTO    scale 100→104→100 (overshoot 4%)
f20–f62  PENETRAÇÃO hold rígido, zero keyframes
f63–f67  RICOCHETE  scale 100→92, opacity 100→0, deslocação -800 px
```

Total: 68 f = **2,83 s**. Para um hook de abertura de 3 s, sobra 4 f de respiro.

## 4. Trajetórias — vetores de tiro

A trajetória é o **vetor** do projéctil no ecrã. Não é decoração — é direcção do olhar. Cada trajetória empurra o olho para um ponto, e o plano seguinte deve receber o olhar nesse ponto.

### 4.1 As oito trajetórias-base

| Código | Vector | Uso | Notas |
|---|---|---|---|
| `↑RISE` | baixo→topo | hooks de abertura, "VEM VER" | o olho sobe, prepara leitura no topo |
| `↓SLAM` | topo→baixo | hero claims, preço, "PARA DE FAZER SCROLL" | o mais agressivo; o olho cai |
| `←WHIP-L` | direita→esquerda | transições para plano à esquerda | corta a leitura anterior |
| `→WHIP-R` | esquerda→direita | transições para plano à direita | arrasta o olho para a frente |
| `↔DECODE` | letras nascem no sítio | métricas, "94 m²", preços | sem vector; impacto por aparição |
| `↻ORBIT` | arco curvo | tours, planos orbit | segue movimento de câmara |
| `⤓DROP` | canto superior→centro | takeovers, "ESTE É O ANDAR" | cai como cortina |
| `✺BLOOM` | centro→fora radial | rupturas `.20 mm`, CTA final | expande e ocupa |

### 4.2 Regra de continuidade de vector

O vector do ricochete de um projéctil deve apontar para o ponto de entrada do projéctil seguinte. Exemplo:

```text
Plano A:  "PARA DE FAZER SCROLL"   ↓SLAM   ricochete → (sai para baixo)
Plano B:  "ESTE É O ANDAR"        ↑RISE   tiro      ↑ (sai de baixo)
```

Isto cria um **loop de vector**: o olho desce no A, sobe no B, desce no C, etc. Quebrar o loop sem motivo é um corte de ritmo. Manter o loop é o que faz o reel "sentir-se" rápido sem cortes bruscos.

### 4.3 Trajetórias proibidas

- **Nunca `↓SLAM` seguido de `↓SLAM`.** Dois impactos no mesmo vector cansam o olho e anulam a agressividade do primeiro.
- **Nunca `↻ORBIT` em reels 9:16.** O arco lê-se como "loading" em ecrã vertical.
- **Nunca `✺BLOOM` em lower-third 16:9.** O bloom invade o imóvel.
- **Nunca `↔DECODE` em calibre `.50 BMG` ou maior.** Letras a nascer não têm energia de impacto; o hero tem de entrar inteiro.

## 5. Sistema de cor — paleta THERMAL-INK

Sistema livre, escolhido para máxima leitura em fundos imobiliários variados (fachada, sala, varanda, aerial). Construído sobre **6 tokens** com função semântica fixa — nunca usar uma cor fora da sua função.

### 5.1 Tokens

| Token | HEX | Função semântica | Uso permitido |
|---|---|---|---|
| **INK** | `#0B0B0D` | tinta-base, fundos de takeover, stroke | texto sobre fundo claro, blocos full-frame, bordas |
| **BONE** | `#EDE7DB` | texto-base sobre fundo escuro/imagem | corpo de legendas em qualquer calibre |
| **ASH** | `#6E6A63` | texto de apoio, métricas secundárias | "m²", "PÉ-DIREITO", sub-labels |
| **EMBER** | `#FF4D1C` | acento de impacto, hero words | `.45 ACP` e maior, uma palavra por plano |
| **COIN** | `#FFB81C` | valor/preço, escassez numérica | preço, "última unidade", "5 dias" |
| **SIGNAL** | `#B6FF3C` | CTA, ruptura, chamada final | `.20 mm` e CTA terminal apenas |

### 5.2 Regras de aplicação

- **Uma cor de acento por plano.** EMBER e COIN nunca coexistem no mesmo projéctil; SIGNAL nunca aparece fora do último plano.
- **BONE sobre INK, INK sobre BONE.** Os dois são intercambiáveis por contraste. ASH é sempre secundário a um dos dois.
- **EMBER exige fundo neutro.** Sobre fundo saturado (madeira quente, tijolo), baixar EMBER para `#E8421A` ou trocar para COIN.
- **COIN nunca sobre amarelo/madeira clara.** Perde leitura. Trocar por EMBER.
- **SIGNAL sobre INK apenas.** Sobre BONE ou imagem, SIGNAL berra e quebra a paleta.

### 5.3 Modos por tipo de plano

| Tipo de plano | Base | Acento | Fundo |
|---|---|---|---|
| Fachada diurna | INK | EMBER | BONE (caixa) |
| Sala com luz quente | INK | COIN | BONE a 90% opacity |
| Varanda/aerial | BONE | EMBER | INK a 85% |
| Interior escuro | BONE | EMBER | sem caixa, stroke 2px INK |
| Tour cinematográfico | BONE | ASH | sem caixa, drop shadow 8px 60% |

### 5.4 Caixa-bloco (backplate) opcional

Para legibilidade em fundos variáveis, usar caixa INK a 78–92% opacity com blur 8px e padding 24px lateral / 16px vertical. A caixa é **sempre rectangular, sem cantos arredondados** — cantos arredondados leem-se como "story template", não como balística.

## 6. After Effects — implementação do motor

### 6.1 Setup de comp

```text
Comp 9:16:  1080×1920, 24 fps, duração do plano + 12f respiro
Comp 16:9:  1920×1080 (ou 3840×2160), 24 fps
Cor:  sRGB, working space OFF (entrega em Rec.709)
Shutter angle: 180°  (motion blur nativo, não plugin)
```

### 6.2 Expressão universal de envelope balístico

Colocar num Slider Control chamado `bal` no layer de texto, animado de 0→1 durante CARGA+TIRO+VOO+IMPACTO, depois manter em 1 durante PENETRAÇÃO, e 1→0 no RICOCHETE. Aplicar esta expressão na `Scale`:

```javascript
// Balistic envelope — Scale
// bal: 0=carga, 1=impacto+penetração, 0=ricochete
// Ajustar CAL (calibre) e VEC (vector) por projéctil

const bal = effect("bal")("Slider");
const CAL = 0.50;          // 0.22, 9, 0.45, 0.50, 12, 20 → factor de overshoot
const ovr = CAL <= 9 ? 1.12 : CAL <= 50 ? 1.08 : 1.04;  // overshoot por calibre

// CARGA (bal 0→0.15): pull-back para 0.96
// TIRO+VOO (bal 0.15→0.85): subida para ovr
// IMPACTO (bal 0.85→1.0): assenta em 1.0
// RICOCHETE: controlado por slider negativo fora do envelope

const carga = linear(bal, 0, 0.15, 96, 100);
const tiro  = linear(bal, 0.15, 0.85, 100, 100 * ovr);
const imp   = linear(bal, 0.85, 1.0, 100 * ovr, 100);

bal < 0.15 ? carga : bal < 0.85 ? tiro : imp;
```

Para o RICOCHETE, animar `bal` de 1→0 numa curva `cubic-bezier(0.36,0,0.66,-0.2)` e aplicar na `Opacity` e `Position` com offset contrário ao vector de entrada.

### 6.3 Posição por vector (expressão)

```javascript
// Posição com vector — usar no Position
// dir: "DOWN","UP","LEFT","RIGHT","DROP","BLOOM","DECODE"
// dist: distância de tiro em px (ver tabela 3.2)
// bal: envelope 0→1

const dir = effect("dir")("Menu").value;
const dist = effect("dist")("Slider");
const bal = effect("bal")("Slider");
const p = [transform.position[0], transform.position[1]];

const off = {
  "DOWN":  [0,  dist],
  "UP":    [0, -dist],
  "LEFT":  [-dist, 0],
  "RIGHT": [dist, 0],
  "DROP":  [dist*0.6, dist*0.8],
  "BLOOM": [0, 0],          // bloom usa Scale, não Position
  "DECODE":[0, 0]
}[dir] || [0,0];

// CARGA: puxa contra o vector (antecipação)
const carga = bal < 0.15 ? -off[0]*0.08, -off[1]*0.08 : 0, 0;
// TIRO: deslocação completa
const tiro  = [off[0]*easeOut(bal), off[1]*easeOut(bal)];

[p[0] - off[0] + tiro[0] + carga[0],
 p[1] - off[1] + tiro[1] + carga[1]];
```

### 6.4 Decode por palavra (per-character)

Para `↔DECODE`, separar em palavras com `Animate > Range Selector`, e na `Offset` usar:

```javascript
// Cada palavra nasce com 3f de offset, 4f de duração
const idx = textIndex - 1;            // palavra 0-based
const start = idx * 3;                // 3f entre palavras
const dur = 4;
const t = timeToFrames(time) - start;
const v = linear(clamp(t, 0, dur), 0, dur, 0, 100);
v;                                    // Offset 0→100
```

Aplicar `Opacity 0→100` e `Position Y +20→0` no mesmo Range Selector.

### 6.5 Bloom para `.20 mm` (ruptura)

```javascript
// Scale bloom — aplicar no Scale
const bal = effect("bal")("Slider");
const peak = linear(bal, 0.2, 0.6, 100, 320);   // expande 3,2x
const settle = linear(bal, 0.6, 1.0, 320, 280); // assenta em 2,8x
bal < 0.6 ? peak : settle;
```

Com `Gaussian Blur` animado de 40→0 em 6f para o efeito de "foco de impacto".

### 6.6 Motion blur e frame rate

- **Shutter 180° sempre.** É o que dá peso ao TIRO.
- **Nunca usar CC Force Motion Blur** — fica plastificado. Usar o nativo.
- Em `.20 mm` e `12 GA`, adicionar `Echo` (1 echo, 2f, decay 0.6) para rasto de projéctil.

## 7. DaVinci Resolve / Fusion — implementação alternativa

Para quem não usa AE, o motor implementa-se em Fusion com a mesma lógica de envelope. Cada projéctil é um `Text+` com um Custom Control a conduzir Scale, Position e Opacity.

### 7.1 Setup de página

```text
Project: 24 fps, Rec.709, Gamma 2.4
Fusion page: cada projéctil = um Text+ + um Background (caixa opcional)
Render: ProRes 422 HQ master, H.264 deliverable
```

### 7.2 Envelope balístico em Fusion (Custom Tool + Spline)

No `Text+`, adicionar um `Custom Control` (node `CustomTool`) com 4 pontos de animação:

```text
Frame 0    bal = 0.00   (carga)
Frame 2    bal = 0.15    (fim carga)
Frame 7    bal = 0.85    (fim tiro)
Frame 11   bal = 1.00    (impacto assentado)
Frame 11–N hold = 1.00  (penetração)
Frame N+5  bal = 0.00   (ricochete)
```

No `Text+ > Transform > Size`, expressão:

```lua
-- Balistic envelope — Size
bal = PointInTime  -- liga ao Custom Control
cal = 0.50         -- calibre
ovr = cal <= 9 and 1.12 or cal <= 50 and 1.08 or 1.04
if bal < 0.15 then
  return 96 + (100-96) * (bal/0.15)
elseif bal < 0.85 then
  return 100 + (100*ovr - 100) * ((bal-0.15)/0.70)
else
  return 100*ovr + (100 - 100*ovr) * ((bal-0.85)/0.15)
end
```

### 7.3 Vector de posição (Fusion)

No `Text+ > Position`, animar com keyframes em vez de expressão (Fusion é mais estável assim):

```text
Frame 0   Position = [centro - offset*0.08]   (carga, antecipação)
Frame 2   Position = [centro - offset*0.08]   (fim carga)
Frame 7   Position = [centro + offset]        (fim tiro, no alvo)
Frame 11  Position = [centro]                (impacto assentado)
Frame N   Position = [centro]                (hold)
Frame N+5 Position = [centro - offset_saida] (ricochete)
```

Curva de spline: botão direito no keyframe → `Bezier` para tiro, `Smooth` para impacto, `Linear` para hold.

### 7.4 Caixa-bloco em Fusion

```text
Background node → INK, alpha 0.85
  → Rectangle mask com Feather 0 (cantos vivos)
  → Padding 24px lateral, 16px vertical
  → Merge por baixo do Text+
```

Para blur na caixa (legibilidade sobre imagem em movimento), adicionar `Defocus` com valor 8 antes do Merge.

### 7.5 Bloom `.20 mm` em Fusion

```text
Text+ (Scale 100→280) → Blur (40→0 em 6f) → Glow (0.4 threshold)
  → Merge over → Bloom (Resolve Color, 0.6)
```

### 7.6 Render

```text
Master:    ProRes 422 HQ, 1080×1920 ou 3840×2160
Deliverable: H.264 CRF 18, +2 sharpen, audio AAC 320
Audio: 48k, -14 LUFS para Reels, -16 LUFS para Tours
```

## 8. SFX — banda sonora balística

Cada projéctil tem um **SFX de família** sincronizado frame-a-frame com as fases. O som é metade da agressividade: um `.50 BMG` mudo é um slide; com o impacto certo é um soco no peito.

### 8.1 Biblioteca por calibre

| Calibre | CARGA | TIRO | IMPACTO | RICOCHETE |
|---|---|---|---|---|
| .22 LSR | — | blip digital | click | tick |
| 9 mm | — | whoosh curto 0,12s | pop de papel | flick |
| .45 ACP | riser 0,08s | whoosh médio 0,18s | thud de couro | whoosh inverso |
| .50 BMG | riser 0,12s + sub-bass | whoosh grave 0,25s | sub-thud + impacto metálico | boom inverso |
| 12 GA | pump 0,15s | whoosh + spray 0,20s | impacto de porta + vidro | ring out 0,4s |
| 20 mm | riser 0,4s + tensão | boom + ar | impacto de concreto | ring + decaimento 0,8s |

### 8.2 Sincronização frame-a-frame

```text
f00  CARGA    → riser/antecipação (ganho 0→-6dB)
f02  TIRO     → whoosh principal (peak -3dB)
f07  VOO      → silêncio (1 frame mudo, "vazio de ar")
f11  IMPACTO  → thud/impacto (peak 0dB, sidechain ao riser)
f12  PENETRA  → sustain de impacto (decaimento -6dB em 6f)
fN   RICOCHETE→ whoosh inverso (ganho 0→-12dB)
```

O **frame muto em f07** (VOO) é a marca do motor: 41,67 ms de silêncio antes do impacto cria a sensação de "projéctil a viajar". Sem esse vazio, o impacto soa a um só evento contínuo e perde peso.

### 8.3 Camada musical

A música não substitui o SFX — coexiste. Regras:

- **SFX no bus de impacto, música no bus de fundo.** Sidechain do bus de música ao bus de SFX: -6dB durante 4f após cada impacto.
- **BPM da música não dita o timing dos projécteis.** As tabelas de tiro (§3) ditam. Se a música tem 92 BPM (≈ 4 f por beat), os projécteis disparam em beats ímpares para não colar com a batida.
- **Riser musical só no último plano.** Antes disso, toda a tensão vem dos SFX balísticos.

### 8.4 Mix final

```text
Bus SFX:    -6 dB peak, sidechain ao bus musical
Bus música:  -18 dB rms, sidechain comprimido -6dB nos impactos
Bus voz (se houver agente): -14 dB, sempre acima de tudo
Master:    -14 LUFS Reels, -16 LUFS Tours, true peak -1 dB
```

## 9. Anti-padrões — o que não é balístico

Lista de erros recorrentes que se parecem agressivos mas não são. Cada um tem a correcção.

### 9.1 "Slide-in suave" (AE default)

**Sintoma:** texto entra com `ease-in-out` de 0,5 s, parece educado, não agressivo.
**Diagnóstico:** está a usar o preset de Keyframe Assistant. Não há CARGA, não há IMPACTO.
**Correcção:** tabela de tiro §3.1. CARGA 2f + TIRO 4f + IMPACTO 3f. Curva TIRO = `cubic-bezier(0.0,0.0,0.15,1)`.

### 9.2 "Tudo em maiúsculas, tudo a bater"

**Sintoma:** cinco planos seguidos com `.50 BMG` em EMBER. O olho satura e nada se lê.
**Diagnóstico:** violação da regra dos 3 calibres (§1). Sem contraste de calibre, não há hero.
**Correcção:** um `.50 BMG` por cada 3–4 planos. Os outros planos usam `9 mm` e `.45 ACP`. O hero é hero porque aparece sozinho.

### 9.3 "Texto que fica"

**Sintoma:** a legenda entra e nunca sai. Fica 4 s parada até ao corte.
**Diagnóstico:** PENETRAÇÃO sem RICOCHETE. A energia que entrou não saiu.
**Correcção:** todo projéctil tem 6 fases (§0). Se o plano dura 4 s e o projéctil precisa de 2,5 s, há 1,5 s de `tacet` — não de texto parado.

### 9.4 "Bounce interminável"

**Sintoma:** o texto entra com overshoot e fica a oscilar 1,2 s.
**Diagnóstico:** curva de IMPACTO com overshoot 1,56 em calibre grande (§3.3).
**Correcção:** calibre `.50 BMG` e maior usam overshoot 1,30, não 1,56. O overshoot é uma marca de impacto, não uma mola de brincar.

### 9.5 "Stroke fino em hero"

**Sintoma:** `.50 BMG` com stroke 1px branco. Lê-se como legenda de TV, não como hero.
**Diagnóstico:** stroke subdimensionado para o calibre.
**Correcção:** stroke por calibre — `.45 ACP` 1,5px, `.50 BMG` 2,5px, `12 GA` 3px, `20 mm` 4px + bloom.

### 9.6 "Cor de acento em tudo"

**Sintoma:** EMBER em 6 palavras de 3 planos seguidos. O acento deixa de ser acento.
**Diagnóstico:** violação de "uma cor de acento por plano" (§5.2).
**Correcção:** EMBER só em hero words e só numa palavra por plano. O resto é BONE.

### 9.7 "Decode em hero"

**Sintoma:** "PARA DE FAZER SCROLL" a aparecer letra-a-letra em 1,2 s.
**Diagnóstico:** trajetória `↔DECODE` em calibre `.50 BMG` (§4.3).
**Correcção:** hero entra inteiro, com `↓SLAM` ou `↑RISE`. Decode é para métricas e preços (`9 mm`).

### 9.8 "Caixa com cantos arredondados"

**Sintoma:** backplate com border-radius 16px. Lê-se como story do Instagram, não como balística.
**Diagnóstico:** template de redes sociais aplicado a tipografia cinética.
**Correcção:** caixa rectangular, cantos vivos, blur 8px (§5.4).

### 9.9 "Motion blur desligado"

**Sintoma:** o TIRO parece uma aparição, sem peso.
**Diagnóstico:** shutter angle a 0° ou motion blur off.
**Correcção:** shutter 180° sempre (§6.1). O motion blur é o rasto do projéctil.

### 9.10 "SFX contínuo"

**Sintoma:** whoosh de 0,8 s a cobrir tiro + impacto. Sem vazio.
**Diagnóstico:** sem o frame muto de f07 (§8.2).
**Correcção:** cortar o whoosh em f07, meter 1f de silêncio, impactar em f08. O vazio é o impacto.

## 10. Hooks prontos — sequências de abertura (3 segundos)

Sequências de tiro completas, prontas a carregar. Cada uma tem calibre, vector, frames, cor e SFX. São **gatilhos de scroll-stop** — o objectivo é o utilizador não passar ao segundo 4.

### 10.1 HOOK-A — "PARA DE FAZER SCROLL" (clássico agressivo)

```text
Plano 1 (0–3s):  fachada, push-in lento
  Projéctil 1 (.50 BMG, ↓SLAM, EMBER)
    "PARA DE FAZER"        f02–f07 tiro, f08–f11 impacto, f12–f50 hold
                          ricochete f51–f55 → sai baixo
  Projéctil 2 (.50 BMG, ↑RISE, EMBER) — encadeia o vector
    "SCROLL"               f52–f57 tiro, f58–f61 impacto, f62–f72 hold
                          ricochete f73–f77 → sai direita
SFX: riser 0,12s @f00 → whoosh grave @f02 → vazio @f07 → sub-thud @f08
     → whoosh inverso @f51 → whoosh @f52 → impacto @f58
Música: entra em f62 (depois do segundo impacto)
```

### 10.2 HOOK-B — "ESTE É O ANDAR" (takeover)

```text
Plano 1 (0–3s):  sala, dolly-in
  Projéctil 1 (12 GA, ⤓DROP, EMBER sobre INK)
    "ESTE É O"             f03–f07 tiro (canto sup. esq. → centro), f08–f11 impacto
                          hold f12–f48, ricochete f49–f52 → sai esquerda
  Projéctil 2 (.45 ACP, →WHIP-R, BONE)
    "ANDAR"                f53–f57 tiro, f58–f61 impacto, f62–f72 hold
SFX: pump 0,15s @f00 → whoosh+spray @f03 → impacto porta @f08
     → whoosh @f53 → thud couro @f58
```

### 10.3 HOOK-C — "94 m²" (decode de métrica)

```text
Plano 1 (0–3s):  sala, orbit lento
  Projéctil 1 (9 mm, ↔DECODE, BONE)
    "94"                  f04–f08 decode (Offset 0→100, 4f)
    "m²"                  f08–f12 decode (3f offset)
                          hold f12–f60, ricochete f61–f64
  Projéctil 2 (.22 LSR, ↑RISE, COIN)
    "PÉ-DIREITO 3,1 m"     f30–f34 tiro, f35–f38 impacto, f39–f60 hold
SFX: click ×2 @f04 → blip @f08 → whoosh curto @f30 → pop papel @f35
```

### 10.4 HOOK-D — "VEM." (ruptura .20 mm)

```text
Plano 1 (0–3s):  porta, câmara parada
  Projéctil 1 (20 mm, ✺BLOOM, SIGNAL sobre INK)
    "VEM."                f05–f11 bloom (Scale 100→320), f12–f15 settle 280
                          hold f16–f48, ricochete f49–f50 (snap, 2f)
  Tacet f51–f72 (respiro absoluto, só imagem)
SFX: riser 0,4s @f00 → boom+ar @f05 → silêncio @f11
     → impacto concreto @f12 → ring decaimento 0,8s @f13
Música: NÃO entra neste hook. O silêncio é o impacto.
```

### 10.5 HOOK-E — "TRES VARANDAS. RIO." (claim duplo)

```text
Plano 1 (0–3s):  varanda, tilt-up
  Projéctil 1 (.45 ACP, ↑RISE, BONE)
    "TRES VARANDAS."       f03–f07 tiro, f08–f11 impacto, f12–f40 hold
                          ricochete f41–f44 → sai cima
  Projéctil 2 (.45 ACP, ↓SLAM, EMBER) — vector oposto, contraponto
    "RIO."                f45–f49 tiro, f50–f53 impacto, f54–f72 hold
SFX: whoosh médio @f03 → thud couro @f08 → whoosh inverso @f41
     → whoosh grave @f45 → sub-thud @f50
```

### 10.6 Mapa de escolha rápida de hook

| Tipo de imóvel | Hook recomendado | Razão |
|---|---|---|
| Apartamento standard, captação rápida | HOOK-A | scroll-stop universal |
| Andar/cobertura, hero | HOOK-B | takeover, escala |
| T2/T3 com métrica forte | HOOK-C | decode, leitura de número |
| Lançamento/exclusividade | HOOK-D | ruptura, escassez |
| Vista premium (rio/mar) | HOOK-E | claim duplo, contraponto |

## 11. Receitas concretas — peças completas

### 11.1 REEL 9:16 — "Apartamento Rio" (34 s)

Peça completa, 6 planos, calibres `.50 BMG` + `.45 ACP` + `9 mm`, paleta THERMAL-INK.

```text
PEÇA: reel-apartamento-rio | 9:16 | 24fps | 34s | música 92 BPM

[P01 | f000–f072 | 3,0s | fachada, push-in]
  .50 BMG ↓SLAM EMBER  "PARA DE FAZER SCROLL"
    carga f00–f02, tiro f02–f07, impacto f08–f11, hold f12–f50, ricochete f51–f55 ↓
  SFX: riser 0,12s + whoosh grave + vazio f07 + sub-thud f08

[P02 | f072–f144 | 3,0s | hall, pan direita]
  tacet  (respiro: só imagem, som ambiente)

[P03 | f144–f240 | 4,0s | sala, orbit lento]
  9 mm ↔DECODE BONE  "94 m²"
    decode f146–f154, hold f155–f210, ricochete f211–f214
  .22 LSR ↑RISE COIN  "PÉ-DIREITO 3,1 m"  @f180
    tiro f180–f184, impacto f185–f188, hold f189–f210, ricochete f211–f214
  SFX: click ×2 + blip + whoosh curto + pop papel

[P04 | f240–f336 | 4,0s | varanda, tilt-up]
  .45 ACP ↑RISE BONE  "TRES VARANDAS."
    tiro f242–f247, impacto f248–f251, hold f252–f300, ricochete f301–f304 ↑
  .45 ACP ↓SLAM EMBER  "RIO."  @f305
    tiro f305–f309, impacto f310–f313, hold f314–f336
  SFX: whoosh médio + thud couro + whoosh grave + sub-thud

[P05 | f336–f576 | 10,0s | cozinha + quarto, cortes rápidos]
  9 mm →WHIP-R BONE  "COZINHA 18 m²"  @f340 (4 planos, 1 projéctil cada)
  9 mm ←WHIP-L BONE  "SUÍTE 22 m²"   @f420
  9 mm ↓SLAM BONE   "WC COMPLETO"   @f500
  SFX: whoosh curto ×3 + pop ×3, sincronizados com whip

[P06 | f576–f816 | 10,0s | porta, câmara parada → aerial]
  12 GA ⤓DROP EMBER/INK  "ESTE É O ANDAR"
    tiro f578–f583, impacto f584–f587, hold f588–f720, ricochete f721–f724 ←
  .45 ACP ↓SLAM SIGNAL  "VEM VER."  @f730
    tiro f730–f734, impacto f735–f738, hold f739–f800, ricochete f801–f805
  SFX: pump + whoosh spray + impacto porta + ring out
       + riser musical f720 + boom final f735
MÚSICA: entra f588 (depois do takeover), sai f800
```

### 11.2 TOUR 16:9 — "Tour Cobertura" (45 s)

Peça completa, 5 planos, calibres `.45 ACP` + `9 mm` + `12 GA`, paleta THERMAL-INK, lower-third.

```text
PEÇA: tour-cobertura | 16:9 | 24fps | 45s | música 84 BPM, cinematográfica

[P01 | f000–f240 | 10,0s | aerial diurno, aproximação]
  .45 ACP ↔DECODE BONE  "COBERTURA 280 m²"  (lower-third esq.)
    decode f10–f30, hold f31–f200, ricochete f201–f210 →
  .22 LSR ↑RISE COIN  "TERRAÇO 90 m²"  @f120
    tiro f120–f124, impacto f125–f128, hold f129–f200, ricochete f201–f204
  SFX: whoosh curto + click + blip (sem sub-thud, tour é mais contido)

[P02 | f240–f480 | 10,0s | sala, dolly-in lento]
  tacet  (respiro: só imagem, música)
  9 mm ↔DECODE BONE  "PÉ-DIREITO 4,2 m"  @f360
    decode f360–f372, hold f373–f460, ricochete f461–f464
  SFX: click ×2 + blip

[P03 | f480–f720 | 10,0s | varanda/rio, orbit]
  .45 ACP ↑RISE EMBER  "VISTA PERMANENTE"  (lower-third esq.)
    tiro f482–f487, impacto f488–f491, hold f492–f680, ricochete f681–f684 ↑
  SFX: whoosh médio + thud couro

[P04 | f720–f960 | 10,0s | cozinha + suites, cortes médios]
  9 mm →WHIP-R BONE  "COZINHA 32 m²"  @f740
  9 mm ←WHIP-L BONE  "SUÍTE MASTER 38 m²"  @f820
  9 mm →WHIP-R BONE  "WC PRIVATIVO"  @f900
  SFX: whoosh curto ×3 + pop ×3

[P05 | f960–f1080 | 5,0s | porta, câmara parada → fade]
  12 GA ⤓DROP EMBER/INK  "ESTE É O ANDAR"  (centro-inferior)
    tiro f962–f967, impacto f968–f971, hold f972–f1040, ricochete f1041–f1044 ←
  .45 ACP ↓SLAM SIGNAL  "VEM VER."  @f1050
    tiro f1050–f1054, impacto f1055–f1058, hold f1059–f1075, ricochete f1076–f1080
  SFX: pump + whoosh spray + impacto porta + ring out + boom final
MÚSICA: entra f000, cresce em f480, peak em f960, sai em f1075
```

## 12. Checklist de produção — antes de exportar

Lista de verificação rápida, por projéctil e por peça. Se falha um item, não exporta.

### 12.1 Por projéctil

- [ ] Calibre definido e dentro da regra dos 3 calibres por peça
- [ ] 6 fases presentes: CARGA, TIRO, VOO, IMPACTO, PENETRAÇÃO, RICOCHETE
- [ ] Hold ≥ mínimo do calibre (tabela §3.1)
- [ ] Vector de ricochete aponta para a entrada do projéctil seguinte
- [ ] Cor de acento usada uma vez por plano, na função semântica certa
- [ ] Caixa (se usada) rectangular, sem cantos arredondados, blur 8px
- [ ] Não sobrepõe janela, porta, vaidade ou cara humana
- [ ] Dentro de safe-zone (lateral e vertical, tabela §2.2)

### 12.2 Por peça

- [ ] Máximo 3 calibres usados
- [ ] Máximo 1–2 projécteis `.20 mm` (ruptura)
- [ ] Pelo menos 1 `tacet` por cada 4 planos com texto
- [ ] Loop de vector mantido entre planos (§4.2)
- [ ] Shutter 180° em todos os layers com TIRO
- [ ] Frame muto em f07 do VOO (SFX)
- [ ] Bus SFX com sidechain ao bus musical
- [ ] LUFS: -14 Reels / -16 Tours, true peak -1 dB
- [ ] Master ProRes 422 HQ, deliverable H.264 CRF 18

---

## 13. Glossário balístico

| Termo | Definição |
|---|---|
| **Calibre** | classe de peso tipográfico do projéctil; define energia e hold mínimo |
| **CARGA** | fase 1, antecipação invisível (1–3f), pull-back oposto ao vector |
| **TIRO** | fase 2, saída da boca, deslocação principal, com motion blur |
| **VOO** | fase 3, desaceleração + frame muto de SFX (§8.2) |
| **IMPACTO** | fase 4, cravagem no alvo + overshoot (1,30–1,56 por calibre) |
| **PENETRAÇÃO** | fase 5, hold rígido, leitura plena, zero keyframes |
| **RICOCHETE** | fase 6, saída com vector, overshoot inverso |
| **Vector** | direcção de tiro (↓SLAM, ↑RISE, →WHIP-R, etc., §4.1) |
| **Loop de vector** | continuidade de direcção entre projécteis consecutivos (§4.2) |
| **Tacet** | plano deliberadamente sem texto; respiro composicional |
| **Takeover** | projéctil `12 GA` que invade o ecrã, corta o plano |
| **Ruptura** | projéctil `.20 mm`, máximo 1–2 por peça, máscara o imóvel |
| **Tabela de tiro** | timings exactos por calibre (§3.1) |
| **Velocidade de boca** | px/frame durante o TIRO (§3.2) |
| **Token de cor** | função semântica fixa na paleta THERMAL-INK (§5.1) |
| **Frame muto** | 1f de silêncio em f07 do VOO, marca do motor |

---

*Fim do playbook. O motor balístico é livre: calibres, trajetórias e paleta podem ser ajustados à peça — mas as seis fases, o loop de vector e o frame muto não se negociam. São o que faz a agressividade ser cinética e não caótica.*

